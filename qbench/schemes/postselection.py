"""Module implementing postselection experiment."""
from typing import Dict, Union

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.providers import BackendV1, BackendV2
from qiskit.result import marginal_counts

from ..common_models import MeasurementsDict
from ._utils import remap_qubits


def _construct_identity_circuit(
    state_preparation: Instruction, v_dag: Instruction
) -> QuantumCircuit:
    circuit = QuantumCircuit(2)
    circuit.append(state_preparation, [0, 1])
    circuit.append(v_dag, [1])
    circuit.measure_all()
    return circuit


def _construct_black_box_circuit(
    state_preparation: Instruction, u_dag: Instruction, v_dag: Instruction
) -> QuantumCircuit:
    circuit = QuantumCircuit(2)
    circuit.append(state_preparation, [0, 1])
    circuit.append(u_dag, [0])
    circuit.append(v_dag, [1])
    circuit.measure_all()
    return circuit


def assemble_postselection_circuits(
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    u_dag: Instruction,
    v0_dag: Instruction,
    v1_dag: Instruction,
) -> Dict[str, QuantumCircuit]:
    """Assemble circuits required for running Fourier discrimination experiment using postselection.

    :param target: index of qubit measured either in Z-basis or the alternative one.
    :param ancilla: index of auxiliary qubit.
    :param state_preparation: instruction preparing the initial state of both qubits.
    :param u_dag: hermitian adjoint of matrix U s.t. i-th column corresponds to
     i-th effect of alternative measurement. Can be viewed as matrix for a change of basis in
     which measurement is being performed.
    :param v0_dag: hermitian adjoint of positive part of Holevo-Helstrom measurement.
    :param v1_dag: hermitian adjoint of negative part of Holevo-Helstrom measurement.

    :return: dictionary with keys "id_v0", "id_v1", "u_v0", "u_v1" mapped to corresponding circuits.
     (e.g. id_v0 maps to a circuit with identity measurement followed by v0 measurement on ancilla)
    """
    raw_circuits = {
        "id_v0": _construct_identity_circuit(state_preparation, v0_dag),
        "id_v1": _construct_identity_circuit(state_preparation, v1_dag),
        "u_v0": _construct_black_box_circuit(state_preparation, u_dag, v0_dag),
        "u_v1": _construct_black_box_circuit(state_preparation, u_dag, v1_dag),
    }
    return {
        key: remap_qubits(circuit, {0: target, 1: ancilla}).decompose()
        for key, circuit in raw_circuits.items()
    }


def compute_probabilities_from_postselection_measurements(
    id_v0_counts: MeasurementsDict,
    id_v1_counts: MeasurementsDict,
    u_v0_counts: MeasurementsDict,
    u_v1_counts: MeasurementsDict,
) -> float:
    """Convert measurements obtained from postselection Fourier discrimination experiment
    to probabilities.

    :param id_v0_counts: measurements for circuit with identity measurement on target and
     v0 measurement on ancilla.
    :param id_v1_counts: measurements for circuit with identity measurement on target and
     v1 measurement on ancilla.
    :param u_v0_counts: measurements for circuit with U measurement on target and
     v0 measurement on ancilla.
    :param u_v1_counts: measurements for circuit with U measurement on target and
     v1 measurement on ancilla.
    :return: probability of distinguishing between u and identity measurements.
    """
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
    u_dag: Instruction,
    v0_dag: Instruction,
    v1_dag: Instruction,
    num_shots_per_measurement: int,
) -> float:
    """Estimate prob. of distinguishing between measurements in computational and other basis.

    :param backend: backend to use for sampling.
    :param target: index of qubit measured either in Z-basis or the alternative one.
    :param ancilla: index of auxiliary qubit.
    :param state_preparation: instruction preparing the initial state of both qubits.
    :param u_dag: hermitian adjoint of matrix U s.t. i-th column corresponds to
     i-th effect of alternative measurement. Can be viewed as matrix for a change of basis in
     which measurement is being performed.
    :param v0_dag: hermitian adjoint of positive part of Holevo-Helstrom measurement.
    :param v1_dag: hermitian adjoint of negative part of Holevo-Helstrom measurement.
    :param num_shots_per_measurement: number of shots to be performed for Z-basis and
     alternative measurement. Since each measurement on target qubit is combined with each
     measurement on ancilla qubit, the total number of shots done in the experiment is
     4 * num_shots_per_measurement.
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
    circuits = assemble_postselection_circuits(
        state_preparation=state_preparation,
        u_dag=u_dag,
        v0_dag=v0_dag,
        v1_dag=v1_dag,
        target=target,
        ancilla=ancilla,
    )

    counts = {
        key: backend.run(circuit, shots=num_shots_per_measurement).result().get_counts()
        for key, circuit in circuits.items()
    }

    return compute_probabilities_from_postselection_measurements(
        counts["id_v0"], counts["id_v1"], counts["u_v0"], counts["u_v1"]
    )
