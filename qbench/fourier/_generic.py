import numpy as np
from braket import circuits


def _state_preparation(target, ancilla):
    return circuits.Circuit().h(target).cnot(target, ancilla)


def _black_box_dag(qubit, phi):
    return circuits.Circuit().h(qubit).phaseshift(qubit, -phi).h(qubit)


def _v0_dag(qubit, phi):
    return circuits.Circuit().rz(qubit, -np.pi / 2).ry(qubit, -(phi + np.pi) / 2)


def _v1_dag(qubit, phi):
    return circuits.Circuit().rz(qubit, -np.pi / 2).ry(qubit, -(phi + np.pi) / 2).rx(qubit, -np.pi)


def _v0_v1_direct_sum(target, ancilla, phi):
    return (
        circuits.Circuit().phaseshift(target, np.pi)
        + _v0_dag(ancilla, phi)
        + circuits.Circuit().cnot(target, ancilla)
    )
