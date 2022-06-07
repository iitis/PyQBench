"""Module implementing postselection experiment."""
from typing import Callable

from braket import circuits, devices


def benchmark_using_postselection(
    device: devices.Device,
    target: int,
    ancilla: int,
    state_preparation: Callable[[int, int], circuits.Circuit],
    basis_change: Callable[[int], circuits.Circuit],
    v0: Callable[[int, int], circuits.Circuit],
    v1: Callable[[int, int], circuits.Circuit],
    num_shots_per_measurement: int,
) -> float:

    pass
