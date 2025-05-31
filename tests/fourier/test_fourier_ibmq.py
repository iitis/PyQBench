import os

import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit_ibm_runtime import QiskitRuntimeService

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
    if sum(e in os.environ for e in ("QISKIT_IBM_TOKEN", "IBMQ_TOKEN", "IQP_API_TOKEN")) > 0:
        service = QiskitRuntimeService()
        return service.least_busy()

    raise ValueError(
        "Missing IBM API token! You need to specify it via environment variable QISKIT_IBM_TOKEN "
        "or IBMQ_TOKEN (deprecated)!"
    )


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
