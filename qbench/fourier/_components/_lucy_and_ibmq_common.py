import numpy as np
from qiskit import QuantumCircuit


def u_dag(phi):
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
