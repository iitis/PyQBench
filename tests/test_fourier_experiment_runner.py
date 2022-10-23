import numpy as np
import pytest

from qbench.common_models import SimpleBackendDescription
from qbench.fourier import FourierDiscriminationExperiment
from qbench.fourier._experiment_runner import (
    fetch_statuses,
    resolve_results,
    run_experiment,
    tabulate_results,
)
from qbench.fourier.testing import assert_sync_results_contain_data_for_all_circuits


@pytest.fixture
def async_backend_description():
    return SimpleBackendDescription(
        provider="qbench.testing:MockProvider", name="mock-backend", asynchronous=True
    )


@pytest.fixture
def sync_backend_description():
    return SimpleBackendDescription(
        provider="qbench.testing:MockProvider", name="mock-backend", asynchronous=False
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


class TestSynchronousExecutionOfExperiment:
    def test_experiment_results_contain_measurements_for_each_circuit_qubit_pair_and_phi(
        self, experiment, sync_backend_description
    ):
        results = run_experiment(experiment, sync_backend_description)
        assert_sync_results_contain_data_for_all_circuits(experiment, results)


class TestASynchronousExecutionOfExperiment:
    def test_number_of_fetched_statuses_corresponds_to_number_of_jobs(
        self, experiment, async_backend_description
    ):
        result = run_experiment(experiment, async_backend_description)
        statuses = fetch_statuses(result)

        assert len(result.data) == sum(statuses.values())

    def test_resolving_results_gives_object_with_histograms_for_all_circuits(
        self, experiment, async_backend_description
    ):
        results = run_experiment(experiment, async_backend_description)
        resolved = resolve_results(results)

        assert_sync_results_contain_data_for_all_circuits(experiment, resolved)

    def test_tabulating_results_gives_dataframe_with_probabilities_for_all_circuits(
        self, experiment, sync_backend_description
    ):
        result = run_experiment(experiment, sync_backend_description)
        expected_keys = [
            (pair.target, pair.ancilla, phi)
            for pair in experiment.qubits
            for phi in np.linspace(
                experiment.angles.start, experiment.angles.stop, experiment.angles.num_steps
            )
        ]

        tab = tabulate_results(result)

        assert list(tab.columns) == ["target", "ancilla", "phi", "disc_prob"]
        actual_keys = [(row[0], row[1], row[2]) for row in tab.itertuples(index=False)]
        assert sorted(actual_keys) == sorted(expected_keys)
