"""Testing utilities related qbench.fourier packager."""
import numpy as np

from qbench.fourier import (
    FourierDiscriminationExperiment,
    FourierDiscriminationSyncResult,
)


def assert_sync_results_contain_data_for_all_circuits(
    experiment: FourierDiscriminationExperiment, results: FourierDiscriminationSyncResult
) -> None:
    """Verify synchronous result of computation has measurements for each qubits pair and phi.

    :param experiment: Fourier discrimination experiment. Note that this function does not take
     into account the method used in experiment, and only checks (target, ancilla) pairs ond
     values of phi parameter.
    :param results: data of execution of synchronous experiment.
    :raise: AssertionError if measurements for some combination of (target, ancilla, phi) are
     missing.
    """
    expected_keys = [
        (pair.target, pair.ancilla, phi)
        for pair in experiment.qubits
        for phi in np.linspace(
            experiment.angles.start, experiment.angles.stop, experiment.angles.num_steps
        )
    ]

    actual_keys = [(entry.target, entry.ancilla, entry.phi) for entry in results.data]

    def _are_equal(actual, expected):
        return actual[0:2] == expected[0:2] and abs(actual[2] - expected[2]) < 1e-6

    assert len(actual_keys) == len(expected_keys) and all(
        _are_equal(actual, expected) for actual, expected in zip(expected_keys, actual_keys)
    )
