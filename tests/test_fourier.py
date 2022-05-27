import numpy as np
import pytest
from scipy import linalg

from qbench.fourier import (
    global_phase_circuit,
    measurement_circuit,
    state_preparation_circuit,
)


def test_initial_state_prepared_from_ket_zeros_is_maximally_entangled():
    ket0 = np.array([1, 0, 0, 0])
    circuit = state_preparation_circuit(0, 1)

    np.testing.assert_allclose(circuit.as_unitary() @ ket0, [1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])


@pytest.mark.parametrize("phi", [np.pi, np.pi / 4, np.pi / 5, np.sqrt(2), 0])
def test_measurement_circuit_has_correct_unitary(phi):
    circuit = measurement_circuit(phi)
    expected_unitary = linalg.dft(2) @ np.diag([1, np.exp(1j * phi)]) @ linalg.dft(2) / 2

    np.testing.assert_allclose(circuit.as_unitary(), expected_unitary, atol=1e-6)


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
def test_decomposition_of_global_phase_expected_correct_unitary(phi):
    expected = np.diag([np.exp(1j * phi), np.exp(1j * phi)])
    actual = global_phase_circuit(phi, 0).as_unitary()

    np.testing.assert_allclose(expected, actual)
