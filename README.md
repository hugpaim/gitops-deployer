# 🚀 gitops-deployer

> Lightweight GitOps pipeline — receive a GitHub webhook on push, run configurable pipeline steps, and notify your team via Slack or Discord.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/Webhook-GitHub-181717?style=flat-square&logo=github&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![CI](https://github.com/hugpaim/gitops-deployer/actions/workflows/ci.yaml/badge.svg)

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────┐
│              GitHub — push event                    │
│         POST /webhook  (HMAC-SHA256 signed)         │
└──────────────────────┬──────────────────────────────┘
                       │
         ┌─────────────▼─────────────┐
         │      Flask Webhook        │
         │   signature validation    │
         │   concurrency lock        │
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │      PipelineRunner       │
         │   reads pipeline.yaml     │
         │   topo-sorted steps       │
         └──────┬──────────┬─────────┘
                │          │
   ┌────────────▼──┐  ┌────▼──────────────────┐
   │  Step         │  │    DeployHistory      │
   │  Executors    │  │      (SQLite)         │
   │  shell        │  └───────────────────────┘
   │  docker_build │
   │  docker_push  │  ┌────────────────────────┐
   │  ssh_deploy   │  │     Notifier           │
   └───────────────┘  │  Slack │ Discord       │
                      └────────────────────────┘
```

## 📁 Project Structure

```
gitops-deployer/
├── deployer/
│   ├── webhook/
│   │   ├── server.py         # Flask webhook receiver
│   │   └── signature.py      # HMAC-SHA256 validation
│   ├── pipeline/
│   │   ├── runner.py         # Orchestrate pipeline steps
│   │   ├── steps.py          # shell / docker / ssh executors
│   │   └── history.py        # SQLite deploy history
│   └── utils/
│       ├── config.py         # YAML config loader
│       ├── logger.py         # Per-run log files
│       └── notify.py         # Slack / Discord notifications
├── configs/
│   └── pipeline.example.yaml
├── tests/
│   ├── test_signature.py
│   └── test_pipeline.py
├── conftest.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/hugpaim/gitops-deployer.git
cd gitops-deployer

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Configure your pipeline
cp configs/pipeline.example.yaml configs/pipeline.yaml
# Edit pipeline.yaml with your steps

# 5. Set webhook secret
echo "WEBHOOK_SECRET=your-secret-here" > .env

# 6. Start the server
python -m deployer.webhook.server --port 8080
```

## ⚙️ Pipeline Configuration

```yaml
# configs/pipeline.yaml
project: my-app
repo: your-org/your-repo

branches:
  main:
    steps:
      - name: Run tests
        type: shell
        run: "cd /opt/app && pytest tests/ -q"

      - name: Build image
        type: docker_build
        context: /opt/app
        tag: "myrepo/my-app:latest"

      - name: Push image
        type: docker_push
        tag: "myrepo/my-app:latest"

      - name: Deploy via SSH
        type: ssh_deploy
        host: ${DEPLOY_HOST}
        user: ${DEPLOY_USER}
        key_file: ~/.ssh/deploy_key
        commands:
          - docker pull myrepo/my-app:latest
          - docker stop my-app || true
          - docker run -d --name my-app -p 80:8000 myrego/my-app:latest

notifications:
  slack_webhook: ${SLACK_WEBHOOK_URL}
```

## 🔄 Pipeline Step Types

| Type | Description |
|------|-------------|
| `shell` | Run any shell command on the host |
| `docker_build` | Build a Docker image |
| `docker_push` | Push image to a registry |
| `ssh_deploy` | Run commands on a remote host via SSH |

## 🔒 GitHub Webhook Setup

1. Go to repo → **Settings → Webhooks → Add webhook**
2. Payload URL: `https://your-server:8080/webhook`
3. Content type: `application/json`
4. Secret: same value as `WEBHOOK_SECRET` in `.env`
5. Events: **Just the push event**

## 🧪 Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

```
tests/test_signature.py::test_valid_signature    PASSED
tests/test_signature.py::test_invalid_signature  PASSED
tests/test_signature.py::test_missing_signature  PASSED
tests/test_signature.py::test_wrong_prefix       PASSED
tests/test_pipeline.py::test_shell_step_success  PASSED
tests/test_pipeline.py::test_shell_step_failure  PASSED
tests/test_pipeline.py::test_unknown_step_type   PASSED
tests/test_pipeline.py::test_secret_masking      PASSED

8 passed
```

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Webhook server | Flask |
| Signature validation | HMAC-SHA256 |
| SSH deploys | Paramiko |
| Config | YAML + dotenv |
| Deploy history | SQLite |
| Notifications | Slack / Discord webhooks |

---

> Part of [@hugpaim](https://github.com/hugpaim) DevOps portfolio

