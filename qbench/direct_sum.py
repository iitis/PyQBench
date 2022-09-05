"""Module implementing experiment using direct sum of V0† ⊕ V1†."""
from typing import Union

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.providers import BackendV1, BackendV2
from qiskit.result import marginal_counts

from qbench.utils import remap_qubits


def asemble_direct_sum_circuits(
    state_preparation: Instruction,
    black_box_dag: Instruction,
    v0_v1_direct_sum_dag: Instruction,
    target: int,
    ancilla: int,
):
    id_circuit = QuantumCircuit(2)
    id_circuit.append(state_preparation, [0, 1])
    id_circuit.append(v0_v1_direct_sum_dag, [0, 1])
    id_circuit.measure_all()

    u_circuit = QuantumCircuit(2)
    u_circuit.append(state_preparation, [0, 1])
    u_circuit.append(black_box_dag, [0])
    u_circuit.append(v0_v1_direct_sum_dag, [0, 1])
    u_circuit.measure_all()

    return (
        remap_qubits(id_circuit, {0: target, 1: ancilla}).decompose(),
        remap_qubits(u_circuit, {0: target, 1: ancilla}).decompose(),
    )


def interpret_direct_sum_measurements(id_counts, u_counts):
    num_shots_per_measurement = sum(id_counts.values())
    return (
        marginal_counts(id_counts, [1]).get("1", 0) + marginal_counts(u_counts, [1]).get("0", 0)
    ) / (2 * num_shots_per_measurement)


def benchmark_using_controlled_unitary(
    backend: Union[BackendV1, BackendV2],
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    black_box_dag: Instruction,
    v0_v1_direct_sum_dag: Instruction,
    num_shots_per_measurement: int,
) -> float:
    """Estimate prob. of distinguishing between measurements in computational and other basis.

    :param backend: backend to be used for sampling.
    :param target: index of qubit measured either in computational basis or the alternative
     one.
    :param ancilla: index of auxiliary qubit.
    :param state_preparation: instruction preparing the initial state of both qubits.
    :param black_box_dag: hermitian adjoint of matrix U s.t. i-th column corresponds to
     i-th effect of alternative measurement. Can be viewed as matrix for a change of basis in
     which measurement is being performed.
    :param v0_v1_direct_sum_dag: block-diagonal operator comprising hermitian adjoints
     of both parts of Holevo-Helstrom measurement.
    :param num_shots_per_measurement: number of shots to be performed for computational basis and
     alternative measurement. The total number of shots done in the experiment is
     therefore 2 * num_shots_per_measurement.
    :return: estimated probability of distinguishing between computational basis and alternative
     measurement.

    .. note::
       The circuits used for sampling have the form::

                   ┌────────────────────┐┌────┐┌────────────┐
           target: ┤0                   ├┤ M† ├┤0           ├─
                   │  state_preparation │└────┘│  V0† ⊕ V1† │
          ancilla: ┤1                   ├──────┤1           ├─
                   └────────────────────┘      └────────────┘

       where M defines the measurement to be performed (M=identity or M=U†).
       Refer to the paper for details how the final measurements are interpreted.
    """
    id_circuit, u_circuit = asemble_direct_sum_circuits(
        state_preparation=state_preparation,
        black_box_dag=black_box_dag,
        v0_v1_direct_sum_dag=v0_v1_direct_sum_dag,
        target=target,
        ancilla=ancilla,
    )

    id_counts = backend.run(id_circuit, shots=num_shots_per_measurement).result().get_counts()
    u_counts = backend.run(u_circuit, shots=num_shots_per_measurement).result().get_counts()

    return interpret_direct_sum_measurements(id_counts, u_counts)
