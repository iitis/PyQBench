"""Components for Fourier experiment specifically compiled for OQC Lucy device.

For detailed description of functions in this module refer to the documentation of
FourierComponents class.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Instruction

from ...common_models import AnyParameter

INSTRUCTIONS_TO_DECOMPOSE = ["hadamard-rigetti", "cnot-rigetti", "v0-dag"]


def _decompose(circuit: QuantumCircuit) -> QuantumCircuit:
    return circuit.decompose(INSTRUCTIONS_TO_DECOMPOSE, reps=2)


def _rigetti_hadamard() -> Instruction:
    """Decomposition of Hadamard gate using only Rigetti native gates.

    The decomposition uses the identity: H = RX(pi/2) RZ(pi/2) RX(pi/2)
    """
    circuit = QuantumCircuit(1, name="hadamard-rigetti")
    circuit.rx(np.pi / 2, 0)
    circuit.rz(np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    return circuit.to_instruction()


def _rigetti_cnot() -> Instruction:
    """Decomposition of CNOT gate using only Rigetti native gates.

    The decomposition uses identity: CNOT(i, j) = H(j) CZ(i, j) H(j), and the hadamard gates
    are decomposed using _rigetti_hadamard function.
    """
    circuit = QuantumCircuit(2, name="cnot-rigetti")
    circuit.append(_rigetti_hadamard(), [1])
    circuit.cz(0, 1)
    circuit.append(_rigetti_hadamard(), [1])
    return circuit.to_instruction()


# For description of functions below refer to the __init__ file in qbench.fourier


def state_preparation() -> Instruction:
    circuit = QuantumCircuit(2, name="state-prep")
    circuit.append(_rigetti_hadamard(), [0])
    circuit.append(_rigetti_cnot(), [0, 1])
    return _decompose(circuit).to_instruction()


def u_dag(phi: AnyParameter) -> Instruction:
    circuit = QuantumCircuit(1, name="U-dag")
    circuit.rz(np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(-phi, 0)
    circuit.rx(-np.pi / 2, 0)
    circuit.rz(-np.pi / 2, 0)
    return circuit.to_instruction()


def v0_dag(phi: AnyParameter) -> Instruction:
    circuit = QuantumCircuit(1, name="v0-dag")
    circuit.rz(-np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(-(phi + np.pi) / 2, 0)
    circuit.rx(-np.pi / 2, 0)
    return circuit.to_instruction()


def v1_dag(phi: AnyParameter) -> Instruction:
    circuit = QuantumCircuit(1, name="v1-dag")
    circuit.rz(np.pi / 2, 0)
    circuit.rx(np.pi / 2, 0)
    circuit.rz(-(np.pi - phi) / 2, 0)
    circuit.rx(-np.pi / 2, 0)
    return circuit.to_instruction()


def v0_v1_direct_sum(phi: AnyParameter) -> Instruction:
    circuit = QuantumCircuit(2, name="v0 ⊕ v1-dag")
    circuit.rz(np.pi, 0)
    circuit.append(v0_dag(phi), [1])
    circuit.append(_rigetti_cnot(), [0, 1])
    return _decompose(circuit).to_instruction()
