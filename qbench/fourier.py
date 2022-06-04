import numpy as np
from braket import circuits


def state_preparation_circuit(target: int = 0, ancilla: int = 1) -> circuits.Circuit:
    """Create circuit initializing system into maximally entangled state.

    :param target: Index of qubit on which von Neumann measurement will be performed.
    :param ancilla: Index of qubit on which conditional measurement will be performed.
    :return: A circuit mapping |00> to (|00> + |11>) / sqrt(2).
    """
    return circuits.Circuit().h(target).cnot(target, ancilla)


def measurement_circuit(phi: float, target: int = 0) -> circuits.Circuit:
    """Create von Neumann measurement circuit.

    :param phi: Rotation angle used in PHASE gate.
    :param target: Index of qubit on which von Neumann measurement will be performed.
    :return: A circuit H-PHASE(phi)-H
    """
    return circuits.Circuit().h(target).phaseshift(target, phi).h(target)


def v0_circuit(phi: float, target: int):
    """Circuit implementing V0 operation on given qubit.

    :param phi: rotation angle.
    :param target: qubit V0 should be applied to
    """
    return circuits.Circuit().ry(target, (phi + np.pi) / 2).rz(target, -np.pi / 2)


def v1_circuit(phi: float, target: int):
    """Circuit implementing V0 operation on given qubit.

    :param phi: rotation angle.
    :param target: qubit V1 should be applied to
    """
    return circuits.Circuit().rx(target, np.pi).ry(target, (phi + np.pi) / 2).rz(target, -np.pi / 2)
