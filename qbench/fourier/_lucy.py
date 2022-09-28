"""Components for Fourier experiment specifically compiled for OQC Lucy device."""
import numpy as np
from qiskit import QuantumCircuit

from ._lucy_and_ibmq_common import black_box_dag, v0_dag, v1_dag


def state_preparation():
    circuit = QuantumCircuit(2, name="state-prep")
    circuit.sx(0)
    circuit.rz(np.pi, 0)
    circuit.x(0)
    circuit.sx(1)
    circuit.ecr(0, 1)
    return circuit.to_instruction()


def v0_v1_direct_sum(phi):
    circuit = QuantumCircuit(2, name="v0 ⊕ v1-dag")
    circuit.rz(-np.pi / 2, 1)
    circuit.sx(1)
    circuit.rz(-(phi + np.pi) / 2, 1)
    circuit.rz(3 * np.pi / 2, 0)
    circuit.x(0)
    circuit.ecr(0, 1)
    return circuit.to_instruction()


__all__ = ["state_preparation", "black_box_dag", "v0_dag", "v1_dag", "v0_v1_direct_sum"]
