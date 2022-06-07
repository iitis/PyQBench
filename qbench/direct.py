"""Module implementing direct experiment."""
from typing import Callable

from braket import circuits, devices


def benchmark_using_controlled_unitary(
    device: devices.Device,
    target: int,
    ancilla: int,
    state_preparation: Callable[[int, int], circuits.Circuit],
    controlled_unitary: Callable[[int, int], circuits.Circuit],
) -> float:
    pass
