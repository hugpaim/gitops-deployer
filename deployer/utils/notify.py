# deployer/utils/notify.py
import os
import requests


class Notifier:
    def __init__(self, config: dict):
        self.slack_url = os.path.expandvars(config.get("slack_webhook", ""))
        self.discord_url = os.path.expandvars(config.get("discord_webhook", ""))

    def _post(self, url: str, text: str):
        if not url or url.startswith("$"):
            return
        try:
            requests.post(url, json={"text": text, "content": text}, timeout=5)
        except requests.RequestException:
            pass

    def send_start(self, project: str, branch: str, meta: dict):
        msg = (f"🚀 *Deploy started* | `{project}` "
               f"branch=`{branch}` commit=`{meta.get('commit')}` "
               f"by {meta.get('pusher')}")
        self._post(self.slack_url, msg)
        self._post(self.discord_url, msg)

    def send_success(self, project: str, branch: str, meta: dict, elapsed: float):
        msg = (f"✅ *Deploy succeeded* | `{project}` "
               f"branch=`{branch}` commit=`{meta.get('commit')}` "
               f"in {elapsed}s")
        self._post(self.slack_url, msg)
        self._post(self.discord_url, msg)

    def send_failure(self, project: str, branch: str, meta: dict,
                     step: str, error: str):
        msg = (f"❌ *Deploy FAILED* | `{project}` "
               f"branch=`{branch}` commit=`{meta.get('commit')}` "
               f"— step `{step}`: {error}")
        self._post(self.slack_url, msg)
        self._post(self.discord_url, msg)
