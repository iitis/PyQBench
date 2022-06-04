import numpy as np
import pytest
from scipy import linalg

from qbench.fourier import (
    global_phase_circuit,
    measurement_circuit,
    state_preparation_circuit,
    v0_circuit,
    v1_circuit,
)


def _v0_ref(phi):
    """Explicit formula for V0.

    This function is used for comparison with V0 decomposed into gates available in Amazon braket.
    """
    phi_adjusted = (np.pi - phi) / 4
    return np.array(
        [
            [1j * np.sin(phi_adjusted), -1j * np.cos(phi_adjusted)],
            [np.cos(phi_adjusted), np.sin(phi_adjusted)],
        ]
    )


def _v1_ref(phi):
    """Explicit formula for V1.

    This function is used for comparison with V1 decomposed into gates available in Amazon braket.
    """
    phi_adjusted = (np.pi - phi) / 4
    return np.array(
        [
            [-1j * np.cos(phi_adjusted), 1j * np.sin(phi_adjusted)],
            [np.sin(phi_adjusted), np.cos(phi_adjusted)],
        ]
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
def test_decomposed_v0_is_equal_to_the_original_one_if_global_phase_is_preserved(phi):
    actual = v0_circuit(phi, 0, preserve_global_phase=True).as_unitary()
    expected = _v0_ref(phi)

    np.testing.assert_allclose(expected, actual, atol=1e-10)


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
def test_decomposed_v1_is_equal_to_the_original_one_if_global_phase_is_preserved(phi):
    actual = v1_circuit(phi, 0, preserve_global_phase=True).as_unitary()
    expected = _v1_ref(phi)

    np.testing.assert_allclose(expected, actual, atol=1e-10)


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
def test_decomposed_v0_differs_from_the_original_one_only_by_phase(phi):
    # Since v0 is unitary, multiplication of the form (const * v0) @ v0^dagger should be
    # a scalar matrix, which is what this test checks.
    expected_diag = (
        v0_circuit(phi, 0, preserve_global_phase=False).as_unitary() @ _v0_ref(phi).conj().T
    )
    np.testing.assert_allclose(expected_diag, np.eye(2) * expected_diag[0, 0], atol=1e-10)


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
def test_decomposed_v1_differs_from_the_original_one_only_by_phase(phi):
    # See previous test for v0 for explanation of this test.
    expected_diag = (
        v1_circuit(phi, 0, preserve_global_phase=False).as_unitary() @ _v1_ref(phi).conj().T
    )
    np.testing.assert_allclose(expected_diag, np.eye(2) * expected_diag[0, 0], atol=1e-10)
