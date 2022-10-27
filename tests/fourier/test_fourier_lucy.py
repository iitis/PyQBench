import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit_braket_provider import AWSBraketProvider

from qbench.fourier import FourierComponents


def _assert_can_be_run_in_verbatim_mode(backend, instruction: Instruction):
    circuit = QuantumCircuit(instruction.num_qubits)
    circuit.append(instruction, list(range(instruction.num_qubits)))
    circuit.measure_all()
    resp = backend.run(circuit.decompose(), shots=10, verbatim=True)
    assert resp.result()
    assert sum(resp.result().get_counts().values()) == 10


@pytest.fixture(scope="module")
def lucy():
    return AWSBraketProvider().get_backend("Lucy")


@pytest.fixture()
def circuits():
    # We only use one value of phi that is not a characteristic multiple of pi/2
    # It should be enough to verify that circuits can be run, while not incurring
    # too big costs when tests are run.
    return FourierComponents(phi=0.1, gateset="lucy")


@pytest.mark.skipif("not config.getoption('lucy')")
class TestLucyDeviceCanRunDecomposedCircuitsInVerbatimMode:
    def test_u_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.u_dag)

    def test_v0_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.v0_dag)

    def test_v1_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.v1_dag)

    def test_v0_v1_direct_sum_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.v0_v1_direct_sum_dag)
