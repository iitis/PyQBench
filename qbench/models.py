from typing import List

from pydantic import BaseModel


class DeviceDescription(BaseModel):
    arn: str
    disable_qubit_rewiring: bool
    gateset: str


class AngleDescription(BaseModel):
    start: float
    stop: float
    number_of_steps: int


class PairOfQubitsDescription(BaseModel):
    target: int
    ancilla: int


class ExperimentDescription(BaseModel):
    type: str
    qubits: List[PairOfQubitsDescription]
    angle: AngleDescription
    method: str
    number_of_shots: int


class ResultForSigleAngle(BaseModel):
    phi: float
    counts: dict


class SingleResult(BaseModel):
    target: int
    ancilla: int
    measurement_counts: List[ResultForSigleAngle]


class ResultDescription(BaseModel):
    method: str
    number_of_shots: int
    results: List[SingleResult]
