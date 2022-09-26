from typing import Dict, List, Literal, Optional, Tuple, Union

from pydantic import validator

from ..common_models import (
    AnglesRange,
    BackendDescription,
    BaseModel,
    IBMQJobDescription,
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


class ResultForAngle(BaseModel):
    phi: float
    histograms: Dict[str, SynchronousHistogram]


class SingleResult(BaseModel):
    target: Qubit
    ancilla: Qubit
    measurement_counts: List[ResultForAngle]


class BatchResult(BaseModel):
    job: IBMQJobDescription
    keys: List[Tuple[int, int, str, float]]


class FourierDiscriminationResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    results: Union[List[SingleResult], List[BatchResult]]
