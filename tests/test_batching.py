import pytest
from qiskit.circuit.random import random_circuit

from qbench.batching import batch_circuits_with_keys


@pytest.fixture()
def circuits():
    return [random_circuit(2, 2, seed=1234) for _ in range(5)]


@pytest.fixture()
def keys():
    return [
        ("u_v0", 0, 1, 0.0),
        ("id_v1", 0, 1, 0.0),
        ("u_v0", 1, 2, 0.5),
        ("u_v1", 1, 2, 0.1),
        ("id_v1", 1, 4, 0.2),
    ]


class TestBatchingCircuits:
    @pytest.mark.parametrize(
        "num_circuits, max_circuits_per_batch, expected_num_batches, expected_batches_sizes",
        [(5, 2, 3, (2, 2, 1)), (10, 3, 4, (3, 3, 3, 1)), (8, 4, 2, (4, 4)), (10, None, 1, (10,))],
    )
    def test_number_of_batches_and_their_size_is_correct(
        self, num_circuits, max_circuits_per_batch, expected_num_batches, expected_batches_sizes
    ):
        circuits = [random_circuit(2, depth=3, seed=1234) for _ in range(num_circuits)]
        keys = list(range(num_circuits))

        batches = batch_circuits_with_keys(circuits, keys, max_circuits_per_batch)

        assert len(batches) == expected_num_batches
        assert all(
            len(batch.circuits) == len(batch.keys) == size
            for batch, size in zip(batches, expected_batches_sizes)
        )

    @pytest.mark.parametrize(
        "num_circuits, max_circuits_per_batch", [(5, 2), (10, 3), (8, 4), (10, None)]
    )
    def test_correspondence_between_keys_and_circuits_is_preserved(
        self, num_circuits, max_circuits_per_batch
    ):
        circuits = [random_circuit(2, depth=3, seed=1234) for _ in range(num_circuits)]
        keys = list(range(num_circuits))
        expected_keys_to_circuits = dict(zip(keys, circuits))

        batches = batch_circuits_with_keys(circuits, keys, max_circuits_per_batch)

        keys_to_circuits = {
            key: circuit for batch in batches for key, circuit in zip(batch.keys, batch.circuits)
        }

        assert expected_keys_to_circuits == keys_to_circuits
