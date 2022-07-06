from pydantic import BaseModel
from typing import List


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


class QubitsDescription(BaseModel):
    qubits: List[PairOfQubitsDescription]


class ExperimentDescription(BaseModel):
    type: str
    qubits: list  # does not work if I write QubitsDescription
    angle: AngleDescription
    method: str
    number_of_shots: int


class ResultDescription(BaseModel):
    pass
