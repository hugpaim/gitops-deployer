# deployer/webhook/server.py
import os
import threading
import click
from flask import Flask, request, jsonify
from deployer.webhook.signature import verify_signature
from deployer.utils.config import load_config
from deployer.pipeline.runner import PipelineRunner

app = Flask(__name__)
_lock = threading.Lock()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/webhook", methods=["POST"])
def webhook():
    cfg = app.config["PIPELINE_CONFIG"]
    secret = os.environ.get("WEBHOOK_SECRET", "")

    # Validate signature
    sig = request.headers.get("X-Hub-Signature-256", "")
    if secret and not verify_signature(request.data, secret, sig):
        return jsonify({"error": "invalid signature"}), 401

    event = request.headers.get("X-GitHub-Event", "")
    if event != "push":
        return jsonify({"message": f"ignoring event: {event}"}), 200

    payload = request.get_json(force=True)
    ref = payload.get("ref", "")
    branch = ref.replace("refs/heads/", "")
    repo = payload.get("repository", {}).get("full_name", "")
    pusher = payload.get("pusher", {}).get("name", "unknown")
    commit = payload.get("after", "")[:8]

    # Check repo matches config
    if cfg.get("repo") and repo != cfg["repo"]:
        return jsonify({"message": "repo mismatch, ignoring"}), 200

    branch_cfg = cfg.get("branches", {}).get(branch)
    if not branch_cfg:
        return jsonify({"message": f"no pipeline for branch '{branch}'"}), 200

    # Prevent concurrent deploys
    if not _lock.acquire(blocking=False):
        return jsonify({"error": "deploy already in progress"}), 429

    def run():
        try:
            runner = PipelineRunner(cfg, branch, branch_cfg["steps"])
            runner.run(meta={"pusher": pusher, "commit": commit, "repo": repo})
        finally:
            _lock.release()

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"message": f"pipeline started for {branch}@{commit}"}), 202


@click.command()
@click.option("--port", default=8080, show_default=True)
@click.option("--config", default="configs/pipeline.yaml", show_default=True)
def main(port, config):
    """Start the gitops-deployer webhook server."""
    cfg = load_config(config)
    app.config["PIPELINE_CONFIG"] = cfg
    print(f"[gitops-deployer] listening on :{port}")
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
