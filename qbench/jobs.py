from functools import singledispatch

from qiskit.providers.ibmq import IBMQJob
from qiskit_braket_provider import AWSBraketJob

from qbench.common_models import AWSJobDescription, IBMQJobDescription


@singledispatch
def create_job_description(job):
    pass


@create_job_description.register
def create_job_description_for_ibmq(job: IBMQJob) -> IBMQJobDescription:
    return IBMQJobDescription(ibmq_job_id=job.job_id())


@create_job_description.register
def create_job_description_for_aws(job: AWSBraketJob) -> AWSJobDescription:
    return AWSJobDescription(aws_job_id=job.job_id())
