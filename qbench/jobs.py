"""Implementation of utilities for interacting with jobs."""
from functools import singledispatch
from typing import Sequence

from qiskit.providers import JobV1

# from qiskit.providers.ibmq import IBMQBackend, IBMQJob


@singledispatch
def retrieve_jobs(backend, job_ids: Sequence[str]) -> Sequence[JobV1]:
    """Retrieve jobs with given ids from a backend.

    :param backend: backend which was used to run the jobs.
    :param job_ids: identifiers of jobs to obtain.
    :return: sequence of jobs. Note that it is not guaranteed that the order of this sequence
     will match order of ids in job_ids parameter.
    """
    return [backend.retrieve_job(job_id) for job_id in job_ids]


# @retrieve_jobs.register
# def _retrieve_jobs_from_ibmq(backend: IBMQBackend, job_ids: Sequence[str]) -> Sequence[IBMQJob]:
#     return backend.jobs(db_filter={"id": {"inq": job_ids}}, limit=len(job_ids))
