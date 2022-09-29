"""Module implementing several test utilities and mocks."""
from functools import lru_cache
from typing import List, cast

import numpy as np
from qiskit.providers import BackendV1, JobV1, ProviderV1
from qiskit.providers.aer import AerSimulator

from qbench.fourier import FourierDiscriminationExperiment
from qbench.fourier._models import FourierDiscriminationResult, SingleResult


class MockSimulator(AerSimulator):
    """A local mock simulator adhering to the BakckendV2 interface, but caching all jobs it executes.

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


def assert_sync_results_contain_data_for_all_circuits(
    experiment: FourierDiscriminationExperiment, results: FourierDiscriminationResult
) -> None:
    """Verify synchronous result of computation has measurements for each qubits pair and phi.

    :param experiment: Fourier discrimination experiment. Note that this function does not take
     into account the method used in experiment, and only checks (target, ancilla) pairs ond
     values of phi parameter.
    :param results: results of execution of synchronous experiment.
    :raise: AssertionError if measurements for some combination of (target, ancilla, phi) are
     missing.
    """
    actual_qubit_pairs = [
        (entry.target, entry.ancilla) for entry in cast(List[SingleResult], results.results)
    ]

    expected_qubit_pairs = [(entry.target, entry.ancilla) for entry in experiment.qubits]

    assert set(actual_qubit_pairs) == set(expected_qubit_pairs)
    assert len(actual_qubit_pairs) == len(expected_qubit_pairs)

    expected_angles = np.linspace(
        experiment.angles.start, experiment.angles.stop, experiment.angles.num_steps
    )

    assert all(
        sorted([counts.phi for counts in entry.measurement_counts]) == sorted(expected_angles)
        for entry in cast(List[SingleResult], results.results)
    )
