import pytest
from braket.circuits import Circuit
from qiskit import QuantumCircuit
from qiskit_braket_provider import AWSBraketProvider

from qbench.fourier import FourierCircuits


def _assert_can_be_run_in_verbatim_mode(device, circuit):
    verbatim_circuit = Circuit().add_verbatim_box(circuit)
    # Shots = 10 is the minimum number.
    resp = device.run(verbatim_circuit, shots=10)
    assert resp.result()


def _assert_can_be_run(backend, circuit):
    assert backend.run(circuit, shots=10).results()


def _instruction_as_circuit(instruction, qubits):
    circuit = QuantumCircuit(len(qubits))
    circuit.append(instruction, qubits)
    circuit.measure_all()
    return circuit


@pytest.fixture()
def lucy():
    return AWSBraketProvider().get_backend("Lucy")


@pytest.fixture()
def circuits():
    # We only use one value of phi that is not a characteristic multiple of pi/2
    # It should be enough to verify that circuits can be run, while not incurring
    # too big costs when tests are run.
    return FourierCircuits(phi=0.1, gateset="lucy")


@pytest.mark.skipif("not config.getoption('lucy')")
class TestLucyDeviceCanRunDecomposedCircuits:
    def test_black_box_can_be_run(self, lucy, circuits):
        _assert_can_be_run(lucy, circuits.black_box_dag)

    def test_v0_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run(lucy, circuits.v0_dag)

    def test_v1_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run(lucy, circuits.v1_dag)

    def test_v0_v1_direct_sum_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run(lucy, circuits.controlled_v0_v1_dag)


# @pytest.mark.skipif("not config.getoption('lucy')")
@pytest.mark.skip
class TestLucyDeviceCanRunDecomposedCircuitsInVerbatimMode:
    def test_black_box_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.black_box_dag)

    def test_v0_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.v0_dag)

    def test_v1_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.v1_dag)

    def test_v0_v1_direct_sum_dag_can_be_run(self, lucy, circuits):
        _assert_can_be_run_in_verbatim_mode(lucy, circuits.controlled_v0_v1_dag)
