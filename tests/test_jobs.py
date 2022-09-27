from qiskit import QuantumCircuit
from qiskit.providers.ibmq import IBMQJob
from qiskit.providers.ibmq.apiconstants import ApiJobStatus
from qiskit_braket_provider import BraketLocalBackend

from qbench.common_models import AWSJobDescription, IBMQJobDescription
from qbench.jobs import create_job_description


class TestCreatingJobDescription:
    def test_job_description_for_ibmq_is_of_correct_type_and_has_correct_id(self):
        job = IBMQJob(
            job_id="some-ibmq-id",
            backend=None,
            api_client=None,
            creation_date="2022-09-09",
            status=ApiJobStatus.QUEUED,
        )

        description = create_job_description(job)

        assert isinstance(description, IBMQJobDescription)
        assert description.ibmq_job_id == "some-ibmq-id"

    def test_job_description_for_braket_is_of_correct_type_and_has_correct_id(self):
        backend = BraketLocalBackend()
        circuit = QuantumCircuit(1)
        circuit.x(0)
        circuit.measure_all()
        job = backend.run(circuit, shots=10)

        description = create_job_description(job)

        assert isinstance(description, AWSJobDescription)
        assert description.aws_job_id == job.job_id()
