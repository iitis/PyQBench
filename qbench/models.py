from pydantic import BaseModel


class DeviceDescription(BaseModel):
    anr: str
    disable_qubit_rewiring: bool
    gateset: str

class ExperimentDescription(BaseModel):
    type: str
    qubits: list 
    angle: dict 
    method: str
    number_of_shots: int

class QubitsDescription(BaseModel):
    pass

class AngleDescription(BaseModel):
    start: float
    stop: float
    number_of_steps: int

class ResultDescription(BaseModel):
    pass
    