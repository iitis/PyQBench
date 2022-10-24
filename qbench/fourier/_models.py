from typing import (
    Any,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

import numpy as np
from pydantic import validator

from ..common_models import (
    AnglesRange,
    BackendDescription,
    BaseModel,
    Qubit,
    QubitsPair,
    StrictPositiveInt,
    SynchronousHistogram,
)


class FourierExperimentSet(BaseModel):
    type: Literal["discrimination-fourier"]
    qubits: List[QubitsPair]
    angles: AnglesRange
    gateset: Optional[str]
    method: Literal["direct_sum", "postselection"]
    num_shots: StrictPositiveInt

    @validator("qubits")
    def check_if_all_pairs_of_qubits_are_different(cls, qubits):
        list_of_qubits = [(qubits.target, qubits.ancilla) for qubits in qubits]
        if len(set(list_of_qubits)) != len(list_of_qubits):
            raise ValueError("All pairs of qubits should be distinct.")
        return qubits

    def enumerate_experiment_labels(self) -> Iterable[Tuple[int, int, float]]:
        return (
            (pair.target, pair.ancilla, phi)
            for pair in self.qubits
            for phi in np.linspace(self.angles.start, self.angles.stop, self.angles.num_steps)
        )


class FourierDiscriminationMetadata(BaseModel):
    experiments: FourierExperimentSet
    backend_description: BackendDescription


T = TypeVar("T", bound="QubitMitigationInfo")


class QubitMitigationInfo(BaseModel):
    prob_meas0_prep1: float
    prob_meas1_prep0: float

    @classmethod
    def from_job_properties(cls: Type[T], properties, qubit) -> T:
        return cls.parse_obj(
            {
                "prob_meas0_prep1": properties.qubit_property(qubit)["prob_meas0_prep1"][0],
                "prob_meas1_prep0": properties.qubit_property(qubit)["prob_meas1_prep0"][0],
            }
        )


class MitigationInfo(BaseModel):
    target: QubitMitigationInfo
    ancilla: QubitMitigationInfo


class ResultForCircuit(BaseModel):
    name: str
    histogram: SynchronousHistogram
    mitigation_info: Optional[MitigationInfo]
    mitigated_histogram: Optional[Any]


class SingleResult(BaseModel):
    target: Qubit
    ancilla: Qubit
    phi: float
    results_per_circuit: List[ResultForCircuit]


class BatchResult(BaseModel):
    job_id: str
    keys: Sequence[Tuple[int, int, str, float]]


class FourierDiscriminationSyncResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    data: List[SingleResult]


class FourierDiscriminationAsyncResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    data: List[BatchResult]
