import math
from itertools import islice
from typing import Any, NamedTuple, Optional, Sequence

from qiskit import QuantumCircuit
from qiskit.providers import JobV1


class BatchWithKey(NamedTuple):
    circuits: Sequence[QuantumCircuit]
    keys: Sequence[Any]


class BatchJob(NamedTuple):
    job: JobV1
    keys: Sequence[Any]


def batch_circuits_with_keys(
    circuits: Sequence[QuantumCircuit], keys: Sequence[Any], max_circuits_per_batch: Optional[int]
) -> Sequence[BatchWithKey]:
    if max_circuits_per_batch is None:
        # We wrap circuits in lists to indulge qiskit-braket-provider
        return [BatchWithKey(list(circuits), keys)]
    num_batches = math.ceil(len(circuits) / max_circuits_per_batch)
    circuits_it = iter(circuits)
    keys_it = iter(keys)
    return [
        BatchWithKey(
            list(islice(circuits_it, max_circuits_per_batch)),
            tuple(islice(keys_it, max_circuits_per_batch)),
        )
        for _ in range(num_batches)
    ]


def execute_in_batches(
    backend,
    circuits: Sequence[QuantumCircuit],
    keys: Sequence[Any],
    shots: int,
    batch_size: Optional[int],
    **kwargs
) -> Sequence[BatchJob]:
    batches = batch_circuits_with_keys(circuits, keys, batch_size)
    return [
        BatchJob(backend.run(batch.circuits, shots=shots, **kwargs), batch.keys)
        for batch in batches
    ]
