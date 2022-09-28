from functools import lru_cache

from qiskit.providers import JobV1, ProviderV1
from qiskit.providers.aer import AerSimulator


class MockSimulator(AerSimulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._job_dict = {}

    def name(self):
        return "mock-backend"

    def retrieve_job(self, job_id: str) -> JobV1:
        return self._job_dict[job_id]

    def run(self, *args, **kwargs):
        job = super().run(*args, **kwargs)
        self._job_dict[job.job_id()] = job
        return job


@lru_cache()
def _create_mock_simulator():
    return MockSimulator()


class MockProvider(ProviderV1):
    def backends(self, name=None, **kwargs):
        return [_create_mock_simulator()]
