import re
from importlib import import_module
from typing import Any, Dict, List, Optional, Union

from pydantic.v1 import BaseModel as PydanticBaseModel
from pydantic.v1 import ConstrainedInt, Field, StrictStr, root_validator, validator
from qiskit.circuit import Parameter
from qiskit.providers import BackendV1, BackendV2
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

from qbench._expressions import eval_expr

AnyParameter = Union[float, Parameter]


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
            raise ValueError("Start cannot be smaller than stop.")
        return values

    @root_validator
    def check_if_number_of_steps_is_one_when_start_equals_stop(cls, values):
        if (values.get("start") == values.get("stop")) and values.get("num_steps") != 1:
            raise ValueError("There can be only one step if start equals stop.")
        return values


class Delta(BaseModel):
    delta: Any


class QubitsPair(BaseModel):
    target: Qubit
    ancilla: Qubit

    @root_validator(skip_on_failure=True)
    def check_qubits_differ(cls, values):
        if values["target"] == values["ancilla"]:
            raise ValueError("Target and ancilla need to have different indices.")
        return values


SynchronousHistogram = Dict[TwoQubitBitstring, StrictPositiveInt]


def _import_object(object_spec):
    module_path, obj_name = object_spec.split(":")
    module = import_module(module_path)
    return getattr(module, obj_name)


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


class SimpleBackendDescription(BaseModel):
    provider: str
    name: str
    run_options: Dict[str, Any] = Field(default_factory=dict)
    asynchronous: bool = False

    _verify_provider = validator("provider", allow_reuse=True)(_check_is_correct_object_path)

    def create_backend(self):
        provider = _import_object(self.provider)()
        return provider.get_backend(self.name)


class BackendFactoryDescription(BaseModel):
    factory: str
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)  # type: ignore
    run_options: Dict[str, Any] = Field(default_factory=dict)
    asynchronous: bool = False

    _verify_factory = validator("factory", allow_reuse=True)(_check_is_correct_object_path)

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
        service = QiskitRuntimeService(
            channel="ibm_quantum",
            instance=f"{self.provider.hub}/{self.provider.group}/{self.provider.project}",
        )

        return service.backend(name=self.name)

        # TODO finish!
        # exit(-1)


class AerBackendDescription(BaseModel):
    name: str
    asynchronous: bool = False

    def create_backend(self):
        return AerSimulator()


BackendDescription = Union[
    SimpleBackendDescription,
    BackendFactoryDescription,
    IBMQBackendDescription,
    AerBackendDescription,
]


class BackendDescriptionRoot(BaseModel):
    __root__: BackendDescription


Backend = Union[BackendV1, BackendV2]
MeasurementsDict = Dict[str, int]
