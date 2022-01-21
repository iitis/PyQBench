from braket import circuits


def state_preparation_circuit(target: int = 0, ancilla: int = 1) -> circuits.Circuit:
    return circuits.Circuit().h(target).cnot(target, ancilla)
