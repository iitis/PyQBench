"""Functions for splitting sequences of circuits into batches."""
import math
from itertools import islice
from typing import Any, Iterable, NamedTuple, Optional, Sequence

from qiskit import QuantumCircuit
from qiskit.providers import JobV1
from tqdm import tqdm

from .common_models import Backend


class BatchWithKey(NamedTuple):
    circuits: Sequence[QuantumCircuit]
    keys: Sequence[Any]


class BatchJob(NamedTuple):
    job: JobV1
    keys: Sequence[Any]


def batch_circuits_with_keys(
    circuits: Sequence[QuantumCircuit], keys: Sequence[Any], max_circuits_per_batch: Optional[int]
) -> Sequence[BatchWithKey]:
    """Split sequence of circuits into batches, preserving correspondence between circuits and keys.

    :param circuits: sequence of circuits to be split.
    :param keys: keys corresponding to given circuits (i.e. keys[i] -> circuits[i]. Keys do not have
     to be unique.
    :param max_circuits_per_batch: maximum size of the batch. All batches will be of this size,
      except possibly last batch, which can be smaller.
    :return: sequence of namedtuples with fields `circuits` and `keys`. Each such tuple, possibly
     except the last one, is of size `max_circuits_per_batch`. Correspondence between circuits and
     keys are preserved in each batch.
    """
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
    backend: Backend,
    circuits: Sequence[QuantumCircuit],
    keys: Sequence[Any],
    shots: int,
    batch_size: Optional[int],
    show_progress: bool = False,
    **kwargs,
) -> Iterable[BatchJob]:
    """Execute given sequence of circuits with corresponding keys in batches on a backend.

    :param backend: backend which will be usd for executing circuits.
    :param circuits: sequence of circuits to be executed.
    :param keys: sequence of keys corresponding to the circuits.
    :param shots: number of shots for each circuit.
    :param batch_size: number of circuits in a batch. The circuits and keys will be batches using
     batch_circuits_with_keys_function, and each batch will be executed as a single job on
     the backend.
    :param show_progress: flag determining if a tqdm progress bar should be shown (True) or not
     (False). Defaults to False.
    :return: Iterable of namedtuples with fields `job` and `keys`. Each job runs circuits
     corresponding to keys in `keys`, and the order of circuits in the job corresponds to
     order of `keys`.
    """
    batches = batch_circuits_with_keys(circuits, keys, batch_size)
    result = (
        BatchJob(backend.run(batch.circuits, shots=shots, **kwargs), batch.keys)
        for batch in batches
    )
    if show_progress:
        result = tqdm(result, total=len(batches))
    return result
