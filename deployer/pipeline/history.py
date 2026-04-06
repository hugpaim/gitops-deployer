# deployer/pipeline/history.py
import sqlite3
import time


class DeployHistory:
    def __init__(self, db_path: str = "deploy_history.db"):
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS deploys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT,
                    branch TEXT,
                    commit TEXT,
                    pusher TEXT,
                    started_at REAL,
                    finished_at REAL,
                    success INTEGER,
                    error TEXT
                )
            """)

    def start(self, project: str, branch: str, commit: str, pusher: str) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO deploys (project, branch, commit, pusher, started_at) VALUES (?,?,?,?,?)",
                (project, branch, commit, pusher, time.time()),
            )
            return cur.lastrowid

    def finish(self, run_id: int, success: bool, error: str | None = None):
        with self._conn() as c:
            c.execute(
                "UPDATE deploys SET finished_at=?, success=?, error=? WHERE id=?",
                (time.time(), int(success), error, run_id),
            )

    def recent(self, project: str, limit: int = 20) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT * FROM deploys WHERE project=? ORDER BY started_at DESC LIMIT ?",
                (project, limit),
            ).fetchall()
        cols = ["id", "project", "branch", "commit", "pusher",
                "started_at", "finished_at", "success", "error"]
        return [dict(zip(cols, r)) for r in rows]
