import pytest

from qbench.common_models import SimpleBackendDescription
from qbench.fourier import FourierExperimentSet
from qbench.fourier.experiment_runner import (
    fetch_statuses,
    resolve_results,
    run_experiment,
    tabulate_results,
)
from qbench.fourier.testing import (
    assert_sync_results_contain_data_for_all_experiments,
    assert_tabulated_results_contain_data_for_all_experiments,
)


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


@pytest.fixture
def backend_with_mitigation_info_description():
    return SimpleBackendDescription(
        provider="qbench.testing:MockProvider",
        name="mock-backend-with-mitigation",
        asynchronous=False,
    )


@pytest.fixture(params=["direct_sum", "postselection"])
def experiments(request):
    return FourierExperimentSet.parse_obj(
        {
            "type": "discrimination-fourier",
            "qubits": [
                {"target": 0, "ancilla": 1},
                {"target": 1, "ancilla": 0},
                {"target": 2, "ancilla": 5},
            ],
            "angles": {"start": 0, "stop": 2, "num_steps": 3},
            "method": request.param,
            "num_shots": 100,
        }
    )


class TestSynchronousExecutionOfExperiments:
    def test_experiment_results_contain_measurements_for_each_circuit_qubit_pair_and_phi(
        self, experiments, sync_backend_description
    ):
        results = run_experiment(experiments, sync_backend_description)
        assert_sync_results_contain_data_for_all_experiments(experiments, results)


class TestASynchronousExecutionOfExperiments:
    def test_number_of_fetched_statuses_corresponds_to_number_of_jobs(
        self, experiments, async_backend_description
    ):
        result = run_experiment(experiments, async_backend_description)
        statuses = fetch_statuses(result)

        assert len(result.data) == sum(statuses.values())

    def test_resolving_results_gives_object_with_histograms_for_all_circuits(
        self, experiments, async_backend_description
    ):
        results = run_experiment(experiments, async_backend_description)
        resolved = resolve_results(results)

        assert_sync_results_contain_data_for_all_experiments(experiments, resolved)

    def test_tabulating_results_gives_dataframe_with_probabilities_for_all_circuits(
        self, experiments, sync_backend_description
    ):
        result = run_experiment(experiments, sync_backend_description)

        tab = tabulate_results(result)

        assert list(tab.columns) == ["target", "ancilla", "phi", "disc_prob"]
        assert_tabulated_results_contain_data_for_all_experiments(experiments, tab)

    def test_tabulating_results_gives_frame_with_mitigated_histogram_if_such_info_is_available(
        self, experiments, backend_with_mitigation_info_description
    ):
        result = run_experiment(experiments, backend_with_mitigation_info_description)

        tab = tabulate_results(result)

        assert list(tab.columns) == ["target", "ancilla", "phi", "disc_prob", "mit_disc_prob"]
        assert_tabulated_results_contain_data_for_all_experiments(experiments, tab)
