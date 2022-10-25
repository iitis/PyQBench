"""Testing utilities related qbench.fourier packager."""
from typing import Sequence, Tuple

import pandas as pd

from ._models import FourierDiscriminationSyncResult, FourierExperimentSet

LabelSequence = Sequence[Tuple[int, int, float]]


def _experiment_labels_equal(actual: LabelSequence, expected: LabelSequence) -> bool:
    """Assert two sequences of experiment labels are equal.

    The label comprises index of target, index of ancilla and Fourier angle phi.
    While we require exact equality between indices of qubits, equality of angles is
    checked only up to 7 decimal places, which is enough for the purpose of our unit tests.
    The exact equality of angles cannot be expected because of the serialization of floating
    point numbers.
    """
    return len(actual) == len(expected) and all(
        label1[0:2] == label2[0:2] and abs(label1[2] - label2[2]) < 1e-7
        for label1, label2 in zip(sorted(actual), sorted(expected))
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
    expected_labels = list(experiments.enumerate_experiment_labels())
    actual_labels = [(entry.target, entry.ancilla, entry.phi) for entry in results.data]

    assert _experiment_labels_equal(actual_labels, expected_labels)


def assert_tabulated_results_contain_data_for_all_experiments(
    experiments: FourierExperimentSet, dataframe: pd.DataFrame
) -> None:
    expected_labels = list(experiments.enumerate_experiment_labels())
    actual_labels = [(row[0], row[1], row[2]) for row in dataframe.itertuples(index=False)]

    assert _experiment_labels_equal(actual_labels, expected_labels)
