from functools import lru_cache

import numpy as np
from qiskit.providers import JobV1, ProviderV1
from qiskit.providers.aer import AerSimulator

from qbench.fourier import FourierDiscriminationExperiment


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


def assert_sync_results_contain_data_for_all_circuits(
    experiment: FourierDiscriminationExperiment, results
):
    actual_qubit_pairs = [(entry.target, entry.ancilla) for entry in results.results]

    expected_qubit_pairs = [(entry.target, entry.ancilla) for entry in experiment.qubits]

    assert set(actual_qubit_pairs) == set(expected_qubit_pairs)
    assert len(actual_qubit_pairs) == len(expected_qubit_pairs)

    expected_angles = np.linspace(
        experiment.angles.start, experiment.angles.stop, experiment.angles.num_steps
    )

    assert all(
        sorted([counts.phi for counts in entry.measurement_counts]) == sorted(expected_angles)
        for entry in results.results
    )
