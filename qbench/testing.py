"""Module implementing several test utilities and mocks."""
from datetime import datetime
from functools import lru_cache
from typing import List

from qiskit import QiskitError
from qiskit.providers import BackendV1, JobStatus, JobV1, ProviderV1
from qiskit.providers.aer import AerSimulator
from qiskit.providers.models import BackendProperties
from qiskit.providers.models.backendproperties import Nduv


def _make_job_fail(job):
    def _status():
        return JobStatus.ERROR

    def _result():
        raise QiskitError("Job failed intentionally")

    job.status = _status
    job.result = _result
    return job


def _add_mitigation_info(job):
    # All typing problems ignored below seem to be problems with BackendProperties and Nduv
    props = BackendProperties(
        backend_name=job.backend().name(),
        backend_version=job.backend().version,
        last_update_date=datetime.now(),  # type: ignore
        qubits=[
            [
                Nduv(datetime.now(), "prob_meas1_prep0", "", 0.21),  # type: ignore
                Nduv(datetime.now(), "prob_meas0_prep1", "", 0.37),  # type: ignore
            ]
            for _ in range(20)
        ],
        gates=[],
        general=[],
    )

    def _properties():
        return props

    job.properties = _properties
    return job


class MockSimulator(AerSimulator):
    """Local mock simulator adhering to the BackendV2 interface, but caching all jobs it executes.

    This class is a wrapper around AerSimulator, so in particular all the initializer arguments
    are the same as for AerSimulator.
    """

    def __init__(
        self, fail_job_indices=None, name="mock-backend", job_wrappers=None, *args, **kwargs
    ):
        self._fail_job_indices = [] if fail_job_indices is None else fail_job_indices
        self._job_wrappers = [] if job_wrappers is None else job_wrappers
        super().__init__(*args, **kwargs)
        self._job_dict = {}
        self._job_count = 0
        self._name = name

    def name(self):
        """Return name of this backend."""
        return self._name

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
        for wrapper in self._job_wrappers:
            job = wrapper(job)
        return job


@lru_cache()
def _create_mock_simulator():
    return MockSimulator()


@lru_cache()
def _create_failing_mock_simulator():
    return MockSimulator(name="failing-mock-backend", fail_job_indices=(1, 2))


@lru_cache()
def _create_mock_simulator_with_mitigation_info():
    return MockSimulator(name="mock-backend-with-mitigation", job_wrappers=[_add_mitigation_info])


class MockProvider(ProviderV1):
    """Provider for obtaining instances of MockSimulator."""

    def backends(self, name=None, **kwargs) -> List[BackendV1]:
        """Get list of all backends obtainable by this provider.

        Unsurprisingly, the list comprises only and instance of MockSimulator. However, it is
        always the same instance. That way, we are able to retrieve the cached jobs.
        """
        all_backends = [
            _create_mock_simulator(),
            _create_failing_mock_simulator(),
            _create_mock_simulator_with_mitigation_info(),
        ]
        return (
            all_backends
            if name is None
            else [backend for backend in all_backends if backend.name() == name]
        )

    @staticmethod
    def reset_caches():
        """Reset caches thus allowing for construction of new Mock simulators.

        This is stateful and ugly, but mock simulators need to be stateful so that
        we can simulate retrieval"""
        _create_failing_mock_simulator.cache_clear()
        _create_mock_simulator.cache_clear()
        _create_mock_simulator_with_mitigation_info.cache_clear()
