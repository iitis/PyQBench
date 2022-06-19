import numpy as np
from braket import circuits


def _state_preparation(target, ancilla):
    return circuits.Circuit().v(target).rz(target, np.pi).x(target).v(ancilla).ecr(target, ancilla)


def _black_box_dag(qubit, phi):
    return (
        circuits.Circuit()
        .v(qubit)
        .rz(qubit, np.pi / 2)
        .v(qubit)
        .rz(qubit, -phi)
        .v(qubit)
        .rz(qubit, np.pi / 2)
        .v(qubit)
    )


def _v0_dag(qubit, phi):
    return (
        circuits.Circuit()
        .rz(qubit, -np.pi / 2)
        .v(qubit)
        .rz(qubit, -(phi + np.pi) / 2)
        .v(qubit)
        .x(qubit)
    )


def _v1_dag(qubit, phi):
    return (
        circuits.Circuit()
        .rz(qubit, np.pi / 2)
        .v(qubit)
        .rz(qubit, -(np.pi - phi) / 2)
        .x(qubit)
        .v(qubit)
    )


def _v0_v1_direct_sum(target, ancilla, phi):
    return (
        circuits.Circuit()
        .rz(ancilla, -np.pi / 2)
        .v(ancilla)
        .rz(ancilla, -(phi + np.pi) / 2)
        .rz(target, 3 * np.pi / 2)
        .x(target)
        .ecr(target, ancilla)
    )
