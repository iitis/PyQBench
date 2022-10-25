import ast
import logging

import pandas as pd
import pytest
from yaml import safe_dump, safe_load

from qbench.cli import main
from qbench.common_models import SimpleBackendDescription
from qbench.fourier import (
    FourierDiscriminationAsyncResult,
    FourierDiscriminationSyncResult,
    FourierExperimentSet,
)
from qbench.fourier.testing import (
    assert_sync_results_contain_data_for_all_experiments,
    assert_tabulated_results_contain_data_for_all_experiments,
)
from qbench.testing import MockProvider


# Wrappers around main, so that we don't repeat 'main' over and over again
def _benchmark(experiment_path, backend_path, output_path):
    main(
        [
            "disc-fourier",
            "benchmark",
            str(experiment_path),
            str(backend_path),
            "--output",
            str(output_path),
        ]
    )


def _read(model_cls, path):
    with open(path) as stream:
        return model_cls.parse_obj(safe_load(stream))


@pytest.fixture
def create_experiment_file(tmp_path):
    experiments = FourierExperimentSet.parse_obj(
        {
            "type": "discrimination-fourier",
            "qubits": [
                {"target": 0, "ancilla": 1},
                {"target": 1, "ancilla": 0},
                {"target": 2, "ancilla": 5},
            ],
            "angles": {"start": 0, "stop": 2, "num_steps": 3},
            "method": "direct_sum",
            "num_shots": 100,
        }
    )

    with open(tmp_path / "experiment.yml", "wt") as stream:
        safe_dump(experiments.dict(), stream)


@pytest.fixture
def create_backend_description(tmp_path):
    description = SimpleBackendDescription(
        provider="qbench.testing:MockProvider", name="mock-backend", asynchronous=True
    )

    with open(tmp_path / "backend.yml", "wt") as stream:
        safe_dump(description.dict(), stream)


@pytest.fixture
def create_failing_backend_description(tmp_path):
    description = SimpleBackendDescription(
        provider="qbench.testing:MockProvider", name="failing-mock-backend", asynchronous=True
    )

    with open(tmp_path / "failing-backend.yml", "wt") as stream:
        safe_dump(description.dict(), stream)


@pytest.mark.usefixtures("create_experiment_file", "create_backend_description")
def test_main_entrypoint_with_disc_fourier_command(tmp_path, capsys):
    MockProvider().reset_caches()

    experiment_path = tmp_path / "experiment.yml"
    backend_path = tmp_path / "backend.yml"
    async_output_path = tmp_path / "async_output.yml"
    resolved_output_path = tmp_path / "result.yml"
    tabulated_output_path = tmp_path / "result.csv"

    _benchmark(experiment_path, backend_path, async_output_path)

    main(["disc-fourier", "status", str(async_output_path)])

    main(["disc-fourier", "resolve", str(async_output_path), str(resolved_output_path)])

    main(["disc-fourier", "tabulate", str(resolved_output_path), str(tabulated_output_path)])

    experiments = _read(FourierExperimentSet, experiment_path)
    results = _read(FourierDiscriminationSyncResult, resolved_output_path)
    async_output = _read(FourierDiscriminationAsyncResult, async_output_path)

    result_df = pd.read_csv(tabulated_output_path)

    assert_sync_results_contain_data_for_all_experiments(experiments, results)

    captured = capsys.readouterr()
    status_output = ast.literal_eval(captured.out)
    assert isinstance(status_output, dict)
    assert sum(status_output.values()) == len(async_output.data)

    assert list(result_df.columns) == ["target", "ancilla", "phi", "disc_prob"]
    assert_tabulated_results_contain_data_for_all_experiments(experiments, result_df)


@pytest.mark.usefixtures("create_experiment_file", "create_failing_backend_description")
def test_main_entrypoint_with_disc_fourier_command_and_failing_backend(tmp_path, capsys, caplog):
    # The only difference compared to the previous test is that now we know that some jobs failed
    # Order of circuits run is subject to change but we know (because of how mock backend works)
    # that two jobs failed.
    # We have total of 3 * 3 * 2 = 18 circuits to run. Mock backend has limit of 2 circuits per
    # job, so we expect 14 circuits to be present in data
    MockProvider().reset_caches()

    experiment_path = tmp_path / "experiment.yml"
    backend_path = tmp_path / "failing-backend.yml"
    async_output_path = tmp_path / "async_output.yml"
    resolved_output_path = tmp_path / "result.yml"
    tabulated_output_path = tmp_path / "result.csv"

    _benchmark(experiment_path, backend_path, async_output_path)

    main(["disc-fourier", "status", str(async_output_path)])

    with caplog.at_level(logging.WARNING):
        main(["disc-fourier", "resolve", str(async_output_path), str(resolved_output_path)])

    main(["disc-fourier", "tabulate", str(resolved_output_path), str(tabulated_output_path)])

    results = _read(FourierDiscriminationSyncResult, resolved_output_path)
    async_output = _read(FourierDiscriminationAsyncResult, async_output_path)

    result_df = pd.read_csv(tabulated_output_path)

    all_keys = [
        (entry.target, entry.ancilla, entry.phi, sub_entry.name)
        for entry in results.data
        for sub_entry in entry.results_per_circuit
    ]

    assert len(all_keys) == 14

    captured = capsys.readouterr()
    status_output = ast.literal_eval(captured.out)
    assert isinstance(status_output, dict)
    assert sum(status_output.values()) == len(async_output.data)

    assert (
        "Some jobs have failed. Examine the output file to determine which data are missing."
        in caplog.text
    )

    # Note that generally one cannot expect to reconstruct N/2 probabilities from N circuits in
    # the direct sum experiments. However, this test case is designed so that failing jobs
    # constitute single computation of probability, and hence the succeeding ones are pairs
    # needed for computing probabilities.
    assert result_df.shape[0] == 7
