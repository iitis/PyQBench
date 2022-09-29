import os

import pytest
from qiskit import QuantumCircuit

from qbench.common_models import IBMQBackendDescription
from qbench.jobs import retrieve_jobs

IBMQ_TOKEN = os.getenv("IBMQ_TOKEN")


@pytest.mark.skipif(IBMQ_TOKEN is None, reason="IBMQ Token is not configured")
def test_ibmq_backend_is_correctly_created_from_description():
    description = IBMQBackendDescription.parse_obj(
        {"name": "ibmq_quito", "asynchronous": True, "provider": {"hub": "ibm-q"}}
    )

    backend = description.create_backend()
    assert backend.name() == "ibmq_quito"

    # We create backend a second time, just to make sure we don't run into "account already enabled"
    # issue
    backend = description.create_backend()
    assert backend.name() == "ibmq_quito"


@pytest.mark.skipif(IBMQ_TOKEN is None, reason="IBMQ Token is not configured")
def test_ibmq_jobs_can_be_retrieved_using_retrieve_job():
    description = IBMQBackendDescription.parse_obj(
        {"name": "ibmq_quito", "asynchronous": True, "provider": {"hub": "ibm-q"}}
    )

    backend = description.create_backend()

    circuit = QuantumCircuit(2)
    circuit.cx(0, 1)
    circuit.measure_all()

    job_1 = backend.run(circuit, shots=10)
    job_2 = backend.run(circuit, shots=10)

    ids_to_retrieve = [job_1.job_id(), job_2.job_id()]

    retrieved_jobs = retrieve_jobs(backend, ids_to_retrieve)

    assert len(retrieved_jobs) == 2
    assert set([job.job_id() for job in retrieved_jobs]) == {job_1.job_id(), job_2.job_id()}

    job_1.cancel()
    job_2.cancel()
