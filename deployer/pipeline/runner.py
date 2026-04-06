# deployer/pipeline/runner.py
import time
from deployer.pipeline.steps import execute_step
from deployer.pipeline.history import DeployHistory
from deployer.utils.logger import RunLogger
from deployer.utils.notify import Notifier


class PipelineRunner:
    def __init__(self, config: dict, branch: str, steps: list[dict]):
        self.config = config
        self.branch = branch
        self.steps = steps
        self.project = config.get("project", "unknown")
        self.history = DeployHistory()
        self.notifier = Notifier(config.get("notifications", {}))

    def run(self, meta: dict):
        run_id = self.history.start(
            project=self.project,
            branch=self.branch,
            commit=meta.get("commit", ""),
            pusher=meta.get("pusher", ""),
        )
        logger = RunLogger(self.project, run_id)
        logger.info(
            f"Pipeline started | branch={self.branch} "
            f"commit={meta.get('commit')} pusher={meta.get('pusher')}"
        )
        self.notifier.send_start(self.project, self.branch, meta)

        start = time.time()
        failed_step = None

        for step in self.steps:
            logger.info(f"--- Step: {step['name']} ({step.get('type','shell')}) ---")
            result = execute_step(step, logger.info)
            if not result.success:
                failed_step = result
                logger.error(f"Step FAILED: {result.name} — {result.error}")
                break
            logger.info(f"Step OK: {result.name}")

        elapsed = round(time.time() - start, 1)
        success = failed_step is None

        self.history.finish(run_id, success=success,
                            error=failed_step.error if failed_step else None)
        logger.info(f"Pipeline {'SUCCEEDED' if success else 'FAILED'} in {elapsed}s")

        if success:
            self.notifier.send_success(self.project, self.branch, meta, elapsed)
        else:
            self.notifier.send_failure(self.project, self.branch, meta,
                                       failed_step.name, failed_step.error)
