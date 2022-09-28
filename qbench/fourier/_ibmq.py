"""Components for Fourier experiment specifically compiled for IBMQ device."""
import numpy as np
from qiskit.circuit import QuantumCircuit

from ._lucy_and_ibmq_common import black_box_dag, v0_dag, v1_dag


def _decompose(circuit):
    return circuit.decompose(["v0-dag"])


def state_preparation():
    circuit = QuantumCircuit(2, name="state-prep")
    circuit.rz(np.pi / 2, 0)
    circuit.sx(0)
    circuit.rz(np.pi / 2, 0)
    circuit.cx(0, 1)
    return circuit.to_instruction()


def v0_v1_direct_sum(phi):
    circuit = QuantumCircuit(2, name="v0 ⊕ v1-dag")
    circuit.rz(np.pi, 0)
    circuit.append(v0_dag(phi), [1])
    circuit.cx(0, 1)
    return _decompose(circuit).to_instruction()


__all__ = ["state_preparation", "black_box_dag", "v0_dag", "v1_dag", "v0_v1_direct_sum"]
