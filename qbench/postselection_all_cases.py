"""Module implementing postselection experiment."""
from typing import Callable

from braket import circuits, devices


def benchmark_using_postselection_all_cases(
    device: devices.Device,
    target: int,
    ancilla: int,
    state_preparation: Callable[[int, int], circuits.Circuit],
    basis_change: Callable[[int], circuits.Circuit],
    v0: Callable[[int], circuits.Circuit],
    v1: Callable[[int], circuits.Circuit],
    num_shots_per_measurement: int,
) -> float:

    identity_circuit_v0 = state_preparation(target, ancilla) + v0(ancilla)

    identity_circuit_v1 = state_preparation(target, ancilla) + v1(ancilla)

    u_circuit_v0 = state_preparation(target, ancilla) + basis_change(target) + v0(ancilla)

    u_circuit_v1 = state_preparation(target, ancilla) + basis_change(target) + v1(ancilla)

    identity_v0_results = device.run(identity_circuit_v0, shots=num_shots_per_measurement).result()
    identity_v1_results = device.run(identity_circuit_v1, shots=num_shots_per_measurement).result()

    u_results_v0 = device.run(u_circuit_v0, shots=num_shots_per_measurement).result()
    u_results_v1 = device.run(u_circuit_v1, shots=num_shots_per_measurement).result()

    return min((
        u_results_v0.measurement_counts["00"]
        + u_results_v1.measurement_counts["10"]
        + identity_v0_results.measurement_counts["01"]
        + identity_v1_results.measurement_counts["11"]
    ) / (2 * num_shots_per_measurement),
    1
    )