"""Module implementing several test utilities and mocks."""
from functools import lru_cache
from typing import List

from qiskit.providers import BackendV1, JobV1, ProviderV1
from qiskit.providers.aer import AerSimulator


class MockSimulator(AerSimulator):
    """Local mock simulator adhering to the BakckendV2 interface, but caching all jobs it executes.

    This class is a wrapper around AerSimulator, so in particular all the initializer arguments
    are the same as for AerSimulator.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_dict = {}

    def name(self):
        """Return name of this backend."""
        return "mock-backend"

    def retrieve_job(self, job_id: str) -> JobV1:
        """Retrieve job of given ID."""
        return self._job_dict[job_id]

    def run(self, *args, **kwargs):
        """Run given circuit and return corresponding job."""
        job = super().run(*args, **kwargs)
        self._job_dict[job.job_id()] = job
        return job


@lru_cache()
def _create_mock_simulator():
    return MockSimulator()


class MockProvider(ProviderV1):
    """Provider for obtaining instances of MockSimulator."""

    def backends(self, name=None, **kwargs) -> List[BackendV1]:
        """Get list of all backends obtainable by this provider.

        Unsurprisingly, the list comprises only and instance of MockSimulator. However, it is
        always the same instance. That way, we are able to retrieve the cached jobs.
        """
        return [_create_mock_simulator()]
