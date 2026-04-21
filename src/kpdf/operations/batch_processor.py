"""Batch job execution engine with threading and progress tracking."""

import logging
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

from kpdf.utils.error_handler import OperationError


class JobStatus(Enum):
    """Job execution state."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class JobResult:
    """Outcome of a completed job."""

    job_id: str
    status: JobStatus
    output_path: Path | None = None
    error_message: str | None = None


@dataclass(slots=True)
class Job:
    """A batch job with execution metadata."""

    job_id: str
    name: str
    operation_fn: Callable[[], Path]
    status: JobStatus = field(default=JobStatus.PENDING)
    result: JobResult | None = field(default=None)
    future: Future[Path] | None = field(default=None)


class BatchProcessor:
    """Execute PDF operations in background with bounded concurrency."""

    def __init__(self, max_workers: int = 4) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: dict[str, Job] = {}
        self.logger = logging.getLogger("kPDF.Batch")

    def submit_job(self, job_id: str, name: str, operation_fn: Callable[[], Path]) -> Job:
        """Queue a job for background execution."""
        job = Job(job_id=job_id, name=name, operation_fn=operation_fn)
        self.jobs[job_id] = job

        def _run_with_tracking() -> Path:
            try:
                job.status = JobStatus.RUNNING
                self.logger.info(f"Job {job_id} started: {name}")
                output = operation_fn()
                job.status = JobStatus.COMPLETED
                job.result = JobResult(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    output_path=output,
                )
                self.logger.info(f"Job {job_id} completed: {name}")
                return output
            except Exception as exc:
                job.status = JobStatus.FAILED
                error_msg = str(exc)
                job.result = JobResult(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    error_message=error_msg,
                )
                self.logger.error(f"Job {job_id} failed: {error_msg}")
                raise

        future = self.executor.submit(_run_with_tracking)
        job.future = future
        return job

    def get_job(self, job_id: str) -> Job | None:
        """Retrieve a job by ID."""
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Attempt to cancel a pending or running job."""
        job = self.jobs.get(job_id)
        if not job or not job.future:
            return False
        was_cancelled = job.future.cancel()
        if was_cancelled:
            job.status = JobStatus.CANCELLED
            self.logger.info(f"Job {job_id} cancelled")
        return was_cancelled

    def list_jobs(self) -> list[Job]:
        """Get all jobs in execution order."""
        return list(self.jobs.values())

    def shutdown(self) -> None:
        """Gracefully stop the executor."""
        self.executor.shutdown(wait=True)
