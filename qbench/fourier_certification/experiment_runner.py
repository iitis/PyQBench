"""Functions for running Fourier certification experiments and interacting with the results."""

from collections import Counter, defaultdict
from logging import getLogger
from typing import Dict, Iterable, List, Optional, Tuple, Union, cast

import numpy as np
import pandas as pd
from mthree import M3Mitigation
from qiskit import QiskitError, QuantumCircuit, transpile
from qiskit.providers import JobV1
from qiskit_ibm_runtime import RuntimeJobV2
from tqdm import tqdm

from qbench.batching import BatchJob, execute_in_batches
from qbench.common_models import Backend, BackendDescription
from qbench.jobs import retrieve_jobs
from qbench.limits import get_limits
from qbench.schemes.direct_sum import (
    assemble_certification_direct_sum_circuits,
    compute_probabilities_from_certification_direct_sum_measurements,
)
from qbench.schemes.postselection import (
    assemble_circuits_certification_postselection,
    compute_probabilities_certification_postselection,
)

from ._components import certification_probability_upper_bound
from ._components.components import FourierComponents
from ._models import (
    BatchResult,
    FourierCertificationAsyncResult,
    FourierCertificationSyncResult,
    FourierExperimentSet,
    QubitMitigationInfo,
    ResultForCircuit,
    SingleResult,
)

logger = getLogger("qbench")


def _backend_name(backend) -> str:
    """Return backend name.

    This is needed because backend.name is sometimes a function (IBMQ) and sometimes a string
    (Braket).
    """
    try:
        return backend.name()
    except TypeError:
        return backend.name


def _log_fourier_experiments(experiments: FourierExperimentSet) -> None:
    """Log basic information about the set of experiments."""
    logger.info("Running set of Fourier-certification experiments")
    logger.info("Number of qubit-pairs: %d", len(experiments.qubits))
    logger.info("Number of phi values: %d", experiments.angles.num_steps)
    logger.info("Statistical significance: %s", "{0:g}".format(experiments.delta))
    logger.info("Number of shots per circuit: %d", experiments.num_shots)
    logger.info("Probability estimation method: %s", experiments.method)
    logger.info("Gateset: %s", experiments.gateset)


def _matrix_from_mitigation_info(info: QubitMitigationInfo) -> np.ndarray:
    """Construct Mthree-compatible matrix from mitigation info."""
    return np.array(
        [
            [1 - info.prob_meas1_prep0, info.prob_meas0_prep1],
            [info.prob_meas1_prep0, 1 - info.prob_meas0_prep1],
        ]
    )


def _mitigate(
    counts: Dict[str, int],
    target: int,
    ancilla: int,
    backend: Backend,
    mitigation_info: Dict[str, QubitMitigationInfo],
) -> Dict[str, float]:
    """Apply error mitigation to obtained counts.

    :param counts: histogram of measured bitstrings.
    :param target: index of the target qubit.
    :param ancilla: index of the ancilla qubit.
    :param backend: backend used for executing job.
    :param mitigation_info: dictionary with keys 'ancilla' and 'target', mapping them to objects
     holding mitigation info (prob_meas1_prep0 and prob_meas0_prep1).
    :return: dictionary with corrected quasi-distribution of bitstrings. Note that this contains
     probabilities and not counts, but nevertheless can be used for computing probabilities.
    """
    mitigator = M3Mitigation(backend)

    matrices: List[Optional[np.ndarray]] = [None for _ in range(backend.configuration().num_qubits)]
    matrices[target] = _matrix_from_mitigation_info(mitigation_info["target"])
    matrices[ancilla] = _matrix_from_mitigation_info(mitigation_info["ancilla"])

    mitigator.cals_from_matrices(matrices)
    result = mitigator.apply_correction(counts, [target, ancilla])

    # Probability distribution
    result = result.nearest_probability_distribution()
    # Wrap value in native floats, otherwise we get serialization problems
    return {key: float(value) for key, value in result.items()}


def _extract_result_from_job(
    job: JobV1 | RuntimeJobV2, target: int, ancilla: int, i: int, name: str
) -> Optional[ResultForCircuit]:
    """Extract meaningful information from job and wrap them in serializable object.

    .. note::
       Single job can comprise running multiple circuits (experiments in Qiskit terminology)
       and hence we need parameter i to identify which one we are processing right now.

    :param job: Qiskit job used for computing results.
    :param target: index of the target qubit.
    :param ancilla: index of the ancilla qubit.
    :param i: index of the experiment in job.
    :param name: name of the circuit to be used in the resulting object.
    :return: object containing results or None if the provided job was not successful.
    """
    try:
        result = {"name": name, "histogram": job.result()[i].join_data().get_counts()}
    except QiskitError:
        return None

    try:
        # We ignore some typing errors, since we are essentially accessing attributes that might
        # not exist according to their base classes.
        props = job.properties()  # type: ignore
        result["mitigation_info"] = {
            "target": QubitMitigationInfo.from_job_properties(props, target),
            "ancilla": QubitMitigationInfo.from_job_properties(props, ancilla),
        }
        result["mitigated_histogram"] = _mitigate(
            result["histogram"],
            target,
            ancilla,
            job.backend(),  # type: ignore
            result["mitigation_info"],
        )
    except AttributeError:
        pass
    return ResultForCircuit.parse_obj(result)


CircuitKey = Tuple[int, int, str, float, float]


def _collect_circuits_and_keys(
    experiments: FourierExperimentSet,
    components: FourierComponents,
) -> Tuple[Tuple[QuantumCircuit, ...], Tuple[CircuitKey, ...]]:
    """Construct all circuits needed for the experiment and assign them unique keys."""

    def _asemble_postselection(target: int, ancilla: int) -> Dict[str, QuantumCircuit]:
        return assemble_circuits_certification_postselection(
            state_preparation=components.state_preparation,
            u_dag=components.u_dag,
            v0_dag=components.v0_dag,
            v1_dag=components.v1_dag,
            target=target,
            ancilla=ancilla,
        )

    def _asemble_direct_sum(target: int, ancilla: int) -> Dict[str, QuantumCircuit]:
        return assemble_certification_direct_sum_circuits(
            state_preparation=components.state_preparation,
            u_dag=components.u_dag,
            v0_v1_direct_sum_dag=components.v0_v1_direct_sum_dag,
            target=target,
            ancilla=ancilla,
        )

    _asemble = (
        _asemble_postselection if experiments.method == "postselection" else _asemble_direct_sum
    )

    logger.info("Assembling experiments...")
    circuit_key_pairs = [
        (
            circuit.assign_parameters({components.phi: float(phi)}),
            (target, ancilla, circuit_name, float(phi)),
        )
        for (target, ancilla, phi) in tqdm(list(experiments.enumerate_experiment_labels()))
        for circuit_name, circuit in _asemble(target, ancilla).items()
    ]

    circuits, keys = zip(*circuit_key_pairs)
    return circuits, keys


def _iter_batches(batches: Iterable[BatchJob]) -> Iterable[Tuple[int, CircuitKey, JobV1]]:
    """Iterate batches in a flat manner.

    The returned iterable yields triples of the form (i, key, job) where:
    - key is the key in one of the batches
    - i is its index in the corresponding batch
    - job is a job comprising this batch
    """
    return (
        (i, key, batch.job)
        for batch in tqdm(batches, desc="Batch")
        for i, key in enumerate(tqdm(batch.keys, desc="Circuit", leave=False))
    )


# def _iter_batches(batches: Iterable[BatchJob]) -> Generator[
#     tuple[int, tuple[int, Any], JobV1 | RuntimeJob | RuntimeJobV2], None, None]:
#     """Iterate batches in a flat manner.
#
#     The returned iterable yields triples of the form (i, key, job) where:
#     - key is the key in one of the batches
#     - i is its index in the corresponding batch
#     - job is a job comprising this batch
#     """
#     for batch in tqdm(batches, desc="Batch"):
#         for i, key in enumerate(tqdm(batch.keys, desc="Circuit", leave=False)):
#             yield i, key, batch.job


def _resolve_batches(batches: Iterable[BatchJob]) -> List[SingleResult]:
    """Resolve all results from batch of jobs and wrap them in a serializable object.

    The number of returned objects can be less than what can be deduced from batches size iff
    some jobs have failed.

    :param batches: batches to be processed.
    :return: dictionary mapping triples (target, ancilla, phi, delta to a list of results for each
     circuit with that parameters.
    """
    resolved = defaultdict(list)

    num_failed = 0
    for i, key, job in _iter_batches(batches):
        target, ancilla, name, phi, delta = key
        result = _extract_result_from_job(job, target, ancilla, i, name)
        if result is None:
            num_failed += 1
        else:
            resolved[target, ancilla, phi, delta].append(result)

    if num_failed:
        logger.warning(
            "Some jobs have failed. Examine the output file to determine which data are missing."
        )

    return [
        SingleResult.parse_obj(
            {
                "target": target,
                "ancilla": ancilla,
                "phi": phi,
                "delta": delta,
                "results_per_circuit": results,
            }
        )
        for (target, ancilla, phi, delta), results in resolved.items()
    ]


def run_experiment(
    experiments: FourierExperimentSet, backend_description: BackendDescription
) -> Union[FourierCertificationSyncResult, FourierCertificationAsyncResult]:
    """Run sef ot experiments on given backend.

    :param experiments: set of experiments to be run.
    :param backend_description: object describing backend and possibly options that should
     be used when executing circuits.
    :return: Object describing experiments data. For synchronous execution, this object
     contains histogram of measurements for all the circuits. For asynchronous execution,
     this object contains mapping between job ids and the sequence of circuits run in a given job.
    """
    _log_fourier_experiments(experiments)

    backend = backend_description.create_backend()
    logger.info(f"Backend type: {type(backend).__name__}, backend name: {_backend_name(backend)}")

    if experiments.method == "postselection":
        circuit_key_pairs = []
        for target, ancilla, phi in tqdm(list(experiments.enumerate_experiment_labels())):
            components = FourierComponents(phi, experiments.delta, gateset=experiments.gateset)
            cos = assemble_circuits_certification_postselection(
                state_preparation=components.state_preparation,
                u_dag=components.u_dag,
                v0_dag=components.v0_dag,
                v1_dag=components.v1_dag,
                target=target,
                ancilla=ancilla,
            )
            for circuit_name, circuit in cos.items():
                circuit_key_pairs += [
                    (
                        transpile(circuit, backend=backend),
                        (target, ancilla, circuit_name, float(phi), experiments.delta),
                    )
                ]
    else:
        circuit_key_pairs = []
        for target, ancilla, phi in tqdm(list(experiments.enumerate_experiment_labels())):
            components = FourierComponents(phi, experiments.delta, gateset=experiments.gateset)
            cos = assemble_certification_direct_sum_circuits(
                state_preparation=components.state_preparation,
                u_dag=components.u_dag,
                v0_v1_direct_sum_dag=components.v0_v1_direct_sum_dag,
                target=target,
                ancilla=ancilla,
            )
            for circuit_name, circuit in cos.items():
                circuit_key_pairs += [
                    (
                        transpile(circuit, backend=backend),
                        (target, ancilla, circuit_name, float(phi), experiments.delta),
                    )
                ]

    logger.info("Assembling experiments...")

    circuits, keys = zip(*circuit_key_pairs)

    logger.info("Submitting jobs...")
    batches = execute_in_batches(
        backend,
        circuits,
        keys,
        experiments.num_shots,
        get_limits(backend).max_circuits,
        show_progress=True,
    )

    metadata = {
        "experiments": experiments,
        "backend_description": backend_description,
    }

    if backend_description.asynchronous:
        async_result = FourierCertificationAsyncResult.parse_obj(
            {
                "metadata": metadata,
                "data": [
                    BatchResult(job_id=batch.job.job_id(), keys=batch.keys) for batch in batches
                ],
            }
        )
        logger.info("Done")
        return async_result
    else:
        logger.info("Executing jobs...")
        sync_result = FourierCertificationSyncResult.parse_obj(
            {"metadata": metadata, "data": _resolve_batches(batches)}
        )
        logger.info("Done")
        return sync_result


def fetch_statuses(async_results: FourierCertificationAsyncResult) -> Dict[str, int]:
    """Fetch statuses of all jobs submitted for asynchronous execution of experiments.

    :param async_results: object describing data of asynchronous execution.
     If the result object already contains histograms, an error will be raised.
    :return: dictionary mapping status name to number of its occurrences.
    """
    # logger.info("Enabling account and creating backend")
    # backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in async_results.data]

    logger.info("Retrieving jobs, this might take a while...")
    jobs = retrieve_jobs(job_ids)
    logger.info("Done")

    return dict(Counter(str(job.status()) for job in jobs))


def resolve_results(
    async_results: FourierCertificationAsyncResult,
) -> FourierCertificationSyncResult:
    """Resolve data of asynchronous execution.

    :param async_results: object describing data of asynchronous execution.
     If the result object already contains histograms, an error will be raised.
    :return: Object containing resolved data. Format of this object is the same as the one
     returned directly from a synchronous execution of Fourier certification experiments. In
     particular, it contains histograms of bitstrings for each circuit run during the experiment.
    """
    # logger.info("Enabling account and creating backend")
    # backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in cast(List[BatchResult], async_results.data)]

    logger.info(f"Fetching total of {len(job_ids)} jobs")
    jobs_mapping = {job.job_id(): job for job in retrieve_jobs(job_ids)}

    batches = [BatchJob(jobs_mapping[entry.job_id], entry.keys) for entry in async_results.data]

    logger.info("Resolving results. This might take a while if mitigation info is included...")
    resolved = _resolve_batches(batches)

    result = FourierCertificationSyncResult.parse_obj(
        {"metadata": async_results.metadata, "data": resolved}
    )

    logger.info("Done")
    return result


def tabulate_results(sync_results: FourierCertificationSyncResult) -> pd.DataFrame:
    compute_probabilities = (
        compute_probabilities_certification_postselection
        if sync_results.metadata.experiments.method.lower() == "postselection"
        else compute_probabilities_from_certification_direct_sum_measurements
    )

    def _make_row(entry):
        data = [
            entry.target,
            entry.ancilla,
            entry.phi,
            entry.delta,
            certification_probability_upper_bound(entry.phi, entry.delta),
            compute_probabilities(
                **{f"{info.name}_counts": info.histogram for info in entry.results_per_circuit}
            ),
        ]
        try:
            data.append(
                compute_probabilities(
                    **{
                        f"{info.name}_counts": info.mitigated_histogram
                        for info in entry.results_per_circuit
                    }
                ),
            )
        except AttributeError:
            pass  # totally acceptable, not all results have mitigation info
        return data

    logger.info("Tabulating results...")
    rows = [_make_row(entry) for entry in tqdm(sync_results.data)]

    # We assume that either all circuits have mitigation info, or none of them has
    columns = (
        ["target", "ancilla", "phi", "delta", "ideal_prob", "cert_prob"]
        if len(rows[0]) == 6
        else ["target", "ancilla", "phi", "delta", "ideal_prob", "cert_prob", "mit_cert_prob"]
    )

    result = pd.DataFrame(data=rows, columns=columns)

    # fig, ax = plt.subplots()
    # ax.plot(phis, theoretical_probs, color="red", label="theoretical_predictions")
    # ax.plot(phis, actual_probs, color="blue", label="actual results")
    # ax.legend()

    # plt.savefig(PATH + f'direct_sum_{backend}_{NUM_SHOTS_PER_MEASUREMENT}.png')

    logger.info("Done")
    return result
