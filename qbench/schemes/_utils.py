"""Module containing utilities, maybe combinatorial ones."""
from typing import Dict

from qiskit import QuantumCircuit, transpile


def remap_qubits(circuit: QuantumCircuit, virtual_to_physical: Dict[int, int]) -> QuantumCircuit:
    """Transpile a circuit by assigning virtual qubits to physical ones.

    :param circuit: quantum circuit to be transpiled.
    :param virtual_to_physical: a mapping of the form virtual index -> physical index.
    :return: circuit with remapped qubits. The returned circuit has always continuous
     indices, and the unused qubits are treated as ancillas.
    """
    assert len(circuit.qregs) == 1
    qreg = circuit.qregs[0]
    return transpile(
        circuit,
        optimization_level=0,
        initial_layout={qreg[key]: value for key, value in virtual_to_physical.items()},
    )
