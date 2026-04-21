"""Qt worker threads for non-blocking job monitoring."""

from PySide6.QtCore import QObject, QTimer, Signal
from pathlib import Path

from kpdf.operations.batch_processor import BatchProcessor, Job, JobStatus


class JobMonitor(QObject):
    """Emits signals when job status changes, using a QTimer to poll."""

    job_started = Signal(str, str)
    job_completed = Signal(str, str, str)
    job_failed = Signal(str, str, str)
    job_cancelled = Signal(str, str)

    POLL_INTERVAL_MS = 150

    def __init__(self, batch_processor: BatchProcessor) -> None:
        super().__init__()
        self.processor = batch_processor
        self.monitoring_job_ids: set[str] = set()
        self._emitted_started: set[str] = set()

        self._timer = QTimer(self)
        self._timer.setInterval(self.POLL_INTERVAL_MS)
        self._timer.timeout.connect(self._poll_all)

    def watch_job(self, job_id: str) -> None:
        """Start monitoring a job and emit signals on status changes."""
        self.monitoring_job_ids.add(job_id)
        if not self._timer.isActive():
            self._timer.start()

    def _poll_all(self) -> None:
        """Poll all monitored jobs; stop timer when none remain."""
        done = set()
        for job_id in list(self.monitoring_job_ids):
            if self._check_job_status(job_id):
                done.add(job_id)
        self.monitoring_job_ids -= done
        if not self.monitoring_job_ids:
            self._timer.stop()

    def _check_job_status(self, job_id: str) -> bool:
        """Poll one job. Returns True when the job has finished (any terminal state)."""
        job = self.processor.get_job(job_id)
        if not job or not job.future:
            return True

        if job.status == JobStatus.RUNNING and job_id not in self._emitted_started:
            self._emitted_started.add(job_id)
            self.job_started.emit(job_id, job.name)

        if not job.future.done():
            return False

        self._emitted_started.discard(job_id)
        if job.status == JobStatus.COMPLETED and job.result:
            output_str = str(job.result.output_path) if job.result.output_path else ""
            self.job_completed.emit(job_id, job.name, output_str)
        elif job.status == JobStatus.FAILED and job.result:
            self.job_failed.emit(job_id, job.name, job.result.error_message or "Unknown error")
        elif job.status == JobStatus.CANCELLED:
            self.job_cancelled.emit(job_id, job.name)
        return True
