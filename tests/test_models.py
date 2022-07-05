from pydantic import ValidationError
import pytest
from qbench.models import DeviceDescription, ExperimentDescription, QubitsDescription, AngleDescription, ResultDescription


class TestDeviceDescription:

    @pytest.mark.parametrize(
        "input",
        [
            {"arn": "test", "disable-qubit-rewiring": False, "gateset": "rigetti"}
        ]
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = DeviceDescription(**input)
        assert description.arn == input["arn"]

    @pytest.mark.parametrize(
        "input",
        [
            {"disable-qubit-rewiring": True}
        ]
    )
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            DeviceDescription(**input)

class TestExperimentDescription:

    @pytest.mark.parametrize(
        "input",
        [
            {
                "type": "fourier_discrimination", 
                "qubits": [
                    {"target": 0, "ancilla": 1},
                    {"target": 5, "ancilla": 2}
                ],
                "angle": {
                    "start": 0,
                    "stop": 4,
                    "number_of_points": 3
                },
                "method": "postselection",
                "number_of_shots": 5
            }
        ]
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = ExperimentDescription(**input)
        assert description.type == input["type"]

    @pytest.mark.parametrize(
        "input",
        [
            {"disable-qubit-rewiring": True}
        ]
    )
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            ExperimentDescription(**input)

class TestQubitDescription:
    pass

class TestAngleDescription:

    @pytest.mark.parametrize(
        "input",
        [
            {
                "start": 0, 
                "stop": 4,
                "number_of_steps": 3 
            }
        ]
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = AngleDescription(input)
        assert description.stop == input["stop"]

    @pytest.mark.parametrize(
        "input",
        [
            {
                "number_of_steps": 3 
            }
        ]
    )
    def test_can_be_parsed_from_correct_input(self, input):
        with pytest.raises(ValidationError):
            AngleDescription(**input)