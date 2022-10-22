"""Testing utilities related qbench.fourier packager."""
from typing import List, cast

import numpy as np

from qbench.fourier import (
    FourierDiscriminationExperiment,
    FourierDiscriminationSyncResult,
)
from qbench.fourier._models import SingleResult


def assert_sync_results_contain_data_for_all_circuits(
    experiment: FourierDiscriminationExperiment, results: FourierDiscriminationSyncResult
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
