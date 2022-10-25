"""Implementation of various utilities for obtaining backend limits."""
from functools import singledispatch
from typing import NamedTuple, Optional

from qiskit.providers.aer import AerSimulator
from qiskit.providers.ibmq import IBMQBackend
from qiskit_braket_provider import AWSBraketBackend

from .testing import MockSimulator


class Limits(NamedTuple):
    max_circuits: Optional[int] = None
    max_shots: Optional[int] = None


@singledispatch
def get_limits(_backend):
    """Obtain limit on maximum number of circuits and shots (per circuit) in a single job.

    :param _backend: backend to obtain limit for.
    :return: namedtuple with max_circuits and max_shots, both optional integers. If any of the
     limits is set to None, it should be treated as lack of limit.
    """
    return Limits()


def _aws_device_summary(backend):
    return backend._device.properties.service.deviceDocumentation.summary


@get_limits.register
def _get_limits_for_aws_backend(backend: AWSBraketBackend):
    if backend.name.lower() == "lucy":
        return Limits(max_shots=10000)
    elif backend.name.lower().startswith("aspen"):
        return Limits(max_shots=100000)
    # Disgusting
    elif "simulator" in _aws_device_summary(backend):
        return Limits(max_shots=100000)
    else:
        raise NotImplementedError(f"Don't know how to obtain limits for device {backend.name}")


@get_limits.register
def _get_limits_for_ibmq_backend(backend: IBMQBackend):
    return Limits(
        max_shots=backend.configuration().max_shots,
        max_circuits=backend.configuration().max_experiments,
    )


@get_limits.register
def _get_limits_for_aer_simulator(backend: AerSimulator):
    return Limits(max_shots=backend.configuration().max_shots)


@get_limits.register
def _get_limits_for_mock_backend(backend: MockSimulator):
    return Limits(max_shots=backend.configuration().max_shots, max_circuits=2)
