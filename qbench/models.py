import re
from importlib import import_module
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConstrainedInt, StrictStr, root_validator, validator


class SimpleBackendDescription(BaseModel):
    provider: str
    name: str

    @validator("provider")
    def check_if_provider_comprises_fully_qualified_path_and_class_name(cls, provider):
        parts = provider.split(":")

        if len(parts) != 2:
            raise ValueError("Incorrect provider format. Expected precisely one colon.")

        module_path, cls_name = parts

        if not all(s.isidentifier() for s in module_path.split(".")):
            raise ValueError("Incorrect module's fully qualified path.")

        if not cls_name.isidentifier():
            raise ValueError("Incorrect class name.")

        return provider

    def create_backend(self):
        module_path, cls_name = self.provider.split(":")
        module = import_module(module_path)
        provider = getattr(module, cls_name)()
        return provider.get_backend(self.name)


class Qubit(ConstrainedInt):
    strict = True
    ge = 0


class ARN(StrictStr):
    regex = re.compile(r"^arn(:[A-Za-z\d\-_]*){5}(/[A-Za-z\d\-_]*)+$")


class TwoQubitBitstring(StrictStr):
    regex = re.compile("^[01]{2}$")


class StrictPositiveInt(ConstrainedInt):
    strict = True
    gt = 0


class AWSDeviceDescription(BaseModel):
    arn: str
    disable_qubit_rewiring: bool = False


class AnglesRange(BaseModel):
    start: float
    stop: float
    num_steps: StrictPositiveInt

    @root_validator
    def check_if_start_smaller_than_stop(cls, values):
        if values.get("start") > values.get("stop"):
            raise ValueError("Start cannot be smallet than stop.")
        return values

    @root_validator
    def check_if_number_of_steps_is_one_when_start_equals_stop(cls, values):
        if (values.get("start") == values.get("stop")) and values.get("num_steps") != 1:
            raise ValueError("There can be only one step if start equals stop.")
        return values


class QubitsPair(BaseModel):
    target: Qubit
    ancilla: Qubit

    @root_validator(skip_on_failure=True)
    def check_qubits_differ(cls, values):
        if values["target"] == values["ancilla"]:
            raise ValueError("Target and ancilla need to have different indices.")
        return values


class FourierDiscriminationExperiment(BaseModel):
    type: Literal["fourier_discrimination"]
    qubits: List[QubitsPair]
    angle: AnglesRange
    gateset: Optional[str]
    method: Literal["direct_sum", "postselection"]
    num_shots: StrictPositiveInt

    @validator("qubits")
    def check_if_all_pairs_of_qubits_are_different(cls, qubits):
        list_of_qubits = [(qubits.target, qubits.ancilla) for qubits in qubits]
        if len(set(list_of_qubits)) != len(list_of_qubits):
            raise ValueError("All pairs of qubits should be distinct.")
        return qubits


class ResultForAngle(BaseModel):
    phi: float
    counts: Dict[TwoQubitBitstring, StrictPositiveInt]


class SingleResult(BaseModel):
    target: Qubit
    ancilla: Qubit
    measurement_counts: List[ResultForAngle]
    measured_qubits: List[Qubit]


class FourierDiscriminationMetadata(BaseModel):
    experiment: FourierDiscriminationExperiment
    device_description: AWSDeviceDescription


class FourierDiscriminationResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    results: List[SingleResult]
