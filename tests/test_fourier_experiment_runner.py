import numpy as np
import pytest

from qbench.common_models import SimpleBackendDescription
from qbench.fourier import FourierDiscriminationExperiment
from qbench.fourier._experiment_runner import (
    fetch_statuses,
    resolve_results,
    run_experiment,
)


@pytest.fixture
def async_backend_description():
    return SimpleBackendDescription(
        provider="qbench.mock_backend:MockProvider", name="mock-backend", asynchronous=True
    )


@pytest.fixture
def sync_backend_description():
    return SimpleBackendDescription(
        provider="qbench.mock_backend:MockProvider", name="mock-backend", asynchronous=False
    )


@pytest.fixture(params=["direct_sum", "postselection"])
def experiment(request):
    return FourierDiscriminationExperiment.parse_obj(
        {
            "type": "discrimination-fourier",
            "qubits": [
                {"target": 0, "ancilla": 1},
                {"target": 1, "ancilla": 0},
                {"target": 2, "ancilla": 5},
            ],
            "angles": {"start": 0, "stop": 2, "num_steps": 3},
            "method": request.param,
            "num_shots": 10,
        }
    )


def _assert_sync_results_contain_data_for_all_circuits(
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


class TestSynchronousExecutionOfExperiment:
    def test_experiment_results_contain_measurements_for_each_circuit_qubit_pair_and_phi(
        self, experiment, sync_backend_description
    ):
        results = run_experiment(experiment, sync_backend_description)
        _assert_sync_results_contain_data_for_all_circuits(experiment, results)


class TestASynchronousExecutionOfExperiment:
    def test_number_of_fetched_statuses_corresponds_to_number_of_jobs(
        self, experiment, async_backend_description
    ):
        result = run_experiment(experiment, async_backend_description)
        statuses = fetch_statuses(result)

        assert len(result.results) == sum(statuses.values())

    def test_resolving_results_gives_object_with_histograms_for_all_circuits(
        self, experiment, async_backend_description
    ):
        results = run_experiment(experiment, async_backend_description)
        resolved = resolve_results(results)

        _assert_sync_results_contain_data_for_all_circuits(experiment, resolved)

    def test_obtaining_status_for_synchronous_experiment_terminates_program(
        self, experiment, sync_backend_description
    ):
        results = run_experiment(experiment, sync_backend_description)

        with pytest.raises(SystemExit):
            fetch_statuses(results)

    def test_resolving_result_of_synchronous_experiment_terminates_program(
        self, experiment, sync_backend_description
    ):
        results = run_experiment(experiment, sync_backend_description)

        with pytest.raises(SystemExit):
            resolve_results(results)
