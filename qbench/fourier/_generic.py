import numpy as np
from qiskit.circuit import QuantumCircuit


def state_preparation():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cnot(0, 1)
    return circuit.to_instruction()


def black_box_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.h(0)
    circuit.p(-phi, 0)
    circuit.h(0)
    return circuit.to_instruction()


def v0_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(-np.pi / 2, 0)
    circuit.ry(-(phi + np.pi) / 2, 0)
    return circuit.to_instruction()


def v1_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(-np.pi / 2, 0)
    circuit.ry(-(phi + np.pi) / 2, 0)
    circuit.rx(-np.pi, 0)
    return circuit.to_instruction()


def v0_v1_direct_sum(phi):
    circuit = QuantumCircuit(2)
    circuit.p(np.pi, 0)
    circuit.append(v0_dag(phi), [1])
    circuit.cnot(0, 1)
    return circuit.to_instruction()
