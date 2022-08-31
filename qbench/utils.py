"""Module containing utilities, maybe combinatorial ones."""
from typing import Dict

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Instruction


def remap_qubits(circuit: QuantumCircuit, virtual_to_physical: Dict[int, int]):
    assert len(circuit.qregs) == 1
    qreg = circuit.qregs[0]
    return transpile(
        circuit,
        optimization_level=0,
        initial_layout={qreg[key]: value for key, value in virtual_to_physical.items()},
    )


def assert_can_be_run_in_verbatim_mode(backend, instruction: Instruction):
    circuit = QuantumCircuit(instruction.num_qubits)
    circuit.append(instruction, list(range(instruction.num_qubits)))
    circuit.measure_all()
    resp = backend.run(circuit.decompose(), shots=10, verbatim=True, disable_qubit_rewiring=True)
    assert resp.result()
    assert sum(resp.result().get_counts().values()) == 10
