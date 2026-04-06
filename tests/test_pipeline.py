# tests/test_pipeline.py
from deployer.pipeline.steps import execute_step, run_shell


def test_shell_step_success():
    step = {"name": "echo test", "type": "shell", "run": "echo hello"}
    result = execute_step(step, lambda x: None)
    assert result.success is True
    assert "hello" in result.output


def test_shell_step_failure():
    step = {"name": "fail", "type": "shell", "run": "exit 1"}
    result = execute_step(step, lambda x: None)
    assert result.success is False
    assert "exit code" in result.error


def test_unknown_step_type():
    step = {"name": "bad", "type": "nonexistent"}
    result = execute_step(step, lambda x: None)
    assert result.success is False
    assert "unknown step type" in result.error


def test_secret_masking():
    from deployer.pipeline.steps import _mask_secrets
    text = "connecting with password=supersecret123"
    masked = _mask_secrets(text)
    assert "supersecret123" not in masked
    assert "***" in masked
