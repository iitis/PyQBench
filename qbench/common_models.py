import re
from typing import Dict, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConstrainedInt, StrictStr, root_validator, validator

from ._expressions import eval_expr
from .backend_models import IbMQJObDescription


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


SynchronousHistogram = Dict[TwoQubitBitstring, StrictPositiveInt]


class ResultForAngle(BaseModel):
    phi: float
    histograms: Dict[str, Union[SynchronousHistogram, IbMQJObDescription]]
