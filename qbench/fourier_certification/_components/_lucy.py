"""Components for Fourier experiment specifically compiled for OQC Lucy device.

For detailed description of functions in this module refer to the documentation of
FourierComponents class.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction

from ._lucy_and_ibmq_common import u_dag, v0_dag, v1_dag


def state_preparation() -> Instruction:
    circuit = QuantumCircuit(2, name="state-prep")
    circuit.sx(0)
    circuit.rz(np.pi, 0)
    circuit.x(0)
    circuit.sx(1)
    circuit.ecr(0, 1)
    return circuit.to_instruction()


# def v0_v1_direct_sum(phi: AnyParameter) -> Instruction:
# circuit = QuantumCircuit(2, name="v0 ⊕ v1-dag")
# circuit.rz(-np.pi / 2, 1)
# circuit.sx(1)
# circuit.rz(-(phi + np.pi) / 2, 1)
# circuit.rz(3 * np.pi / 2, 0)
# circuit.x(0)
# circuit.ecr(0, 1)
# return circuit.to_instruction()


def v0_v1_direct_sum(phi, delta):
    circuit = QuantumCircuit(2, name="v0 ⊕ v1-dag")
    circuit.rz(np.pi, 0)
    circuit.append(v0_dag(phi, delta), [1])
    circuit.x(0)
    circuit.sx(1)
    circuit.rz(-np.pi / 2, 0)
    circuit.ecr(0, 1)
    return circuit.decompose(["v0-dag"]).to_instruction()


__all__ = ["state_preparation", "u_dag", "v0_dag", "v1_dag", "v0_v1_direct_sum"]
