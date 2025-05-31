"""Components for Fourier experiment that are common to both Lucy and IBMQ devices.

For detailed description of functions in this module refer to the documentation of
FourierComponents class.
"""

import numpy as np
from qiskit import QuantumCircuit


def u_dag(phi):
    circuit = QuantumCircuit(1)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(-phi, 0)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    return circuit.to_instruction()


def v0_dag(phi: float, delta: float):
    circuit = QuantumCircuit(1)
    if 1 + np.cos(phi) >= 2 * delta and (0 <= phi <= np.pi):
        circuit.rz(-np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(2 * np.arcsin(np.sqrt(delta)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    elif 1 + np.cos(phi) >= 2 * delta and np.pi < phi <= 2 * np.pi:
        circuit.rz(-np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(-2 * np.arcsin(np.sqrt(delta)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    elif 1 + np.cos(phi) < 2 * delta and 0 <= phi <= np.pi:
        circuit.rz(-np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(2 * np.arccos(np.sin(phi / 2)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    else:
        circuit.rz(np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(2 * np.arccos(np.sin(phi / 2)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    return circuit.to_instruction()


def v1_dag(phi: float, delta: float):
    circuit = QuantumCircuit(1)
    if 1 + np.cos(phi) >= 2 * delta and 0 <= phi <= np.pi:
        circuit.rz(-np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(-np.pi, 0)
        circuit.rz(2 * np.arcsin(np.sqrt(delta)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    elif 1 + np.cos(phi) >= 2 * delta and np.pi < phi <= 2 * np.pi:
        circuit.rz(-np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(-np.pi, 0)
        circuit.rz(-2 * np.arcsin(np.sqrt(delta)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    elif 1 + np.cos(phi) < 2 * delta and 0 <= phi <= np.pi:
        circuit.rz(-np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(-np.pi, 0)
        circuit.rz(2 * np.arccos(np.sin(phi / 2)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    else:
        circuit.rz(np.pi / 2, 0)
        circuit.sx(0)
        circuit.rz(-np.pi, 0)
        circuit.rz(2 * np.arccos(np.sin(phi / 2)) + np.pi, 0)
        circuit.sx(0)
        circuit.rz(3 * np.pi, 0)
    return circuit.to_instruction()


# def u_dag(phi: AnyParameter) -> Instruction:
# circuit = QuantumCircuit(1, name="U-dag")
# circuit.sx(0)
# circuit.rz(np.pi / 2, 0)
# circuit.sx(0)
# circuit.rz(-phi, 0)
# circuit.sx(0)
# circuit.rz(np.pi / 2, 0)
# circuit.sx(0)
# return circuit.to_instruction()


# def v0_dag(phi: AnyParameter) -> Instruction:
# circuit = QuantumCircuit(1, name="v0-dag")
# circuit.rz(-np.pi / 2, 0)
# circuit.sx(0)
# circuit.rz(-(phi + np.pi) / 2, 0)
# circuit.sx(0)
# circuit.x(0)
# return circuit.to_instruction()


# def v1_dag(phi: AnyParameter) -> Instruction:
# circuit = QuantumCircuit(1, name="v1-dag")
# circuit.rz(np.pi / 2, 0)
# circuit.sx(0)
# circuit.rz(-(np.pi - phi) / 2, 0)
# circuit.x(0)
# circuit.sx(0)
# return circuit.to_instruction()
