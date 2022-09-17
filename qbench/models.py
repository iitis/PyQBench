import os
import re
from importlib import import_module
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConstrainedInt, Extra, Field, StrictStr, root_validator, validator
from qiskit import IBMQ

from ._expressions import eval_expr


class BaseModel(PydanticBaseModel):
    class Config:
        extra = "forbid"


def _parse_arithmetic_expression(expr):
    if isinstance(expr, (float, int)):
        return expr
    try:
        return eval_expr(expr)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid expression: {expr}") from e


def _check_is_correct_object_path(path):
    parts = path.split(":")

    if len(parts) != 2:
        raise ValueError("Incorrect provider format. Expected precisely one colon.")

    module_path, obj_name = parts

    if not all(s.isidentifier() for s in module_path.split(".")):
        raise ValueError("Incorrect module's fully qualified path.")

    if not obj_name.isidentifier():
        raise ValueError("Incorrect class name.")

    return path


def _import_object(object_spec):
    module_path, obj_name = object_spec.split(":")
    module = import_module(module_path)
    return getattr(module, obj_name)


class SimpleBackendDescription(BaseModel, extra=Extra.forbid):
    provider: str
    name: str
    run_options: Dict[str, Any] = Field(default_factory=dict)

    _verify_provider = validator("provider", allow_reuse=True)(_check_is_correct_object_path)

    @property
    def asynchronous(self) -> bool:
        return False

    def create_backend(self):
        provider = _import_object(self.provider)()
        return provider.get_backend(self.name)


class BackendFactoryDescription(BaseModel):
    factory: str
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)  # type: ignore
    run_options: Dict[str, Any] = Field(default_factory=dict)

    _verify_factory = validator("factory", allow_reuse=True)(_check_is_correct_object_path)

    @property
    def asynchronous(self):
        return False

    def create_backend(self):
        factory = _import_object(self.factory)
        return factory(*self.args, **self.kwargs)

    # This is only to satisfy MyPy plugin
    class Config:
        extra = "forbid"


class IBMQProviderDescription(BaseModel):
    group: Optional[str]
    hub: Optional[str]
    project: Optional[str]


class IBMQBackendDescription(BaseModel):
    name: str
    asynchronous: bool = False
    provider: IBMQProviderDescription

    def create_backend(self):
        provider = IBMQ.enable_account(
            os.getenv("IBMQ_TOKEN"),
            hub=self.provider.hub,
            group=self.provider.group,
            project=self.provider.project,
        )
        return provider.get_backend(self.name)


BackendDescription = Union[
    SimpleBackendDescription, BackendFactoryDescription, IBMQBackendDescription
]


class Qubit(ConstrainedInt):
    strict = True
    ge = 0


class TwoQubitBitstring(StrictStr):
    regex = re.compile("^[01]{2}$")


class StrictPositiveInt(ConstrainedInt):
    strict = True
    gt = 0


class AnglesRange(BaseModel):
    start: float
    stop: float
    num_steps: StrictPositiveInt

    validate_start = validator("start", allow_reuse=True, pre=True)(_parse_arithmetic_expression)
    validate_stop = validator("stop", allow_reuse=True, pre=True)(_parse_arithmetic_expression)

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


SynchronousHistogram = Dict[TwoQubitBitstring, StrictPositiveInt]


class IbMQJObDescription(BaseModel):
    ibmq_job_id: str


class ResultForAngle(BaseModel):
    phi: float
    histogram: Union[SynchronousHistogram, IbMQJObDescription]


class SingleResult(BaseModel):
    target: Qubit
    ancilla: Qubit
    measurement_counts: List[ResultForAngle]


class FourierDiscriminationMetadata(BaseModel):
    experiment: FourierDiscriminationExperiment
    backend_description: BackendDescription


class FourierDiscriminationResult(BaseModel):
    metadata: FourierDiscriminationMetadata
    results: List[SingleResult]
