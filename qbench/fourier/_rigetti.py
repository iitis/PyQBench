import numpy as np
from braket import circuits


def _rigetti_hadamard(qubit):
    """Decomposition of Hadamard gate using only Rigetti native gates.

    The decomposition uses the identity: H = RX(pi/2) RZ(pi/2) RX(pi/2)
    """
    return circuits.Circuit().rx(qubit, np.pi / 2).rz(qubit, np.pi / 2).rx(qubit, np.pi / 2)


def _rigetti_cnot(control, target):
    """Decomposition of CNOT gate using only Rigetti native gates.

    The decomposition uses identity: CNOT(i, j) = H(j) CZ(i, j) H(j), and the hadamard gates
    are decomposed using _rigetti_hadamard function.
    """
    return _rigetti_hadamard(target).cz(control, target) + _rigetti_hadamard(target)


# For description of functions above refer to the __init__ file in qbench.fourier


def _state_preparation(target, ancilla):
    return _rigetti_hadamard(target) + _rigetti_cnot(target, ancilla)


def _black_box_dag(qubit, phi):
    return (
        circuits.Circuit()
        .rz(qubit, np.pi / 2)
        .rx(qubit, np.pi / 2)
        .rz(qubit, -phi)
        .rx(qubit, -np.pi / 2)
        .rz(qubit, -np.pi / 2)
    )


def _v0_dag(qubit, phi):
    return (
        circuits.Circuit()
        .rz(qubit, -np.pi / 2)
        .rx(qubit, np.pi / 2)
        .rz(qubit, -(phi + np.pi) / 2)
        .rx(qubit, -np.pi / 2)
    )


def _v1_dag(qubit, phi):
    return (
        circuits.Circuit()
        .rz(qubit, np.pi / 2)
        .rx(qubit, np.pi / 2)
        .rz(qubit, -(np.pi - phi) / 2)
        .rx(qubit, -np.pi / 2)
    )


def _v0_v1_direct_sum(target, ancilla, phi):
    return (
        circuits.Circuit().rz(target, np.pi)
        + _v0_dag(ancilla, phi)
        + _rigetti_cnot(target, ancilla)
    )
