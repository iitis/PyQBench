import ast
import logging

import pytest
from yaml import safe_dump, safe_load

from qbench.cli import main
from qbench.common_models import SimpleBackendDescription
from qbench.fourier import FourierDiscriminationExperiment, FourierDiscriminationResult
from qbench.fourier.testing import assert_sync_results_contain_data_for_all_circuits
from qbench.testing import MockProvider


@pytest.fixture
def create_experiment_file(tmp_path):
    experiment = FourierDiscriminationExperiment.parse_obj(
        {
            "type": "discrimination-fourier",
            "qubits": [
                {"target": 0, "ancilla": 1},
                {"target": 1, "ancilla": 0},
                {"target": 2, "ancilla": 5},
            ],
            "angles": {"start": 0, "stop": 2, "num_steps": 3},
            "method": "direct_sum",
            "num_shots": 10,
        }
    )

    with open(tmp_path / "experiment.yml", "wt") as stream:
        safe_dump(experiment.dict(), stream)


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
    experiment_path = tmp_path / "experiment.yml"
    backend_path = tmp_path / "backend.yml"
    async_output_path = tmp_path / "async_output.yml"
    resolved_output_path = tmp_path / "result.yml"

    main(
        [
            "disc-fourier",
            "benchmark",
            str(experiment_path),
            str(backend_path),
            "--output",
            str(async_output_path),
        ]
    )

    main(["disc-fourier", "status", str(async_output_path)])

    main(["disc-fourier", "resolve", str(async_output_path), str(resolved_output_path)])

    with open(experiment_path) as stream:
        experiment = FourierDiscriminationExperiment.parse_obj(safe_load(stream))

    with open(resolved_output_path) as stream:
        results = FourierDiscriminationResult.parse_obj(safe_load(stream))

    with open(async_output_path) as stream:
        async_output = FourierDiscriminationResult.parse_obj(safe_load(stream))

    assert_sync_results_contain_data_for_all_circuits(experiment, results)

    captured = capsys.readouterr()
    status_output = ast.literal_eval(captured.out)
    assert isinstance(status_output, dict)
    assert sum(status_output.values()) == len(async_output.results)


@pytest.mark.usefixtures("create_experiment_file", "create_failing_backend_description")
def test_main_entrypoint_with_disc_fourier_command_and_failing_backend(tmp_path, capsys, caplog):
    MockProvider().reset_caches()

    experiment_path = tmp_path / "experiment.yml"
    backend_path = tmp_path / "failing-backend.yml"
    async_output_path = tmp_path / "async_output.yml"
    resolved_output_path = tmp_path / "result.yml"

    main(
        [
            "disc-fourier",
            "benchmark",
            str(experiment_path),
            str(backend_path),
            "--output",
            str(async_output_path),
        ]
    )

    main(["disc-fourier", "status", str(async_output_path)])

    with caplog.at_level(logging.WARNING):
        main(["disc-fourier", "resolve", str(async_output_path), str(resolved_output_path)])

    with open(resolved_output_path) as stream:
        results = FourierDiscriminationResult.parse_obj(safe_load(stream))

    with open(async_output_path) as stream:
        async_output = FourierDiscriminationResult.parse_obj(safe_load(stream))

    # The only difference compared to the previous test is that now we know that some jobs failed
    # Order of circuits run is subject to change but we know (because of how mock backend works)
    # that two jobs failed.
    # We have total of 3 * 3 * 2 = 18 circuits to run. Mock backend has limit of 2 circuits per
    # job, so we expect 14 circuits to be present in results

    assert (
        sum(
            1
            for entry in results.results
            for counts in entry.measurement_counts
            for _ in counts.circuits_for_angle
        )
        == 14
    )

    captured = capsys.readouterr()
    status_output = ast.literal_eval(captured.out)
    assert isinstance(status_output, dict)
    assert sum(status_output.values()) == len(async_output.results)

    assert (
        "Some jobs have failed. Examine the output file to determine which results are missing."
        in caplog.text
    )
