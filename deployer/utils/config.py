# deployer/utils/config.py
import os
import re
import yaml
from pathlib import Path
from dotenv import load_dotenv


def load_config(path: str = "configs/pipeline.yaml") -> dict:
    load_dotenv()
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(p) as f:
        raw = yaml.safe_load(f)
    return _expand_env(raw)


def _expand_env(obj):
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(i) for i in obj]
    if isinstance(obj, str):
        return os.path.expandvars(obj)
    return obj
