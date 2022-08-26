"""Module implementing direct experiment."""
from typing import Union

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Instruction
from qiskit.providers import BackendV1, BackendV2
from qiskit.result import marginal_counts

from qbench.utils import remap_qubits


def benchmark_using_controlled_unitary(
    backend: Union[BackendV1, BackendV2],
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    black_box_dag: Instruction,
    v0_v1_direct_sum_dag: Instruction,
    num_shots_per_measurement: int,
) -> float:
    # Register with logical bits, will later be mapped to physical ones
    qreg = QuantumRegister(2)

    identity_circuit = QuantumCircuit(qreg)
    identity_circuit.append(state_preparation, [0, 1])
    identity_circuit.append(v0_v1_direct_sum_dag, [0, 1])
    identity_circuit.measure_all()

    u_circuit = QuantumCircuit(qreg)
    u_circuit.append(state_preparation, [0, 1])
    u_circuit.append(black_box_dag, [0])
    u_circuit.append(v0_v1_direct_sum_dag, [0, 1])
    u_circuit.measure_all()

    # transpile to map 0, 1 into target and ancilla
    identity_circuit = remap_qubits(identity_circuit, {0: target, 1: ancilla}).decompose()
    u_circuit = remap_qubits(u_circuit, {0: target, 1: ancilla}).decompose()

    identity_results = backend.run(identity_circuit, shots=num_shots_per_measurement).result()
    u_results = backend.run(u_circuit, shots=num_shots_per_measurement).result()

    return (
        marginal_counts(identity_results.get_counts(), [1]).get("1", 0)
        + marginal_counts(u_results.get_counts(), [1]).get("0", 0)
    ) / (2 * num_shots_per_measurement)
