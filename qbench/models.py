import re
from typing import List, Literal, Optional

from pydantic import (
    BaseModel,
    ConstrainedInt,
    PositiveInt,
    StrictStr,
    root_validator,
    validator,
)


class Qubit(ConstrainedInt):
    strict = True
    ge = 0


class ARN(StrictStr):
    regex = re.compile(r"^arn(:[A-Za-z\d\-_]*){5}(/[A-Za-z\d\-_]*)+$")


class StrictPositiveInt(ConstrainedInt):
    strict = True
    gt = 0


class AWSDeviceDescription(BaseModel):
    arn: str
    disable_qubit_rewiring: bool = False


class AnglesRange(BaseModel):
    start: float
    stop: float
    number_of_steps: StrictPositiveInt

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

    @root_validator(skip_on_failure=True)
    def check_qubits_differ(cls, values):
        if values["target"] == values["ancilla"]:
            raise ValueError("Target and ancilla need to have different indices.")
        return values


class FourierDiscriminationExperiment(BaseModel):
    type: str
    qubits: List[PairOfQubits]
    angle: AnglesRange
    gateset: Optional[str]
    method: Literal["direct_sum", "postselection"]
    number_of_shots: StrictPositiveInt

    @validator("qubits")
    def check_if_all_pairs_of_qubits_are_different(cls, qubits):
        list_of_qubits = [(qubits.target, qubits.ancilla) for qubits in qubits]
        if len(set(list_of_qubits)) != len(list_of_qubits):
            raise ValueError("No to pairs of qubits should be exactly the same.")
        return qubits


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
