"""Module implementing experiment using direct sum of V0† ⊕ V1†."""
from typing import Dict, Union

from qiskit import QuantumCircuit
from qiskit.circuit import Instruction
from qiskit.providers import BackendV1, BackendV2
from qiskit.result import marginal_counts

from ..common_models import MeasurementsDict
from ._utils import remap_qubits


def assemble_direct_sum_circuits(
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    u_dag: Instruction,
    v0_v1_direct_sum_dag: Instruction,
) -> Dict[str, QuantumCircuit]:
    """Assemble circuits required for running Fourier discrimination experiment using direct-sum.

    :param target: index of qubit measured either in Z-basis or the alternative one.
    :param ancilla: index of auxiliary qubit.
    :param state_preparation: instruction preparing the initial state of both qubits.
    :param u_dag: hermitian adjoint of matrix U s.t. i-th column corresponds to
     i-th effect of alternative measurement. Can be viewed as matrix for a change of basis in
     which measurement is being performed.
    :param v0_v1_direct_sum_dag: block-diagonal operator comprising hermitian adjoints of both
     parts of Holevo-Helstrom measurement.
    :return: dictionary with keys "id", "u"mapped to corresponding circuits. The "u" key
     corresponds to a circuit for which U measurement has been performed, while "id" key
     corresponds to a circuit for which identity measurement has been performed.
    """
    id_circuit = QuantumCircuit(2)
    id_circuit.append(state_preparation, [0, 1])
    id_circuit.append(v0_v1_direct_sum_dag, [0, 1])
    id_circuit.measure_all()

    u_circuit = QuantumCircuit(2)
    u_circuit.append(state_preparation, [0, 1])
    u_circuit.append(u_dag, [0])
    u_circuit.append(v0_v1_direct_sum_dag, [0, 1])
    u_circuit.measure_all()

    return {
        "id": remap_qubits(id_circuit, {0: target, 1: ancilla}).decompose(),
        "u": remap_qubits(u_circuit, {0: target, 1: ancilla}).decompose(),
    }


def compute_probabilities_from_direct_sum_measurements(
    id_counts: MeasurementsDict, u_counts: MeasurementsDict
) -> float:
    """Convert measurements obtained from direct_sum Fourier experiment to probabilities.

    :param id_counts: measurements for circuit with identity measurement on target qubit.
    :param u_counts: measurements for circuit with U measurement on target qubit.
    :return: probability of distinguishing between u and identity measurements.
    """
    num_shots_per_measurement = sum(id_counts.values())
    return (
        marginal_counts(id_counts, [1]).get("1", 0) + marginal_counts(u_counts, [1]).get("0", 0)
    ) / (2 * num_shots_per_measurement)


def benchmark_using_direct_sum(
    backend: Union[BackendV1, BackendV2],
    target: int,
    ancilla: int,
    state_preparation: Instruction,
    u_dag: Instruction,
    v0_v1_direct_sum_dag: Instruction,
    num_shots_per_measurement: int,
) -> float:
    """Estimate prob. of distinguishing between measurements in computational and other basis.

    :param backend: backend to be used for sampling.
    :param target: index of qubit measured either in computational basis or the alternative
     one.
    :param ancilla: index of auxiliary qubit.
    :param state_preparation: instruction preparing the initial state of both qubits.
    :param u_dag: hermitian adjoint of matrix U s.t. i-th column corresponds to
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
    circuits = assemble_direct_sum_circuits(
        state_preparation=state_preparation,
        u_dag=u_dag,
        v0_v1_direct_sum_dag=v0_v1_direct_sum_dag,
        target=target,
        ancilla=ancilla,
    )

    id_counts = backend.run(circuits["id"], shots=num_shots_per_measurement).result().get_counts()
    u_counts = backend.run(circuits["u"], shots=num_shots_per_measurement).result().get_counts()

    return compute_probabilities_from_direct_sum_measurements(id_counts, u_counts)
