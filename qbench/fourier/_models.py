from typing import List, Literal, Optional, Tuple

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


class FourierDiscriminationExperiment(BaseModel):
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


class FourierDiscriminationMetadata(BaseModel):
    experiment: FourierDiscriminationExperiment
    backend_description: BackendDescription


class QubitMitigationInfo(BaseModel):
    prob_meas0_prep1: float
    prob_meas1_prep0: float


class MitigationInfo(BaseModel):
    target: QubitMitigationInfo
    ancilla: QubitMitigationInfo


class ResultForCircuit(BaseModel):
    name: str
    histogram: SynchronousHistogram
    mitigation_info: Optional[MitigationInfo]


class SingleResult(BaseModel):
    target: Qubit
    ancilla: Qubit
    phi: float
    results_per_circuit: List[ResultForCircuit]


class BatchResult(BaseModel):
    job_id: str
    keys: List[Tuple[int, int, str, float]]


class FourierDiscriminationSyncResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    results: List[SingleResult]


class FourierDiscriminationAsyncResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    results: List[BatchResult]
