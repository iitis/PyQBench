from typing import List

from pydantic import BaseModel, conint, root_validator

Qubit = conint(strict=True, ge=0)


class DeviceDescription(BaseModel):
    arn: str
    disable_qubit_rewiring: bool
    gateset: str


class AngleDescription(BaseModel):
    start: float
    stop: float
    number_of_steps: int


class PairOfQubitsDescription(BaseModel):
    target: Qubit  # type: ignore
    ancilla: Qubit  # type: ignore

    @root_validator
    def check_qubits_differ(cls, values):
        if values.get("target") == values.get("ancilla"):
            raise ValueError("Target and ancilla need to have different indices.")
        return values


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
    target: Qubit  # type: ignore
    ancilla: Qubit  # type: ignore
    measurement_counts: List[ResultForSigleAngle]


class ResultDescription(BaseModel):
    method: str
    number_of_shots: int
    results: List[SingleResult]
