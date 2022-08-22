import numpy as np
from qiskit import QuantumCircuit


def _state_preparation():
    circuit = QuantumCircuit(2)
    circuit.sx(0)
    circuit.rz(np.pi, 0)
    circuit.x(0)
    circuit.sx(1)
    circuit.ecr(0, 1)
    return circuit


def _black_box_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-phi, 0)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    return circuit


def _v0_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(-np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-(phi + np.pi) / 2, 0)
    circuit.sx(0)
    circuit.x(0)
    return circuit


def _v1_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-(np.pi - phi) / 2, 0)
    circuit.x(0)
    circuit.sx(0)
    return circuit


def _v0_v1_direct_sum(phi):
    circuit = QuantumCircuit(2)
    circuit.rz(-np.pi / 2, 1)
    circuit.sx(1)
    circuit.rz(-(phi + np.pi) / 2, 1)
    circuit.rz(3 * np.pi / 2, 0)
    circuit.x(0)
    circuit.ecr(0, 1)
    return circuit
