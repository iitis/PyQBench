import numpy as np
from tqdm import tqdm

from ..backend_models import IbMQJObDescription
from ..direct_sum import asemble_direct_sum_circuits
from ._components import FourierComponents


def _wrap_result_ibmq_job(job):
    return IbMQJObDescription(ibmq_job_id=job.job_id())


def _wrap_result_counts(job):
    return job.result().get_counts()


_EXECUTION_MODE_TO_RESULT_WRAPPER = {
    True: _wrap_result_ibmq_job,  # async=True
    False: _wrap_result_counts,  # async=False
}


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
    phi = u_circuit.parameters[0]

    wrap_result = _EXECUTION_MODE_TO_RESULT_WRAPPER[asynchronous]

    results = []
    for phi_ in tqdm(phi_range, leave=False, desc="phi"):
        phi_ = float(phi_)  # or else we get into yaml serialization issues
        bound_identity_circuit = identity_circuit.bind_parameters({phi: phi_})
        bound_u_circuit = identity_circuit.bind_parameters({phi: phi_})

        _partial_result = {
            "u": wrap_result(backend.run(bound_identity_circuit, shots=num_shots)),
            "id": wrap_result(backend.run(bound_u_circuit, shots=num_shots)),
        }

        results.append({"phi": phi_, "histograms": _partial_result})

    return {"target": target, "ancilla": ancilla, "measurement_counts": results}
