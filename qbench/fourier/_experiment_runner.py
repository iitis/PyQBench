from collections import Counter, defaultdict
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple, Union, cast

import numpy as np
import pandas as pd
from qiskit import QiskitError, QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.providers import JobV1

from ..batching import BatchJob, execute_in_batches
from ..common_models import BackendDescription
from ..direct_sum import (
    assemble_direct_sum_circuits,
    compute_probabilities_from_direct_sum_measurements,
)
from ..jobs import retrieve_jobs
from ..limits import get_limits
from ..postselection import (
    assemble_postselection_circuits,
    compute_probabilities_from_postselection_measurements,
)
from ._components import FourierComponents
from ._models import (
    BatchResult,
    FourierDiscriminationAsyncResult,
    FourierDiscriminationExperiment,
    FourierDiscriminationSyncResult,
    QubitMitigationInfo,
    ResultForCircuit,
    SingleResult,
)

logger = getLogger("qbench")


def _log_fourier_experiment(experiment: FourierDiscriminationExperiment) -> None:
    logger.info("Running Fourier-discrimination experiment")
    logger.info("Number of qubit-pairs: %d", len(experiment.qubits))
    logger.info("Number of phi values: %d", experiment.angles.num_steps)
    logger.info("Number of shots per circuit: %d", experiment.num_shots)
    logger.info("Probability estimation method: %s", experiment.method)
    logger.info("Gateset: %s", experiment.gateset)


def _extract_result_from_job(
    job: JobV1, target: int, ancilla: int, i: int, name: str
) -> Optional[ResultForCircuit]:
    try:
        result = {"name": name, "histogram": job.result().get_counts()[i]}
    except QiskitError:
        return None
    try:
        props = job.properties()
        result["mitigation_info"] = {
            "target": QubitMitigationInfo.from_job_properties(props, target),
            "ancilla": QubitMitigationInfo.from_job_properties(props, ancilla),
        }
    except AttributeError:
        pass
    return ResultForCircuit.parse_obj(result)


CircuitKey = Tuple[int, int, str, float]


def _collect_circuits_and_keys(
    experiment: FourierDiscriminationExperiment,
    components: FourierComponents,
    phi_range: np.ndarray,
) -> Tuple[Tuple[QuantumCircuit, ...], Tuple[CircuitKey, ...]]:
    """Construct all circuits needed for the experiment and assign them unique keys."""

    def _asemble_postselection(target: int, ancilla: int) -> Dict[str, QuantumCircuit]:
        return assemble_postselection_circuits(
            state_preparation=components.state_preparation,
            u_dag=components.u_dag,
            v0_dag=components.v0_dag,
            v1_dag=components.v1_dag,
            target=target,
            ancilla=ancilla,
        )

    def _asemble_direct_sum(target: int, ancilla: int) -> Dict[str, QuantumCircuit]:
        return assemble_direct_sum_circuits(
            state_preparation=components.state_preparation,
            u_dag=components.u_dag,
            v0_v1_direct_sum_dag=components.controlled_v0_v1_dag,
            target=target,
            ancilla=ancilla,
        )

    _asemble = (
        _asemble_postselection if experiment.method == "postselection" else _asemble_direct_sum
    )

    circuit_key_pairs = [
        (
            circuit.bind_parameters({components.phi: phi}),
            (pair.target, pair.ancilla, circuit_name, float(phi)),
        )
        for pair in experiment.qubits
        for phi in phi_range
        for circuit_name, circuit in _asemble(pair.target, pair.ancilla).items()
    ]

    # Cast is needed, because mypy cannot correctly infer types in zip
    return cast(
        Tuple[Tuple[QuantumCircuit, ...], Tuple[CircuitKey, ...]], tuple(zip(*circuit_key_pairs))
    )


def _resolve_batches(batches: Iterable[BatchJob]) -> List[SingleResult]:
    resolved = defaultdict(list)

    num_failed = 0
    for batch in batches:
        for i, key in enumerate(batch.keys):
            target, ancilla, name, phi = key
            result = _extract_result_from_job(batch.job, target, ancilla, i, name)
            if result is None:
                num_failed += 1
            else:
                resolved[target, ancilla, phi].append(result)

    if num_failed:
        logger.warning(
            "Some jobs have failed. Examine the output file to determine which data are missing."
        )

    return [
        SingleResult.parse_obj(
            {"target": target, "ancilla": ancilla, "phi": phi, "results_per_circuit": results}
        )
        for (target, ancilla, phi), results in resolved.items()
    ]


def run_experiment(
    experiment: FourierDiscriminationExperiment, backend_description: BackendDescription
) -> Union[FourierDiscriminationSyncResult, FourierDiscriminationAsyncResult]:
    """Run experiment on given backend.

    :param experiment: experiment to be run.
    :param backend_description: object describing backend and possibly options that should
     be used when executing circuits.
    :return: Object describing the experiment data. For synchronous execution, this object
     contains histogram of measurements for all the circuits. For asynchronous execution,
     this object contains mapping between job ids and the sequence of circuits run in a given job.
    """
    _log_fourier_experiment(experiment)

    phi = Parameter("phi")
    components = FourierComponents(phi, gateset=experiment.gateset)
    phi_range = np.linspace(
        experiment.angles.start, experiment.angles.stop, experiment.angles.num_steps
    )

    backend = backend_description.create_backend()
    logger.info(f"Backend type: {type(backend).__name__}, backend name: {backend.name}")

    circuits, keys = _collect_circuits_and_keys(experiment, components, phi_range)

    batches = execute_in_batches(
        backend, circuits, keys, experiment.num_shots, get_limits(backend).max_circuits
    )

    metadata = {
        "experiment": experiment,
        "backend_description": backend_description,
    }

    if backend_description.asynchronous:
        return FourierDiscriminationAsyncResult.parse_obj(
            {
                "metadata": metadata,
                "data": [
                    BatchResult(job_id=batch.job.job_id(), keys=batch.keys) for batch in batches
                ],
            }
        )
    else:
        return FourierDiscriminationSyncResult.parse_obj(
            {"metadata": metadata, "data": _resolve_batches(batches)}
        )


def fetch_statuses(async_results: FourierDiscriminationAsyncResult) -> Dict[str, int]:
    """Fetch statuses of all jobs submitted for asynchronous execution of the experiment.

    :param async_results: object describing data of asynchronous execution.
     If the result object already contains histograms, an error will be raised.
    :return: dictionary mapping status name to number of its occurrences.
    """
    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in async_results.data]

    # logger.info(f"Fetching total of {len(job_ids_to_fetch)} jobs")
    # jobs = backend.jobs(db_filter={"id": {"inq": job_ids_to_fetch}})
    jobs = retrieve_jobs(backend, job_ids)

    return dict(Counter(job.status().name for job in jobs))


def resolve_results(
    async_results: FourierDiscriminationAsyncResult,
) -> FourierDiscriminationSyncResult:
    """Resolve data of asynchronous execution.

    :param async_results: object describing data of asynchronous execution.
     If the result object already contains histograms, an error will be raised.
    :return: Object containing resolved data. Format of this object is the same as the one
     returned directly from a synchronous execution of FourierDiscrimination experiment. In
     particular, it contains histograms of btstrings for each circuit run durign the experiment.
    """
    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in cast(List[BatchResult], async_results.data)]

    logger.info(f"Fetching total of {len(job_ids)} jobs")
    jobs_mapping = {job.job_id(): job for job in retrieve_jobs(backend, job_ids)}

    batches = [BatchJob(jobs_mapping[entry.job_id], entry.keys) for entry in async_results.data]

    resolved = _resolve_batches(batches)

    return FourierDiscriminationSyncResult.parse_obj(
        {"metadata": async_results.metadata, "data": resolved}
    )


def tabulate_results(sync_results: FourierDiscriminationSyncResult) -> pd.DataFrame:
    compute_probabilities = (
        compute_probabilities_from_postselection_measurements
        if sync_results.metadata.experiment.method.lower() == "postselection"
        else compute_probabilities_from_direct_sum_measurements
    )

    rows = [
        (
            entry.target,
            entry.ancilla,
            entry.phi,
            compute_probabilities(
                **{f"{info.name}_counts": info.histogram for info in entry.results_per_circuit}
            ),  # type: ignore
        )
        for entry in sync_results.data
    ]

    columns = ["target", "ancilla", "phi", "disc_prob"]

    return pd.DataFrame(data=rows, columns=columns)
