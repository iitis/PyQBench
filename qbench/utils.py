"""Module containing utilities, maybe combinatorial ones."""
from collections import Counter


def count_specific_measurements(measurement_counts: Counter, qubit_index: int, qubit_value: int):
    return sum(
        count
        for bitstring, count in measurement_counts.items()
        if int(bitstring[qubit_index]) == qubit_value
    )
