# deployer/pipeline/steps.py
import os
import subprocess
from dataclasses import dataclass
from typing import Callable


@dataclass
class StepResult:
    name: str
    success: bool
    output: str = ""
    error: str = ""


def _mask_secrets(text: str) -> str:
    """Replace common secret patterns in output."""
    import re
    return re.sub(r"(password|token|secret|key)\s*=\s*\S+", r"\1=***", text, flags=re.IGNORECASE)


def run_shell(step: dict, log: Callable[[str], None]) -> StepResult:
    cmd = step["run"]
    log(f"$ {cmd}")
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=600
        )
        output = _mask_secrets(proc.stdout + proc.stderr)
        log(output)
        if proc.returncode != 0:
            return StepResult(step["name"], False, output, f"exit code {proc.returncode}")
        return StepResult(step["name"], True, output)
    except subprocess.TimeoutExpired:
        return StepResult(step["name"], False, "", "command timed out after 600s")
    except Exception as e:
        return StepResult(step["name"], False, "", str(e))


def run_docker_build(step: dict, log: Callable[[str], None]) -> StepResult:
    context = step.get("context", ".")
    tag = step["tag"]
    dockerfile = step.get("dockerfile", "Dockerfile")
    cmd = f"docker build -f {dockerfile} -t {tag} {context}"
    return run_shell({"name": step["name"], "run": cmd}, log)


def run_docker_push(step: dict, log: Callable[[str], None]) -> StepResult:
    tag = step["tag"]
    return run_shell({"name": step["name"], "run": f"docker push {tag}"}, log)


def run_ssh_deploy(step: dict, log: Callable[[str], None]) -> StepResult:
    try:
        import paramiko
    except ImportError:
        return StepResult(step["name"], False, "", "paramiko not installed")

    host = os.path.expandvars(step["host"])
    user = os.path.expandvars(step.get("user", "root"))
    key_file = os.path.expandvars(os.path.expanduser(step.get("key_file", "~/.ssh/id_rsa")))
    commands = step.get("commands", [])

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, key_filename=key_file, timeout=30)
        all_output = []
        for cmd in commands:
            log(f"[ssh {host}] $ {cmd}")
            _, stdout, stderr = ssh.exec_command(cmd, timeout=120)
            out = stdout.read().decode() + stderr.read().decode()
            log(_mask_secrets(out))
            all_output.append(out)
        ssh.close()
        return StepResult(step["name"], True, "\n".join(all_output))
    except Exception as e:
        return StepResult(step["name"], False, "", str(e))


STEP_HANDLERS = {
    "shell":        run_shell,
    "docker_build": run_docker_build,
    "docker_push":  run_docker_push,
    "ssh_deploy":   run_ssh_deploy,
}


def execute_step(step: dict, log: Callable[[str], None]) -> StepResult:
    step_type = step.get("type", "shell")
    handler = STEP_HANDLERS.get(step_type)
    if not handler:
        return StepResult(step["name"], False, "", f"unknown step type: {step_type}")
    return handler(step, log)
