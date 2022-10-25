import pytest
from qiskit import QuantumCircuit
from qiskit.providers.aer import AerSimulator

from qbench.batching import batch_circuits_with_keys, execute_in_batches


def _dummy_circuit(n):
    circuit = QuantumCircuit(n)
    circuit.h(0)
    circuit.measure_all()

    return circuit


class TestBatchingCircuits:
    @pytest.mark.parametrize(
        "num_circuits, max_circuits_per_batch, expected_num_batches, expected_batches_sizes",
        [(5, 2, 3, (2, 2, 1)), (10, 3, 4, (3, 3, 3, 1)), (8, 4, 2, (4, 4)), (10, None, 1, (10,))],
    )
    def test_number_of_batches_and_their_size_is_correct(
        self, num_circuits, max_circuits_per_batch, expected_num_batches, expected_batches_sizes
    ):
        circuits = [_dummy_circuit(2) for _ in range(num_circuits)]
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
        circuits = [_dummy_circuit(2) for _ in range(num_circuits)]
        keys = list(range(num_circuits))
        expected_keys_to_circuits = dict(zip(keys, circuits))

        batches = batch_circuits_with_keys(circuits, keys, max_circuits_per_batch)

        keys_to_circuits = {
            key: circuit for batch in batches for key, circuit in zip(batch.keys, batch.circuits)
        }

        assert expected_keys_to_circuits == keys_to_circuits


class TestRunningCircuitInBatches:
    def test_keys_in_batch_match_submitted_circuits(self):
        backend = AerSimulator()
        keys = range(2, 10)
        circuits = [_dummy_circuit(n) for n in keys]

        batch_jobs = execute_in_batches(backend, circuits, keys, shots=100, batch_size=2)

        # Example is constructed in such a way that each key == number of qubits in the
        # corresponding circuit
        def _circuit_matches_key(batch_job):
            return all(
                len(bitstring) == key
                for key, counts in zip(batch_job.keys, batch_job.job.result().get_counts())
                for bitstring in counts.keys()
            )

        assert all(_circuit_matches_key(batch_job) for batch_job in batch_jobs)

    def test_all_keys_and_circuits_are_submitted_to_backend(self):
        backend = AerSimulator()
        keys = range(2, 10)
        circuits = [_dummy_circuit(n) for n in keys]

        batch_jobs = list(execute_in_batches(backend, circuits, keys, shots=100, batch_size=2))

        def _n_qubits_from_counts(counts):
            return next(iter(len(key) for key in counts))

        submitted_keys = [key for job in batch_jobs for key in job.keys]

        submitted_circuits_n_qubits = [
            _n_qubits_from_counts(counts)
            for batch in batch_jobs
            for counts in batch.job.result().get_counts()
        ]

        expected_n_qubits = [circuit.num_qubits for circuit in circuits]

        assert len(submitted_keys) == len(keys) and set(submitted_keys) == set(keys)
        assert len(submitted_circuits_n_qubits) == len(expected_n_qubits) and set(
            submitted_circuits_n_qubits
        ) == set(expected_n_qubits)
