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
