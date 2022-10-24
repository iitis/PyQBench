"""Testing utilities related qbench.fourier packager."""
from typing import Sequence, Tuple

import pandas as pd

from ._models import FourierDiscriminationSyncResult, FourierExperimentSet

KeySequence = Sequence[Tuple[int, int, float]]


def _circuit_keys_equal(actual: KeySequence, expected: KeySequence) -> bool:
    """Assert two sequences of"""
    return len(actual) == len(expected) and all(
        key1[0:2] == key2[0:2] and abs(key1[2] - key2[2]) < 1e-7
        for key1, key2 in zip(sorted(actual), sorted(expected))
    )


def assert_sync_results_contain_data_for_all_experiments(
    experiments: FourierExperimentSet, results: FourierDiscriminationSyncResult
) -> None:
    """Verify synchronous result of computation has measurements for each qubits pair and phi.

    :param experiments: set of Fourier discrimination experiments.
     Note that this function does not take into account the method used in experiments,
     and only checks (target, ancilla) pairs ond values of phi parameter.
    :param results: results of execution of synchronous experiments.
    :raise: AssertionError if measurements for some combination of (target, ancilla, phi) are
     missing.
    """
    expected_keys = list(experiments.enumerate_experiment_labels())
    actual_keys = [(entry.target, entry.ancilla, entry.phi) for entry in results.data]

    assert _circuit_keys_equal(actual_keys, expected_keys)


def assert_tabulated_results_contain_data_for_all_circuits(
    experiments: FourierExperimentSet, dataframe: pd.DataFrame
) -> None:
    expected_keys = list(experiments.enumerate_experiment_labels())
    actual_keys = [(row[0], row[1], row[2]) for row in dataframe.itertuples(index=False)]

    assert _circuit_keys_equal(actual_keys, expected_keys)
