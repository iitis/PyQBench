"""Models for all backend descriptions."""
import os
from importlib import import_module
from typing import Any, Dict, List, Optional, Union

from pydantic import Extra, Field, validator
from qiskit import IBMQ

from qbench.models import BaseModel


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


class BackendDescriptionRoot(BaseModel):
    __root__: BackendDescription


class IbMQJObDescription(BaseModel):
    ibmq_job_id: str
