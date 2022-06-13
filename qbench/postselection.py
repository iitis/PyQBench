"""Module implementing postselection experiment."""
from typing import Callable, Counter

from braket import circuits, devices

from qbench.utils import count_specific_measurements


def benchmark_using_postselection(
    device: devices.Device,
    target: int,
    ancilla: int,
    state_preparation: Callable[[int, int], circuits.Circuit],
    basis_change: Callable[[int], circuits.Circuit],
    v0: Callable[[int], circuits.Circuit],
    v1: Callable[[int], circuits.Circuit],
    num_shots_per_measurement: int,
) -> float:

    identity_circuit = state_preparation(target, ancilla) + v1(ancilla)

    u_circuit = state_preparation(target, ancilla) + basis_change(target) + v0(ancilla)

    identity_results = device.run(identity_circuit, shots=num_shots_per_measurement).result()
    u_results = device.run(u_circuit, shots=num_shots_per_measurement).result()

    return (u_results.measurement_counts["00"]) / (
        2
        * count_specific_measurements(
            u_results.measurement_counts, u_results.measured_qubits.index(ancilla), 0
        )
    ) + (identity_results.measurement_counts["11"]) / (
        2
        * count_specific_measurements(
            identity_results.measurement_counts, identity_results.measured_qubits.index(ancilla), 1
        )
    )
