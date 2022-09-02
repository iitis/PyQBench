"""Module containing utilities, maybe combinatorial ones."""
from typing import Dict

from qiskit import QuantumCircuit, transpile


def remap_qubits(circuit: QuantumCircuit, virtual_to_physical: Dict[int, int]):
    assert len(circuit.qregs) == 1
    qreg = circuit.qregs[0]
    return transpile(
        circuit,
        optimization_level=0,
        initial_layout={qreg[key]: value for key, value in virtual_to_physical.items()},
    )
