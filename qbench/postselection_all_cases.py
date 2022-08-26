"""Module implementing postselection experiment."""
from typing import Union

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Instruction
from qiskit.providers import BackendV1, BackendV2
from qiskit.result import marginal_counts

from qbench.utils import remap_qubits


def _construct_identity_circuit(qreg, state_preparation, v_dag):
    circuit = QuantumCircuit(qreg)
    circuit.append(state_preparation, [0, 1])
    circuit.append(v_dag, [1])
    circuit.measure_all()
    return circuit


def _construct_black_box_circuit(qreg, state_preparation, black_box_dag, v_dag):
    circuit = QuantumCircuit(qreg)
    circuit.append(state_preparation, [0, 1])
    circuit.append(black_box_dag, [0])
    circuit.append(v_dag, [1])
    circuit.measure_all()
    return circuit


def benchmark_using_postselection_all_cases(
    backend: Union[BackendV1, BackendV2],
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    basis_change: Instruction,
    v0: Instruction,
    v1: Instruction,
    num_shots_per_measurement: int,
) -> float:
    # Register with logical bits, will later be mapped to physical ones
    qreg = QuantumRegister(2)

    identity_circuit_v0 = _construct_identity_circuit(qreg, state_preparation, v0)
    identity_circuit_v1 = _construct_identity_circuit(qreg, state_preparation, v1)

    u_circuit_v0 = _construct_black_box_circuit(qreg, state_preparation, basis_change, v0)
    u_circuit_v1 = _construct_black_box_circuit(qreg, state_preparation, basis_change, v1)

    # transpile to map 0, 1 into target and ancilla
    identity_circuit_v0 = remap_qubits(identity_circuit_v0, {0: target, 1: ancilla}).decompose()
    identity_circuit_v1 = remap_qubits(identity_circuit_v1, {0: target, 1: ancilla}).decompose()
    u_circuit_v0 = remap_qubits(u_circuit_v0, {0: target, 1: ancilla}).decompose()
    u_circuit_v1 = remap_qubits(u_circuit_v1, {0: target, 1: ancilla}).decompose()

    identity_v0_results = backend.run(identity_circuit_v0, shots=num_shots_per_measurement).result()
    identity_v1_results = backend.run(identity_circuit_v1, shots=num_shots_per_measurement).result()

    u_results_v0 = backend.run(u_circuit_v0, shots=num_shots_per_measurement).result()
    u_results_v1 = backend.run(u_circuit_v1, shots=num_shots_per_measurement).result()

    return (
        u_results_v0.get_counts()["00"] / marginal_counts(u_results_v0.get_counts(), [0])["0"]
        + u_results_v1.get_counts()["01"] / marginal_counts(u_results_v1.get_counts(), [0])["1"]
        + identity_v0_results.get_counts()["10"]
        / marginal_counts(identity_v0_results.get_counts(), [0])["0"]
        + identity_v1_results.get_counts()["11"]
        / marginal_counts(identity_v1_results.get_counts(), [0])["1"]
    ) / 4
