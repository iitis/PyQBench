import os

import pytest
from qiskit import IBMQ
from qiskit.providers.aer import AerSimulator
from qiskit_braket_provider import AWSBraketProvider, BraketLocalBackend

from qbench.limits import get_limits
from qbench.testing import MockSimulator

IBMQ_TOKEN = os.getenv("IBMQ_TOKEN")


@pytest.fixture(scope="module")
def ibmq_provider():
    return IBMQ.get_provider() if IBMQ.active_account() else IBMQ.enable_account(IBMQ_TOKEN)


@pytest.fixture(scope="module")
def aws_provider():
    return AWSBraketProvider()


@pytest.mark.parametrize("name", ["braket_sv", "braket_dm", "default"])
def test_all_limits_of_braket_local_backend_are_undefined(name):
    backend = BraketLocalBackend(name)
    limits = get_limits(backend)

    assert limits.max_circuits is None
    assert limits.max_shots is None


def test_lucy_has_no_circuit_limit_and_10k_limit_of_shots(aws_provider):
    lucy = aws_provider.get_backend("Lucy")
    limits = get_limits(lucy)

    assert limits.max_shots == 10000
    assert limits.max_circuits is None


def test_aspen_has_no_circuit_limit_and_100k_limit_of_shots(aws_provider):
    aspen = aws_provider.get_backend("Aspen-M-2")
    limits = get_limits(aspen)

    assert limits.max_shots == 100000
    assert limits.max_circuits is None


def test_obtaining_limits_of_unknown_aws_device_raises_an_error(aws_provider):
    backend = aws_provider.get_backend("Aspen-M-2")
    backend.name = "unknown_backend"

    with pytest.raises(NotImplementedError):
        get_limits(backend)


@pytest.mark.parametrize("name", ["SV1", "dm1", "TN1"])
def test_aws_simulators_have_no_circuit_limit_and_100k_limit_of_shots(aws_provider, name):
    simulator = aws_provider.get_backend(name)
    limits = get_limits(simulator)

    assert limits.max_shots == 100000
    assert limits.max_circuits is None


@pytest.mark.parametrize("name", ["ibmq_qasm_simulator", "ibmq_quito"])
@pytest.mark.skipif(IBMQ_TOKEN is None, reason="IBMQ Token is not configured")
def test_limits_from_ibmq_devices_are_taken_from_device_configuration(ibmq_provider, name):
    backend = ibmq_provider.get_backend(name)
    limits = get_limits(backend)

    assert limits.max_shots == backend.configuration().max_shots
    assert limits.max_circuits == backend.configuration().max_experiments


def test_aer_simulator_has_undefined_circuit_limits_and_shots_limit_as_in_configuration():
    simulator = AerSimulator()
    limits = get_limits(simulator)

    assert limits.max_circuits is None
    assert limits.max_shots == simulator.configuration().max_shots


def test_mock_simulator_has_circuit_limit_of_2_and_shots_limit_as_in_configuration():
    simulator = MockSimulator()
    limits = get_limits(simulator)

    assert limits.max_circuits == 2
    assert limits.max_shots == simulator.configuration().max_shots
