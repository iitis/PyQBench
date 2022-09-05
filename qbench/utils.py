"""Module containing utilities, maybe combinatorial ones."""
from typing import Dict, Iterable

from qiskit import QuantumCircuit, transpile


def remap_qubits(circuit: QuantumCircuit, virtual_to_physical: Dict[int, int]):
    assert len(circuit.qregs) == 1
    qreg = circuit.qregs[0]
    return transpile(
        circuit,
        optimization_level=0,
        initial_layout={qreg[key]: value for key, value in virtual_to_physical.items()},
    )


def run_remapped(
    backend,
    circuits: Iterable[QuantumCircuit],
    virtual_to_physical: Dict[int, int],
    num_shots: int,
    **options
):
    transpiled = [remap_qubits(circuit, virtual_to_physical).decompose() for circuit in circuits]
    jobs = [backend.run(circuit, shots=num_shots, **options) for circuit in transpiled]
    return [job.result().get_counts() for job in jobs]
