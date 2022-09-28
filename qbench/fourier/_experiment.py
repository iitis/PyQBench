from collections import Counter, defaultdict
from logging import getLogger
from typing import Any, List, MutableMapping, Tuple, cast

import numpy as np
from qiskit.circuit import Parameter
from tqdm import tqdm

from ..batching import execute_in_batches
from ..common_models import BackendDescription
from ..direct_sum import asemble_direct_sum_circuits
from ..jobs import retrieve_jobs
from ..limits import get_limits
from ..postselection import asemble_postselection_circuits
from ._components import FourierComponents
from ._models import (
    BatchResult,
    FourierDiscriminationExperiment,
    FourierDiscriminationResult,
)

logger = getLogger("qbench")


def _verify_results_are_async_or_fail(results):
    if not all(isinstance(entry, BatchResult) for entry in results.results):
        logger.error("Specified file seems to contain results from synchronous experiment")
        exit(1)


def _log_fourier_experiment(experiment):
    logger.info("Running Fourier-discrimination experiment")
    logger.info("Number of qubit-pairs: %d", len(experiment.qubits))
    logger.info("Number of phi values: %d", experiment.angles.num_steps)
    logger.info("Number of shots per circuit: %d", experiment.num_shots)
    logger.info("Probability estimation method: %s", experiment.method)
    logger.info("Gateset: %s", experiment.gateset)


def _sweep_circuits(backend, circuits_map, phi, phi_range, num_shots):
    results = []
    for phi_ in tqdm(phi_range, leave=False, desc="phi"):
        phi_ = float(phi_)  # or else we get into yaml serialization issues
        bound_circuits_map = {
            key: circuit.bind_parameters({phi: phi_}) for key, circuit in circuits_map.items()
        }

        _partial_result = {
            key: backend.run(circuit, shots=num_shots).result().get_counts()
            for key, circuit in bound_circuits_map.items()
        }

        results.append({"phi": phi_, "histograms": _partial_result})
    return results


def _execute_direct_sum_experiment(
    target: int,
    ancilla: int,
    phi_range: np.ndarray,
    num_shots: int,
    components: FourierComponents,
    backend,
):
    circuits_map = asemble_direct_sum_circuits(
        state_preparation=components.state_preparation,
        black_box_dag=components.black_box_dag,
        v0_v1_direct_sum_dag=components.controlled_v0_v1_dag,
        target=target,
        ancilla=ancilla,
    )

    phi = components.phi

    results = _sweep_circuits(
        backend=backend,
        circuits_map=circuits_map,
        phi=phi,
        phi_range=phi_range,
        num_shots=num_shots,
    )

    return {"target": target, "ancilla": ancilla, "measurement_counts": results}


def _execute_postselection_experiment(
    target: int,
    ancilla: int,
    phi_range: np.ndarray,
    num_shots: int,
    components: FourierComponents,
    backend,
):
    circuits_map = asemble_postselection_circuits(
        state_preparation=components.state_preparation,
        black_box_dag=components.black_box_dag,
        v0_dag=components.v0_dag,
        v1_dag=components.v1_dag,
        target=target,
        ancilla=ancilla,
    )

    phi = components.phi

    results = _sweep_circuits(
        backend=backend,
        circuits_map=circuits_map,
        phi=phi,
        phi_range=phi_range,
        num_shots=num_shots,
    )

    return {"target": target, "ancilla": ancilla, "measurement_counts": results}


def _run_experiment_synchronously(
    backend,
    experiment: FourierDiscriminationExperiment,
    phi_range: np.ndarray,
    components: FourierComponents,
):
    if experiment.method == "direct_sum":
        _execute = _execute_direct_sum_experiment
    else:
        _execute = _execute_postselection_experiment

    return [
        _execute(
            pair.target,
            pair.ancilla,
            phi_range,
            experiment.num_shots,
            components,
            backend,
        )
        for pair in tqdm(experiment.qubits, leave=False, desc="Qubit pair")
    ]


def _collect_circuits_and_keys(experiment, components, phi_range):
    def _asemble_postselection(target, ancilla):
        return asemble_postselection_circuits(
            state_preparation=components.state_preparation,
            black_box_dag=components.black_box_dag,
            v0_dag=components.v0_dag,
            v1_dag=components.v1_dag,
            target=target,
            ancilla=ancilla,
        )

    def _asemble_direct_sum(target, ancilla):
        return asemble_direct_sum_circuits(
            state_preparation=components.state_preparation,
            black_box_dag=components.black_box_dag,
            v0_v1_direct_sum_dag=components.controlled_v0_v1_dag,
            target=target,
            ancilla=ancilla,
        )

    _asemble = (
        _asemble_postselection if experiment.method == "postselection" else _asemble_direct_sum
    )

    return zip(
        *[
            (
                circuit.bind_parameters({components.phi: phi}),
                (pair.target, pair.ancilla, circuit_name, float(phi)),
            )
            for pair in experiment.qubits
            for phi in phi_range
            for circuit_name, circuit in _asemble(pair.target, pair.ancilla).items()
        ]
    )


def _run_experiment_asynchronously(
    backend,
    experiment: FourierDiscriminationExperiment,
    phi_range: np.ndarray,
    components: FourierComponents,
):
    circuits, keys = _collect_circuits_and_keys(experiment, components, phi_range)

    batches = execute_in_batches(
        backend, circuits, keys, experiment.num_shots, get_limits(backend).max_circuits
    )

    return [{"job_id": batch.job.job_id(), "keys": batch.keys} for batch in batches]


def run_experiment(
    experiment: FourierDiscriminationExperiment, backend_description: BackendDescription
):
    _log_fourier_experiment(experiment)

    phi = Parameter("phi")
    components = FourierComponents(phi, gateset=experiment.gateset)
    phi_range = np.linspace(
        experiment.angles.start, experiment.angles.stop, experiment.angles.num_steps
    )

    backend = backend_description.create_backend()
    logger.info(f"Backend type: {type(backend).__name__}, backend name: {backend.name}")

    if backend_description.asynchronous:
        results = _run_experiment_asynchronously(backend, experiment, phi_range, components)
    else:
        results = _run_experiment_synchronously(backend, experiment, phi_range, components)

    logger.info("Completed successfully")
    return FourierDiscriminationResult(
        metadata={
            "experiment": experiment,
            "backend_description": backend_description,
        },
        results=results,
    )


def fetch_statuses(async_results: FourierDiscriminationResult):
    _verify_results_are_async_or_fail(async_results)

    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in cast(List[BatchResult], async_results.results)]

    # logger.info(f"Fetching total of {len(job_ids_to_fetch)} jobs")
    # jobs = backend.jobs(db_filter={"id": {"inq": job_ids_to_fetch}})
    jobs = retrieve_jobs(backend, job_ids)

    return dict(Counter(job.status().name for job in jobs))


def resolve_results(async_results: FourierDiscriminationResult):
    _verify_results_are_async_or_fail(async_results)

    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in cast(List[BatchResult], async_results.results)]

    logger.info(f"Fetching total of {len(job_ids)} jobs")
    jobs_mapping = {job.job_id(): job for job in retrieve_jobs(backend, job_ids)}

    result_pairs = [
        (key, counts)
        for entry in cast(List[BatchResult], async_results.results)
        for key, counts in zip(
            entry.keys, jobs_mapping[entry.job_id].result().get_counts()  # type: ignore
        )
    ]

    result_dict: MutableMapping[
        Tuple[int, int], MutableMapping[float, MutableMapping[str, Any]]
    ] = defaultdict(lambda: defaultdict(dict))

    for (target, ancilla, name, phi), counts in result_pairs:
        result_dict[(target, ancilla)][phi][name] = counts

    resolved = [
        {
            "target": target,
            "ancilla": ancilla,
            "measurement_counts": [
                {
                    "phi": phi,
                    "histograms": {name: counts for name, counts in result_for_circ.items()},
                }
                for phi, result_for_circ in result_for_phi.items()
            ],
        }
        for (target, ancilla), result_for_phi in result_dict.items()
    ]

    return FourierDiscriminationResult(metadata=async_results.metadata, results=resolved)
