import os

import pytest
from qiskit import IBMQ, QuantumCircuit
from qiskit.circuit import Instruction

from qbench.fourier import FourierComponents


def _assert_can_be_run(backend, instruction: Instruction):
    circuit = QuantumCircuit(instruction.num_qubits)
    circuit.append(instruction, list(range(instruction.num_qubits)))
    circuit.measure_all()
    resp = backend.run(circuit.decompose(), shots=10)
    assert resp.result()
    assert sum(resp.result().get_counts().values()) == 10


@pytest.fixture(scope="module")
def ibmq():
    token = os.getenv("IBMQ_TOKEN")
    IBMQ.enable_account(token)
    provider = IBMQ.get_provider()
    return provider.get_backend("ibmq_manila")


@pytest.fixture()
def circuits():
    # We only use one value of phi that is not a characteristic multiple of pi/2
    # It should be enough to verify that circuits can be run, while not incurring
    # too big costs when tests are run.
    return FourierComponents(phi=0.1, gateset="ibmq")


@pytest.mark.skipif("not config.getoption('ibmq')")
class TestIBMQDeviceCanRunDecomposedCircuitsInVerbatimMode:
    def test_u_dag_can_be_run(self, ibmq, circuits):
        _assert_can_be_run(ibmq, circuits.u_dag)

    def test_v0_dag_can_be_run(self, ibmq, circuits):
        _assert_can_be_run(ibmq, circuits.v0_dag)

    def test_v1_dag_can_be_run(self, ibmq, circuits):
        _assert_can_be_run(ibmq, circuits.v1_dag)

    def test_v0_v1_direct_sum_dag_can_be_run(self, ibmq, circuits):
        _assert_can_be_run(ibmq, circuits.v0_v1_direct_sum_dag)
