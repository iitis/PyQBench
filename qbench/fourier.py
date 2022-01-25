from braket import circuits


def state_preparation_circuit(target: int = 0, ancilla: int = 1) -> circuits.Circuit:
    """Create circuit initializing system into maximally entangled state.

    :param target: Index of qubit on which von Neumann measurement will be performed.
    :param ancilla: Index of qubit on which conditional measurement will be performed.
    :return: A circuit mapping |00> to (|00> + |11>) / sqrt(2).
    """
    return circuits.Circuit().h(target).cnot(target, ancilla)


def measurement_circuit(phi: float, target: int = 0) -> circuits.Circuit:
    return circuits.Circuit().h(target).phaseshift(target, phi).h(target)
