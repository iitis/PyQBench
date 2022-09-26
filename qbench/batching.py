import math
from itertools import islice
from typing import Any, NamedTuple, Optional, Sequence

from qiskit import QuantumCircuit


class BatchWithKey(NamedTuple):
    circuits: Sequence[QuantumCircuit]
    keys: Sequence[Any]


def batch_circuits_with_keys(
    circuits: Sequence[QuantumCircuit], keys: Sequence[Any], max_circuits_per_batch: Optional[int]
) -> Sequence[BatchWithKey]:
    if max_circuits_per_batch is None:
        return [BatchWithKey(circuits, keys)]
    num_batches = math.ceil(len(circuits) / max_circuits_per_batch)
    circuits_it = iter(circuits)
    keys_it = iter(keys)
    return [
        BatchWithKey(
            tuple(islice(circuits_it, max_circuits_per_batch)),
            tuple(islice(keys_it, max_circuits_per_batch)),
        )
        for _ in range(num_batches)
    ]
