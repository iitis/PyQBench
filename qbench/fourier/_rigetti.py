import numpy as np
from qiskit import QuantumCircuit


def _rigetti_hadamard():
    """Decomposition of Hadamard gate using only Rigetti native gates.

    The decomposition uses the identity: H = RX(pi/2) RZ(pi/2) RX(pi/2)
    """
    circuit = QuantumCircuit(1)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    return circuit.to_instruction()


def _rigetti_cnot():
    """Decomposition of CNOT gate using only Rigetti native gates.

    The decomposition uses identity: CNOT(i, j) = H(j) CZ(i, j) H(j), and the hadamard gates
    are decomposed using _rigetti_hadamard function.
    """
    circuit = QuantumCircuit(2)
    circuit.append(_rigetti_hadamard(), [1])
    circuit.cz(0, 1)
    circuit.append(_rigetti_hadamard(), [1])
    return circuit.to_instruction()


# For description of functions below refer to the __init__ file in qbench.fourier


def _state_preparation():
    circuit = QuantumCircuit(2)
    circuit.append(_rigetti_hadamard(), [0])
    circuit.append(_rigetti_cnot(), [0, 1])
    return circuit.to_instruction()


def _black_box_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(-phi, 0)
    circuit.rx(-np.pi / 2, 0)
    circuit.rz(-np.pi / 2, 0)
    return circuit.to_instruction()


def _v0_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(-np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(-(phi + np.pi) / 2, 0)
    circuit.rx(-np.pi / 2, 0)
    return circuit.to_instruction()


def _v1_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(-(np.pi - phi) / 2, 0)
    circuit.rx(-np.pi / 2, 0)
    return circuit.to_instruction()


def _v0_v1_direct_sum(phi):
    circuit = QuantumCircuit(2)
    circuit.rz(np.pi, 0)
    circuit.append(_v0_dag(phi), [1])
    circuit.append(_rigetti_cnot(), [0, 1])
    return circuit.to_instruction()
