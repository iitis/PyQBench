"""Module implementing direct experiment."""
from typing import Callable, Counter

from braket import circuits, devices


def count_agreeing_measurements(measurement_counts):
    return sum(
        count for bitstring, count in measurement_counts.items()
        if bitstring[0] == bitstring[1]
    )


def count_specific_measurements(measurement_counts: Counter, qubit_index: int, qubit_value: int):
    return sum(
        count for bitstring, count in measurement_counts.items()
        if int(bitstring[qubit_index]) == qubit_value
    )


def benchmark_using_controlled_unitary(
    device: devices.Device,
    target: int,
    ancilla: int,
    state_preparation: Callable[[int, int], circuits.Circuit],
    basis_change: Callable[[int], circuits.Circuit],
    controlled_unitary: Callable[[int, int], circuits.Circuit],
    num_shots_per_measurement: int,
) -> float:
    identity_circuit = (
        state_preparation(target, ancilla) +
        controlled_unitary(target, ancilla)
    )

    u_circuit = (
        state_preparation(target, ancilla) +
        basis_change(target) +
        controlled_unitary(target, ancilla)
    )

    identity_results = device.run(identity_circuit, shots=num_shots_per_measurement).result()
    u_results = device.run(u_circuit, shots=num_shots_per_measurement).result()

    return (
        count_specific_measurements(
            identity_results.measurement_counts,
            identity_results.measured_qubits.index(ancilla),
            1
        ) +
        count_specific_measurements(
            u_results.measurement_counts,
            u_results.measured_qubits.index(ancilla),
            0
        )
    ) / (2 * num_shots_per_measurement)
