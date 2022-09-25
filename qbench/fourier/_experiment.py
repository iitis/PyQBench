from collections import Counter
from logging import getLogger
from typing import cast

import numpy as np
from qiskit.circuit import Parameter
from tqdm import tqdm

from ..common_models import BackendDescription, IBMQJobDescription
from ..direct_sum import asemble_direct_sum_circuits
from ..postselection import asemble_postselection_circuits
from ._components import FourierComponents
from ._models import FourierDiscriminationExperiment, FourierDiscriminationResult

logger = getLogger("qbench")


def _wrap_result_ibmq_job(job):
    return IBMQJobDescription(ibmq_job_id=job.job_id())


def _wrap_result_counts(job):
    return job.result().get_counts()


_EXECUTION_MODE_TO_RESULT_WRAPPER = {
    True: _wrap_result_ibmq_job,  # async=True
    False: _wrap_result_counts,  # async=False
}


def _verify_results_are_async_or_fail(results):
    if not results.metadata.backend_description.asynchronous:
        logger.error("Specified file seems to contain results from synchronous experiment")
        exit(1)


def _collect_jobs_from_results(async_results):
    return [
        cast(IBMQJobDescription, job_description).ibmq_job_id
        for entry in async_results.results
        for measurements in entry.measurement_counts
        for job_description in measurements.histograms.values()
    ]


def _log_fourier_experiment(experiment):
    logger.info("Running Fourier-discrimination experiment")
    logger.info("Number of qubit-pairs: %d", len(experiment.qubits))
    logger.info("Number of phi values: %d", experiment.angles.num_steps)
    logger.info("Number of shots per circuit: %d", experiment.num_shots)
    logger.info("Probability estimation method: %s", experiment.method)
    logger.info("Gateset: %s", experiment.gateset)


def _sweep_circuits(backend, circuits_map, phi, phi_range, num_shots, wrap_result):
    results = []
    for phi_ in tqdm(phi_range, leave=False, desc="phi"):
        phi_ = float(phi_)  # or else we get into yaml serialization issues
        bound_circuits_map = {
            key: circuit.bind_parameters({phi: phi_}) for key, circuit in circuits_map.items()
        }

        _partial_result = {
            key: wrap_result(backend.run(circuit, shots=num_shots))
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
    asynchronous: bool,
):
    identity_circuit, u_circuit = asemble_direct_sum_circuits(
        state_preparation=components.state_preparation,
        black_box_dag=components.black_box_dag,
        v0_v1_direct_sum_dag=components.controlled_v0_v1_dag,
        target=target,
        ancilla=ancilla,
    )

    circuits_map = {"U": u_circuit, "id": identity_circuit}
    phi = u_circuit.parameters[0]

    wrap_result = _EXECUTION_MODE_TO_RESULT_WRAPPER[asynchronous]

    results = _sweep_circuits(
        backend=backend,
        circuits_map=circuits_map,
        phi=phi,
        phi_range=phi_range,
        num_shots=num_shots,
        wrap_result=wrap_result,
    )

    return {"target": target, "ancilla": ancilla, "measurement_counts": results}


def _execute_postselection_experiment(
    target: int,
    ancilla: int,
    phi_range: np.ndarray,
    num_shots: int,
    components: FourierComponents,
    backend,
    asynchronous: bool,
):
    id_v0_circuit, id_v1_circuit, u_v0_circuit, u_v1_circuit = asemble_postselection_circuits(
        state_preparation=components.state_preparation,
        black_box_dag=components.black_box_dag,
        v0_dag=components.v0_dag,
        v1_dag=components.v1_dag,
        target=target,
        ancilla=ancilla,
    )

    circuits_map = {
        "id_v0": id_v0_circuit,
        "id_v1": id_v1_circuit,
        "u_v0_circuit": u_v0_circuit,
        "u_v1_circuit": u_v1_circuit,
    }

    phi = id_v0_circuit.parameters[0]

    wrap_result = _EXECUTION_MODE_TO_RESULT_WRAPPER[asynchronous]

    results = _sweep_circuits(
        backend=backend,
        circuits_map=circuits_map,
        phi=phi,
        phi_range=phi_range,
        num_shots=num_shots,
        wrap_result=wrap_result,
    )

    return {"target": target, "ancilla": ancilla, "measurement_counts": results}


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

    if experiment.method == "direct_sum":
        _execute = _execute_direct_sum_experiment
    else:
        _execute = _execute_postselection_experiment

    all_results = [
        _execute(
            pair.target,
            pair.ancilla,
            phi_range,
            experiment.num_shots,
            components,
            backend,
            backend_description.asynchronous,
        )
        for pair in tqdm(experiment.qubits, leave=False, desc="Qubit pair")
    ]

    logger.info("Completed successfully")
    return FourierDiscriminationResult(
        metadata={
            "experiment": experiment,
            "backend_description": backend_description,
        },
        results=all_results,
    )


def fetch_statuses(async_results: FourierDiscriminationResult):
    _verify_results_are_async_or_fail(async_results)

    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids_to_fetch = _collect_jobs_from_results(async_results)

    logger.info(f"Fetching total of {len(job_ids_to_fetch)} jobs")
    jobs = backend.jobs(db_filter={"id": {"inq": job_ids_to_fetch}})

    return dict(Counter(job.status().name for job in jobs))


def resolve_results(async_results: FourierDiscriminationResult):
    _verify_results_are_async_or_fail(async_results)

    logger.info("Enabling account and creating backend")
    backend = async_results.metadata.backend_description.create_backend()

    logger.info("Reading jobs ids from the input file")
    job_ids_to_fetch = _collect_jobs_from_results(async_results)

    logger.info(f"Fetching total of {len(job_ids_to_fetch)} jobs")
    jobs_mapping = {
        job.job_id(): job for job in backend.jobs(db_filter={"id": {"inq": job_ids_to_fetch}})
    }

    def _resolve_measurement_counts(counts):
        return {
            "phi": counts.phi,
            "histograms": {
                key: jobs_mapping[cast(IBMQJobDescription, value.ibmq_job_id)].result().get_counts()
                for key, value in counts.histograms.items()
            },
        }

    resolved = [
        {
            "target": entry.target,
            "ancilla": entry.ancilla,
            "measurement_counts": [
                _resolve_measurement_counts(counts) for counts in entry.measurement_counts
            ],
        }
        for entry in async_results.results
    ]
    return FourierDiscriminationResult(metadata=async_results.metadata, results=resolved)
