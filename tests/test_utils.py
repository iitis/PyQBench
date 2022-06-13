from collections import Counter

import pytest

from qbench.utils import count_specific_measurements


@pytest.mark.parametrize(
    "measurement_counts, qubit_index, qubit_value, expected_count",
    [
        (Counter({"11": 30, "01": 20, "00": 5}), 0, 0, 25),
        (Counter({"01": 20, "00": 5}), 0, 1, 0),
        (Counter({"01": 2, "11": 5}), 1, 1, 7),
    ],
)
def test_counting_specific_measurements(
    measurement_counts, qubit_index, qubit_value, expected_count
):
    assert (
        count_specific_measurements(measurement_counts, qubit_index, qubit_value) == expected_count
    )
