from typing import List, Literal

from pydantic import BaseModel, conint, root_validator
from typing_extensions import Annotated

Qubit = Annotated[int, conint(strict=True, ge=0)]
PositiveInt = Annotated[int, conint(strict=True, ge=1)]


class DeviceDescription(BaseModel):
    arn: str
    disable_qubit_rewiring: bool
    gateset: str


class AngleDescription(BaseModel):
    start: float
    stop: float
    number_of_steps: PositiveInt

    @root_validator
    def check_if_start_smaller_than_stop(cls, values):
        if values.get("start") > values.get("stop"):
            raise ValueError("Start cannot be smallet than stop.")
        return values

    @root_validator
    def check_if_number_of_steps_is_one_when_start_equals_stop(cls, values):
        if (values.get("start") == values.get("stop")) and values.get("number_of_steps") != 1:
            raise ValueError("There can be only one step if start equals stop.")
        return values


class PairOfQubits(BaseModel):
    target: Qubit
    ancilla: Qubit

    @root_validator
    def check_qubits_differ(cls, values):
        if values.get("target") == values.get("ancilla"):
            raise ValueError("Target and ancilla need to have different indices.")
        return values


class ExperimentDescription(BaseModel):
    type: str
    qubits: List[PairOfQubits]
    angle: AngleDescription
    method: str
    number_of_shots: PositiveInt

    @root_validator
    def check_if_all_pairs_of_qubits_are_different(cls, values):
        list_of_qubits = [(qubits.target, qubits.ancilla) for qubits in values.get("qubits", [])]
        if len(set(list_of_qubits)) != len(list_of_qubits):
            raise ValueError("No to pairs of qubits should be exactly the same.")
        return values


class ResultForSigleAngle(BaseModel):
    phi: float
    counts: dict


class SingleResult(BaseModel):
    target: Qubit
    ancilla: Qubit
    measurement_counts: List[ResultForSigleAngle]


class ResultFourierDescription(BaseModel):
    method: Literal["direct", "postselection"]
    number_of_shots: PositiveInt
    results: List[SingleResult]
