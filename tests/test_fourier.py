import numpy as np
import pytest
from scipy import linalg

from qbench.fourier import FourierCircuits, discrimination_probability_upper_bound


def _assert_unitaries_equal_up_to_phase(actual, expected):
    supposedly_scalar = actual @ expected.conj().T
    np.testing.assert_allclose(
        supposedly_scalar, np.diag([supposedly_scalar[0, 0]] * actual.shape[0]), atol=1e-10
    )


def _v0_ref(phi):
    """Explicit formula for V0.

    This function is used for comparison with V0 decomposed into gates available in Amazon braket.
    """
    phi_adjusted = (np.pi - phi) / 4
    return np.array(
        [
            [1j * np.sin(phi_adjusted), -1j * np.cos(phi_adjusted)],
            [-np.cos(phi_adjusted), -np.sin(phi_adjusted)],
        ]
    )


def _v1_ref(phi):
    """Explicit formula for V1.

    This function is used for comparison with V1 decomposed into gates available in Amazon braket.
    """
    phi_adjusted = (np.pi - phi) / 4
    return np.array(
        [
            [1j * np.cos(phi_adjusted), -1j * np.sin(phi_adjusted)],
            [np.sin(phi_adjusted), np.cos(phi_adjusted)],
        ]
    )


def _swap_gate():
    return np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])


def _v0_v1_block_diag_ref(phi):
    swap = _swap_gate()
    return swap @ linalg.block_diag(_v0_ref(phi), _v1_ref(phi)) @ swap


def _proj(ket):
    return np.outer(ket, ket.conj())


@pytest.mark.parametrize("gateset", [None, "rigetti"])
class TestFourierCircuits:
    def test_initial_state_prepared_from_ket_zeros_is_maximally_entangled(self, gateset):
        bell = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)])
        expected_proj = _proj(bell)

        circuit = FourierCircuits(phi=0.1, gateset=gateset).state_preparation(0, 1)
        actual_proj = _proj(circuit.as_unitary()[:, 0])
        np.testing.assert_allclose(actual_proj, expected_proj, atol=1e-10)

    @pytest.mark.parametrize("phi", [np.pi, np.pi / 4, np.pi / 5, np.sqrt(2), 0])
    def test_black_box_has_correct_unitary(self, phi, gateset):
        circuit = FourierCircuits(phi=phi, gateset=gateset).unitary_to_discriminate(0)
        expected_unitary = linalg.dft(2) @ np.diag([1, np.exp(-1j * phi)]) @ linalg.dft(2) / 2

        _assert_unitaries_equal_up_to_phase(circuit.as_unitary(), expected_unitary)

    @pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
    def test_decomposed_v0_dagger_is_equal_to_the_original_one(self, phi: float, gateset):
        actual = FourierCircuits(phi=phi, gateset=gateset).v0_dag(0).as_unitary()
        expected = _v0_ref(phi).conj().T

        _assert_unitaries_equal_up_to_phase(actual, expected)

    @pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
    def test_decomposed_v1_is_equal_to_the_original_one(self, phi: float, gateset):
        actual = FourierCircuits(phi=phi, gateset=gateset).v1_dag(0).as_unitary()
        expected = _v1_ref(phi).conj().T

        _assert_unitaries_equal_up_to_phase(actual, expected)

    @pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
    def test_decomposed_v0_v1_circuit_is_equal_to_the_original_one_up_to_phase(
        self, phi: float, gateset
    ):
        actual = FourierCircuits(phi=phi, gateset=gateset).controlled_v0_v1_dag(0, 1).as_unitary()
        expected = _v0_v1_block_diag_ref(phi).conj().T

        _assert_unitaries_equal_up_to_phase(actual, expected)


def test_computed_exact_probabilities_are_feasible():
    phis = np.linspace(0, 2 * np.pi, 10000)

    probs = discrimination_probability_upper_bound(phis)

    assert np.all(probs >= 0) and np.all(probs <= 1)
