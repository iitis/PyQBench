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


def global_phase_circuit(phi: float, target: int):
    """Create a circuit applying global phase factor to target qubit.

    The corresponding unitary is of the form diag(exp(i * phi), exp(i * phi)).

    :param phi: Rotation angle defining phase.
    :param target: Index of qubit global phase should be applied to.
    :return: A circuit comprising gates shifting global phase of the target qubit.
    """
    return circuits.Circuit().phaseshift(target, 2 * phi).rz(target, -2 * phi)


def v0_circuit(phi: float, target: int, preserve_global_phase=True):
    """Circuit implementing V0 operation on given qubit.

    :param phi: rotation angle.
    :param target: qubit V0 should be applied to
    :param preserve_global_phase: whether the decomposition should preserve global phase.
     This should matter only if V0 is used to construct a controlled gate, and is irrelevant
     otherwise. To be on the safe side, the default is `True`. Note that including global phase
     adds two more gates to the circuit.
    """
    circuit = (
        global_phase_circuit(np.pi / 4, target) if preserve_global_phase else circuits.Circuit()
    )
    return circuit.ry(target, (phi + np.pi) / 2).rz(target, -np.pi / 2)


def v1_circuit(phi: float, target: int, preserve_global_phase=True):
    """Circuit implementing V0 operation on given qubit.

    :param phi: rotation angle.
    :param target: qubit V1 should be applied to
    :param preserve_global_phase: whether the decomposition should preserve global phase.
     This should matter only if V1 is used to construct a controlled gate, and is irrelevant
     otherwise. To be on the safe side, the default is `True`. Note that including global phase
     adds two more gates to the circuit.
    """
    circuit = (
        global_phase_circuit(3 * np.pi / 4, target) if preserve_global_phase else circuits.Circuit()
    )
    return circuit.rx(target, np.pi).ry(target, (phi + np.pi) / 2).rz(target, -np.pi / 2)
