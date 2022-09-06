"""Module implementing postselection experiment."""
from typing import Union

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.providers import BackendV1, BackendV2
from qiskit.result import marginal_counts

from qbench.utils import remap_qubits


def _construct_identity_circuit(state_preparation, v_dag):
    circuit = QuantumCircuit(2)
    circuit.append(state_preparation, [0, 1])
    circuit.append(v_dag, [1])
    circuit.measure_all()
    return circuit


def _construct_black_box_circuit(state_preparation, black_box_dag, v_dag):
    circuit = QuantumCircuit(2)
    circuit.append(state_preparation, [0, 1])
    circuit.append(black_box_dag, [0])
    circuit.append(v_dag, [1])
    circuit.measure_all()
    return circuit


def asemble_postselection_circuits(
    state_preparation: Instruction,
    black_box_dag: Instruction,
    v0_dag: Instruction,
    v1_dag: Instruction,
    target: int,
    ancilla: int,
):
    raw_circuits = [
        _construct_identity_circuit(state_preparation, v0_dag),
        _construct_identity_circuit(state_preparation, v1_dag),
        _construct_black_box_circuit(state_preparation, black_box_dag, v0_dag),
        _construct_black_box_circuit(state_preparation, black_box_dag, v1_dag),
    ]
    return [remap_qubits(circuit, {0: target, 1: ancilla}).decompose() for circuit in raw_circuits]


def interpret_postselection_measurements(id_v0_counts, id_v1_counts, u_v0_counts, u_v1_counts):
    return (
        u_v0_counts.get("00", 0) / marginal_counts(u_v0_counts, [0]).get("0", 0)
        + u_v1_counts.get("01", 0) / marginal_counts(u_v1_counts, [0]).get("1", 0)
        + id_v0_counts.get("10", 0) / marginal_counts(id_v0_counts, [0]).get("0", 0)
        + id_v1_counts.get("11", 0) / marginal_counts(id_v1_counts, [0]).get("1", 0)
    ) / 4


def benchmark_using_postselection(
    backend: Union[BackendV1, BackendV2],
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    black_box_dag: Instruction,
    v0_dag: Instruction,
    v1_dag: Instruction,
    num_shots_per_measurement: int,
) -> float:
    """Estimate prob. of distinguishing between measurements in computational and other basis.

    :param backend: backend to use for sampling.
    :param target: index of qubit measured either in Z-basis or the alternative one.
    :param ancilla: index of auxiliary qubit.
    :param state_preparation: instruction preparing the initial state of both qubits.
    :param black_box_dag: hermitian adjoint of matrix U s.t. i-th column corresponds to
     i-th effect of alternative measurement. Can be viewed as matrix for a change of basis in
     which measurement is being performed.
    :param v0_dag: hermitian adjoint of positive part of Holevo-Helstrom measurement.
    :param v1_dag: hermitian adjoint of negative part of Holevo-Helstrom measurement.
    :param num_shots_per_measurement: number of shots to be performed for Z-basis and
     alternative measurement. The total number of shots done in the experiment is
     therefore 2 * num_shots_per_measurement.
    :return: estimated probability of distinguishing between computational basis and alternative
      measurement.

    .. note::
       The circuits used for sampling have the form:::

                    ┌────────────────────┐ ┌─────┐
            target: ┤0                   ├─┤ Mi† ├
                    │  state_preparation │ ├─────┤
           ancilla: ┤1                   ├─┤ Vj† ├
                    └────────────────────┘ └─────┘

       for i=0,1, j=0,1 where M0 = U, M1 = identity.
       Refer to the paper for details how the terminal measurements are interpreted.
    """
    (id_circuit_v0, id_circuit_v1, u_circuit_v0, u_circuit_v1,) = asemble_postselection_circuits(
        state_preparation=state_preparation,
        black_box_dag=black_box_dag,
        v0_dag=v0_dag,
        v1_dag=v1_dag,
        target=target,
        ancilla=ancilla,
    )

    id_v0_counts = backend.run(id_circuit_v0, shots=num_shots_per_measurement).result().get_counts()
    id_v1_counts = backend.run(id_circuit_v1, shots=num_shots_per_measurement).result().get_counts()

    u_v0_counts = backend.run(u_circuit_v0, shots=num_shots_per_measurement).result().get_counts()
    u_v1_counts = backend.run(u_circuit_v1, shots=num_shots_per_measurement).result().get_counts()

    return interpret_postselection_measurements(
        id_v0_counts, id_v1_counts, u_v0_counts, u_v1_counts
    )
