from collections import Counter, defaultdict
from logging import getLogger
from typing import Any, Dict, Iterable, List, MutableMapping, Tuple, cast

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.providers.ibmq.job.exceptions import IBMQJobFailureError
from tqdm import tqdm

from ..batching import execute_in_batches
from ..common_models import Backend, BackendDescription
from ..direct_sum import asemble_direct_sum_circuits
from ..jobs import retrieve_jobs
from ..limits import get_limits
from ..postselection import assemble_postselection_circuits
from ._components import FourierComponents
from ._models import (
    BatchResult,
    FourierDiscriminationExperiment,
    FourierDiscriminationResult,
    QubitMitigationInfo,
    ResultForAngle,
    SingleResult,
)

logger = getLogger("qbench")


def _verify_results_are_async_or_fail(results: FourierDiscriminationResult) -> None:
    if not all(isinstance(entry, BatchResult) for entry in results.results):
        logger.error("Specified file seems to contain results from synchronous experiment")
        exit(1)


def _log_fourier_experiment(experiment: FourierDiscriminationExperiment) -> None:
    logger.info("Running Fourier-discrimination experiment")
    logger.info("Number of qubit-pairs: %d", len(experiment.qubits))
    logger.info("Number of phi values: %d", experiment.angles.num_steps)
    logger.info("Number of shots per circuit: %d", experiment.num_shots)
    logger.info("Probability estimation method: %s", experiment.method)
    logger.info("Gateset: %s", experiment.gateset)


def _sweep_circuits(
    backend: Backend,
    circuits_map: Dict[str, QuantumCircuit],
    phi: Parameter,
    phi_range: np.ndarray,
    num_shots: int,
) -> List[ResultForAngle]:
    """Run each circuit in the mapping with different value bound to phi and return measurements.

    Suppose circuits_map is of the form {key1: circuit1, key2: circuit2} and there are three
    different values pf phi in phi_range (say phi1, phi2, phi3). This function will:
    - bind phi=phi1 to both circuits and run them through the backend
    - bind phi=phi2 to both circuits and run them through the backend
    - bind phi=phi3 to both circuits and run them through the backend
    As the result, the list of the following form will be returned:

    [
        ResultForAngle(phi=phi1, histograms={key1: ..., key2: ...})
        ResultForAngle(phi=phi2, histograms={key1: ..., key2: ...})
        ResultForAngle(phi=phi3, histograms={key1: ..., key2: ...})
    ]

    where ... represent dictionary of measurement counts (bitstring -> count) for corresponding
    key.
    """
    results = []
    for phi_ in tqdm(phi_range, leave=False, desc="phi"):
        phi_ = float(phi_)  # or else we get into yaml serialization issues
        bound_circuits_map = {
            key: circuit.bind_parameters({phi: phi_}) for key, circuit in circuits_map.items()
        }

        _partial_result = {
            key: {"histogram": backend.run(circuit, shots=num_shots).result().get_counts()}
            for key, circuit in bound_circuits_map.items()
        }

        results.append(ResultForAngle(phi=phi_, circuits_for_angle=_partial_result))
    return results


def _execute_direct_sum_experiment(
    backend: Backend,
    target: int,
    ancilla: int,
    phi_range: np.ndarray,
    num_shots: int,
    components: FourierComponents,
) -> SingleResult:
    """Execute Fourier discrimination experiment using direct sum method.

    .. note::
       The components are provided to this function as parameter, because instances
       of FourierComponents can differ in the used gateset. For more information
       see FourierComponents class.

    :param backend: backend on which to run the experiment.
    :param target: the index of qubit to which measurement to be distinguished is applied.
    :param ancilla: the index of the ancilla qubit.
    :param phi_range: values of phi parameter in Fourier parametrized family to be used
     in the experiment.
    :param num_shots: number of shots for each circuit. Please be aware that the total
     number of shots for given phi is equal to 2 * num_shots, because two circuits are
     run for each angle.
    :param components: building blocks for the experiment.
    :return dictionary with keys "target", "ancilla" and "measurement_counts."
    """
    circuits_map = asemble_direct_sum_circuits(
        state_preparation=components.state_preparation,
        u_dag=components.u_dag,
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

    return SingleResult(target=target, ancilla=ancilla, measurement_counts=results)


def _execute_postselection_experiment(
    backend: Backend,
    target: int,
    ancilla: int,
    phi_range: np.ndarray,
    num_shots: int,
    components: FourierComponents,
) -> SingleResult:
    """Execute Fourier discrimination experiment using postselection method.

    .. note::
       The components are provided to this function as parameter, because instances
       of FourierComponents can differ in the used gateset. For more information
       see FourierComponents class.

    :param backend: backend on which to run the experiment.
    :param target: the index of qubit to which measurement to be distinguished is applied.
    :param ancilla: the index of the ancilla qubit.
    :param phi_range: values of phi parameter in Fourier parametrized family to be used
     in the experiment.
    :param num_shots: number of shots for each circuit. Please be aware that the total
     number of shots for given phi is equal to 4 * num_shots, because four circuits are
     run for each angle.
    :param components: building blocks for the experiment.
    :return dictionary with keys "target", "ancilla" and "measurement_counts."
    """
    circuits_map = assemble_postselection_circuits(
        state_preparation=components.state_preparation,
        u_dag=components.u_dag,
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

    return SingleResult(target=target, ancilla=ancilla, measurement_counts=results)


def _run_experiment_synchronously(
    backend: Backend,
    experiment: FourierDiscriminationExperiment,
    phi_range: np.ndarray,
    components: FourierComponents,
) -> List[SingleResult]:
    """Run given experiment synchronously (i.e. eagerly collect the results of each job).

    .. note:
       To learn more about inputs and outputs to this function, examine the
       FourierDiscriminationExperiment and


    :param backend: backend on which the experiment will be executed.
    :param experiment: experiment description.
    :param phi_range: values of phi to be substituted into Fourier parametrizd family circuits.\
    :param components: building blocks for the experiment.
    :return: List with result of the experiment for each pair of qubits and values of phi.
    """
    if experiment.method == "direct_sum":
        _execute = _execute_direct_sum_experiment
    else:
        _execute = _execute_postselection_experiment

    return [
        _execute(
            backend,
            pair.target,
            pair.ancilla,
            phi_range,
            experiment.num_shots,
            components,
        )
        for pair in tqdm(experiment.qubits, leave=False, desc="Qubit pair")
    ]


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
        return asemble_direct_sum_circuits(
            state_preparation=components.state_preparation,
            u_dag=components.u_dag,
            v0_v1_direct_sum_dag=components.controlled_v0_v1_dag,
            target=target,
            ancilla=ancilla,
        )

    _asemble = (
        _asemble_postselection if experiment.method == "postselection" else _asemble_direct_sum
    )

    circuit_key_pairs: Iterable[Tuple[QuantumCircuit, CircuitKey]] = [
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


def _run_experiment_asynchronously(
    backend: Backend,
    experiment: FourierDiscriminationExperiment,
    phi_range: np.ndarray,
    components: FourierComponents,
) -> List[BatchResult]:
    """Run Fourier-discrimination experiment asynchronously, producing sequence of batch jobs.

    :param backend: backend on which to run the experiment.
    :param experiment: experiment to be executed.
    :param phi_range: values of phi to be used in Fourier components.
    :param components: building blocks for the experiment.
    :return: list of objects tying job id to the specific circuit that the job comprises.
    """
    circuits, keys = _collect_circuits_and_keys(experiment, components, phi_range)

    batches = execute_in_batches(
        backend, circuits, keys, experiment.num_shots, get_limits(backend).max_circuits
    )

    return [BatchResult(job_id=batch.job.job_id(), keys=batch.keys) for batch in batches]


def run_experiment(
    experiment: FourierDiscriminationExperiment, backend_description: BackendDescription
) -> FourierDiscriminationResult:
    """Run experiment on given backend.

    :param experiment: experiment to be run.
    :param backend_description: object describing backend and possibly options that should
     be used when executing circuits.
    :return: Object describing the experiment results. For synchronous execution, this object
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

    results = (
        _run_experiment_asynchronously(backend, experiment, phi_range, components)
        if backend_description.asynchronous
        else _run_experiment_synchronously(backend, experiment, phi_range, components)
    )

    logger.info("Completed successfully")
    return FourierDiscriminationResult(
        metadata={
            "experiment": experiment,
            "backend_description": backend_description,
        },
        results=results,
    )


def fetch_statuses(async_results: FourierDiscriminationResult) -> Dict[str, int]:
    """Fetch statuses of all jobs submitted for asynchronous execution of the experiment.

    :param async_results: object describing results of asynchronous execution.
     If the result object already contains histograms, an error will be raised.
    :return: dictionary mapping status name to number of its occurrences.
    """
    _verify_results_are_async_or_fail(async_results)

    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in cast(List[BatchResult], async_results.results)]

    # logger.info(f"Fetching total of {len(job_ids_to_fetch)} jobs")
    # jobs = backend.jobs(db_filter={"id": {"inq": job_ids_to_fetch}})
    jobs = retrieve_jobs(backend, job_ids)

    return dict(Counter(job.status().name for job in jobs))


def resolve_results(async_results: FourierDiscriminationResult) -> FourierDiscriminationResult:
    """Resolve results of asynchronous execution.

    :param async_results: object describing results of asynchronous execution.
     If the result object already contains histograms, an error will be raised.
    :return: Object containing resolved results. Format of this object is the same as the one
     returned directly from a synchronous execution of FourierDiscrimination experiment. In
     particular, it contains histograms of btstrings for each circuit run durign the experiment.
    """
    _verify_results_are_async_or_fail(async_results)

    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids = [entry.job_id for entry in cast(List[BatchResult], async_results.results)]

    logger.info(f"Fetching total of {len(job_ids)} jobs")
    jobs_mapping = {job.job_id(): job for job in retrieve_jobs(backend, job_ids)}

    def mitigation_error_for_qubit(job, qubit) -> QubitMitigationInfo:
        prob_meas0_prep1 = job.properties().qubit_property(qubit)["prob_meas0_prep1"][0]
        prob_meas1_prep0 = job.properties().qubit_property(qubit)["prob_meas1_prep0"][0]
        return QubitMitigationInfo(
            prob_meas0_prep1=prob_meas0_prep1, prob_meas1_prep0=prob_meas1_prep0
        )

    def mitigation_info(job, target, ancilla):
        return (
            {
                "target": mitigation_error_for_qubit(job, target),
                "ancilla": mitigation_error_for_qubit(job, ancilla),
            }
            if "properties" in dir(job)
            else None
        )

    def _extract_result_from_job(job, target, ancilla, i):
        try:
            result = {"histogram": job.result().get_counts()[i]}
        except IBMQJobFailureError:
            result = {"histogram": "Failed IBMQJobFailureError for job {job.job_id()}"}
            logger.warning(f"IBMQJobFailureError for job {job.job_id()}")

        try:
            props = job.properties()
            result["mitigation_info"] = {
                "target": {
                    "prob_meas0_prep1": props.qubit_property(target)["prob_meas0_prep1"][0],
                    "prob_meas1_prep0": props.qubit_property(target)["prob_meas1_prep0"][0],
                },
                "ancilla": {
                    "prob_meas0_prep1": props.qubit_property(ancilla)["prob_meas0_prep1"][0],
                    "prob_meas1_prep0": props.qubit_property(ancilla)["prob_meas1_prep0"][0],
                },
            }
        except AttributeError:
            pass
        return result

    result_tuples = [
        (
            (target, ancilla, name, phi),
            _extract_result_from_job(jobs_mapping[entry.job_id], target, ancilla, i),
        )
        for entry in cast(List[BatchResult], async_results.results)
        for i, (target, ancilla, name, phi) in enumerate(entry.keys)  # type: ignore
    ]

    result_dict: MutableMapping[
        Tuple[int, int], MutableMapping[float, MutableMapping[str, Any]]
    ] = defaultdict(lambda: defaultdict(dict))

    for (target, ancilla, name, phi), counts in result_tuples:
        result_dict[(target, ancilla)][phi][name] = counts

    resolved = [
        {
            "target": target,
            "ancilla": ancilla,
            "measurement_counts": [
                {
                    "phi": phi,
                    "circuits_for_angle": {
                        name: result_for_circuit
                        for name, result_for_circuit in result_for_circ.items()
                    },
                }
                for phi, result_for_circ in result_for_phi.items()
            ],
        }
        for (target, ancilla), result_for_phi in result_dict.items()
    ]

    return FourierDiscriminationResult(metadata=async_results.metadata, results=resolved)
