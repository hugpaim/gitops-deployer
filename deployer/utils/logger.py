# deployer/utils/logger.py
import logging
import os
import time
from pathlib import Path


class RunLogger:
    def __init__(self, project: str, run_id: int):
        log_dir = Path("logs") / project
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"run_{run_id}_{ts}.log"

        self._logger = logging.getLogger(f"run.{run_id}")
        self._logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s  %(message)s"))
        self._logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        self._logger.addHandler(ch)

        self.log_file = str(log_file)

    def info(self, msg: str):
        self._logger.info(msg)

    def error(self, msg: str):
        self._logger.error(msg)
