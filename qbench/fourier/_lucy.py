import numpy as np
from qiskit import QuantumCircuit


def state_preparation():
    circuit = QuantumCircuit(2, name="state-prep")
    circuit.sx(0)
    circuit.rz(np.pi, 0)
    circuit.x(0)
    circuit.sx(1)
    circuit.ecr(0, 1)
    return circuit.to_instruction()


def black_box_dag(phi):
    circuit = QuantumCircuit(1, name="U-dag")
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-phi, 0)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    return circuit.to_instruction()


def v0_dag(phi):
    circuit = QuantumCircuit(1, name="v0-dag")
    circuit.rz(-np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-(phi + np.pi) / 2, 0)
    circuit.sx(0)
    circuit.x(0)
    return circuit.to_instruction()


def v1_dag(phi):
    circuit = QuantumCircuit(1, name="v1-dag")
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-(np.pi - phi) / 2, 0)
    circuit.x(0)
    circuit.sx(0)
    return circuit.to_instruction()


def v0_v1_direct_sum(phi):
    circuit = QuantumCircuit(2, name="v0 \\oplus v1-dag")
    circuit.rz(-np.pi / 2, 1)
    circuit.sx(1)
    circuit.rz(-(phi + np.pi) / 2, 1)
    circuit.rz(3 * np.pi / 2, 0)
    circuit.x(0)
    circuit.ecr(0, 1)
    return circuit.to_instruction()
