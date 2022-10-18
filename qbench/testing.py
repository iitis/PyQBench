"""Module implementing several test utilities and mocks."""
from functools import lru_cache
from typing import List

from qiskit import QiskitError
from qiskit.providers import BackendV1, JobStatus, JobV1, ProviderV1
from qiskit.providers.aer import AerSimulator


def _make_job_fail(job):
    def _status():
        return JobStatus.ERROR

    def _result():
        raise QiskitError("Job failed intentionally")

    job.status = _status
    job.result = _result
    return job


class MockSimulator(AerSimulator):
    """Local mock simulator adhering to the BakckendV2 interface, but caching all jobs it executes.

    This class is a wrapper around AerSimulator, so in particular all the initializer arguments
    are the same as for AerSimulator.
    """

    def __init__(self, fail_job_indices=None, *args, **kwargs):
        self._fail_job_indices = [] if fail_job_indices is None else fail_job_indices
        super().__init__(*args, **kwargs)
        self._job_dict = {}
        self._job_count = 0

    def name(self):
        """Return name of this backend."""
        return "mock-backend"

    def retrieve_job(self, job_id: str) -> JobV1:
        """Retrieve job of given ID."""
        return self._job_dict[job_id]

    def run(self, *args, **kwargs):
        """Run given circuit and return corresponding job."""
        job = super().run(*args, **kwargs)
        if self._job_count in self._fail_job_indices:
            job = _make_job_fail(job)
        self._job_count += 1
        self._job_dict[job.job_id()] = job
        return job


@lru_cache()
def _create_mock_simulator(**kwargs):
    return MockSimulator(**kwargs)


class MockProvider(ProviderV1):
    """Provider for obtaining instances of MockSimulator."""

    def backends(self, name=None, **kwargs) -> List[BackendV1]:
        """Get list of all backends obtainable by this provider.

        Unsurprisingly, the list comprises only and instance of MockSimulator. However, it is
        always the same instance. That way, we are able to retrieve the cached jobs.
        """
        return [_create_mock_simulator(**kwargs)]
