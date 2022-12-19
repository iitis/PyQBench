import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit_braket_provider import AWSBraketProvider

from qbench.fourier import FourierComponents


def _assert_can_be_run_in_verbatim_mode(backend, instruction: Instruction):
    circuit = QuantumCircuit(instruction.num_qubits)
    circuit.append(instruction, list(range(instruction.num_qubits)))
    circuit.measure_all()
    resp = backend.run(circuit.decompose(), shots=10, verbatim=True, disable_qubit_rewiring=True)
    assert resp.result()
    assert sum(resp.result().get_counts().values()) == 10


@pytest.fixture(scope="module")
def aspen():
    return AWSBraketProvider().get_backend("Aspen-M-2")


@pytest.fixture()
def circuits():
    # We only use one value of phi that is not a characteristic multiple of pi/2
    # It should be enough to verify that circuits can be run, while not incurring
    # too big costs when tests are run.
    return FourierComponents(phi=0.1, gateset="rigetti")


@pytest.mark.skipif("not config.getoption('rigetti')")
class TestRigettiDeviceCanRunDecomposedCircuitsInVerbatimMode:
    def test_u_dag_can_be_run(self, aspen, circuits):
        _assert_can_be_run_in_verbatim_mode(aspen, circuits.u_dag)

    def test_v0_dag_can_be_run(self, aspen, circuits):
        _assert_can_be_run_in_verbatim_mode(aspen, circuits.v0_dag)

    def test_v1_dag_can_be_run(self, aspen, circuits):
        _assert_can_be_run_in_verbatim_mode(aspen, circuits.v1_dag)

    def test_v0_v1_direct_sum_dag_can_be_run(self, aspen, circuits):
        _assert_can_be_run_in_verbatim_mode(aspen, circuits.v0_v1_direct_sum_dag)
