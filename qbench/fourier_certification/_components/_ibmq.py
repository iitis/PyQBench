"""Components for Fourier experiment specifically compiled for IBMQ device.

For detailed description of functions in this module refer to the documentation of
FourierComponents class.
"""

import numpy as np
from qiskit.circuit import Instruction, QuantumCircuit

from ._lucy_and_ibmq_common import u_dag, v0_dag, v1_dag


def _decompose(circuit: QuantumCircuit):
    return circuit.decompose(["v0-dag"])


def state_preparation() -> Instruction:
    circuit = QuantumCircuit(2, name="state-prep")
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.cx(0, 1)
    return circuit.to_instruction()


# def v0_v1_direct_sum(phi: AnyParameter) -> Instruction:
# circuit = QuantumCircuit(2, name="v0 ⊕ v1-dag")
# circuit.rz(np.pi, 0)
# circuit.append(v0_dag(phi), [1])
# circuit.cx(0, 1)
# return _decompose(circuit).to_instruction()


def v0_v1_direct_sum(phi, delta):
    circuit = QuantumCircuit(2)
    circuit.rz(np.pi, 0)
    if 1 + np.cos(phi) >= 2 * delta and (0 <= phi <= np.pi):
        circuit.rz(-np.pi / 2, 1)
        circuit.sx(1)
        circuit.rz(2 * np.arcsin(np.sqrt(delta)) + np.pi, 1)
        circuit.sx(1)
        circuit.rz(3 * np.pi, 1)
    elif 1 + np.cos(phi) >= 2 * delta and np.pi < phi <= 2 * np.pi:
        circuit.rz(-np.pi / 2, 1)
        circuit.sx(1)
        circuit.rz(-2 * np.arcsin(np.sqrt(delta)) + np.pi, 1)
        circuit.sx(1)
        circuit.rz(3 * np.pi, 1)
    elif 1 + np.cos(phi) < 2 * delta and 0 <= phi <= np.pi:
        circuit.rz(-np.pi / 2, 1)
        circuit.sx(1)
        circuit.rz(2 * np.arccos(np.sin(phi / 2)) + np.pi, 1)
        circuit.sx(1)
        circuit.rz(3 * np.pi, 1)
    else:
        circuit.rz(np.pi / 2, 1)
        circuit.sx(1)
        circuit.rz(2 * np.arccos(np.sin(phi / 2)) + np.pi, 1)
        circuit.sx(1)
        circuit.rz(3 * np.pi, 1)
    circuit.cx(0, 1)
    return circuit.to_instruction()


__all__ = ["state_preparation", "u_dag", "v0_dag", "v1_dag", "v0_v1_direct_sum"]
