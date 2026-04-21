"""Tests for batch job processing."""

import time
from pathlib import Path

import pytest

from kpdf.operations.batch_processor import BatchProcessor, Job, JobStatus


def test_batch_processor_submit_job() -> None:
    processor = BatchProcessor(max_workers=1)
    try:
        def dummy_operation() -> Path:
            return Path("/tmp/output.pdf")

        job = processor.submit_job("job_1", "Test Job", dummy_operation)
        assert job.job_id == "job_1"
        assert job.name == "Test Job"
        
        # Give it a moment to execute
        time.sleep(0.2)
        
        # Check final state
        retrieved_job = processor.get_job("job_1")
        assert retrieved_job is not None
        assert retrieved_job.status == JobStatus.COMPLETED
        assert retrieved_job.result is not None
        assert retrieved_job.result.output_path == Path("/tmp/output.pdf")
    finally:
        processor.shutdown()


def test_batch_processor_job_failure() -> None:
    processor = BatchProcessor(max_workers=1)
    try:
        def failing_operation() -> Path:
            raise ValueError("Intentional test failure")

        job = processor.submit_job("job_fail", "Failing Job", failing_operation)
        
        # Give it a moment to execute
        time.sleep(0.1)
        
        # Check final state
        retrieved_job = processor.get_job("job_fail")
        assert retrieved_job is not None
        assert retrieved_job.status == JobStatus.FAILED
        assert retrieved_job.result is not None
        assert "Intentional test failure" in retrieved_job.result.error_message
    finally:
        processor.shutdown()


def test_batch_processor_cancel_pending() -> None:
    processor = BatchProcessor(max_workers=1)
    try:
        # Submit a long-running job to block the worker
        def slow_operation() -> Path:
            time.sleep(1)
            return Path("/tmp/output.pdf")

        job1 = processor.submit_job("job_slow", "Slow Job", slow_operation)
        
        # Immediately submit a second job that we'll try to cancel
        def quick_operation() -> Path:
            return Path("/tmp/output2.pdf")

        job2 = processor.submit_job("job_cancel", "Cancel Target", quick_operation)
        
        # Try to cancel the pending job
        cancelled = processor.cancel_job("job_cancel")
        assert cancelled is True
        
        # Give it a moment to reflect
        time.sleep(0.1)
        
        retrieved_job = processor.get_job("job_cancel")
        assert retrieved_job is not None
        assert retrieved_job.status == JobStatus.CANCELLED
    finally:
        processor.shutdown()


def test_batch_processor_list_jobs() -> None:
    processor = BatchProcessor(max_workers=1)
    try:
        def dummy_operation() -> Path:
            return Path("/tmp/output.pdf")

        for i in range(3):
            processor.submit_job(f"job_{i}", f"Job {i}", dummy_operation)

        jobs = processor.list_jobs()
        assert len(jobs) >= 3
        job_ids = {job.job_id for job in jobs}
        assert "job_0" in job_ids
        assert "job_1" in job_ids
        assert "job_2" in job_ids
    finally:
        processor.shutdown()
