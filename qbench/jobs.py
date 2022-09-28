from functools import singledispatch
from typing import Sequence

from qiskit.providers import JobV1
from qiskit.providers.ibmq import IBMQBackend, IBMQJob


@singledispatch
def retrieve_jobs(backend, job_ids: Sequence[str]) -> Sequence[JobV1]:
    return [backend.retrieve_job(job_id) for job_id in job_ids]


@retrieve_jobs.register
def retrieve_jobs_from_ibmq(backend: IBMQBackend, job_ids: Sequence[str]) -> Sequence[IBMQJob]:
    return backend.jobs(db_filter={"id": {"inq": job_ids}}, limit=len(job_ids))
