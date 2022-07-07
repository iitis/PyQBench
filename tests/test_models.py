import pytest
from pydantic import ValidationError

from qbench.models import (
    AngleDescription,
    DeviceDescription,
    ExperimentDescription,
    ResultFourierDescription,
)


class TestDeviceDescription:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
                "disable_qubit_rewiring": False,
                "gateset": "lucy",
            },
            {
                "arn": "arn:aws:braket:::device/quantum-simulator/amazon/tn1",
                "disable_qubit_rewiring": True,
                "gateset": "rigetti",
            },
            {
                "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
                "disable_qubit_rewiring": False,
            },
            {"arn": "arn:aws:braket:::device/quantum-simulator/amazon/tn1", "gateset": "rigetti"},
            {"arn": "arn:aws:braket:::device/quantum-simulator/amazon/tn1"},
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = DeviceDescription(**input)
        assert description.arn == input["arn"]

    @pytest.mark.parametrize("input", [{"disable-qubit-rewiring": True}])
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            DeviceDescription(**input)


class TestExperimentDescription:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                "method": "postselection",
                "number_of_shots": 5,
            }
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = ExperimentDescription(**input)
        assert description.type == input["type"]

    @pytest.mark.parametrize(
        "input",
        [
            {"disable-qubit-rewiring": True},
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": "test", "ancilla": 1}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                "method": "postselection",
                "number_of_shots": 5,
            },
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1.5}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                "method": "postselection",
                "number_of_shots": 5,
            },
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 5}],
                "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                "method": "postselection",
                "number_of_shots": 5,
            },
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 4}],
                "angle": {"start": 4, "stop": 1, "number_of_steps": 3},
                "method": "postselection",
                "number_of_shots": 5,
            },
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 4}],
                "angle": {"start": 1, "stop": 1, "number_of_steps": 0},
                "method": "postselection",
                "number_of_shots": 5,
            },
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 4}],
                "angle": {"start": 1, "stop": 1, "number_of_steps": 5},
                "method": "postselection",
                "number_of_shots": 5,
            },
            {
                "type": "fourier_discrimination",
                "qubits": [
                    {"target": 5, "ancilla": 3},
                    {"target": 5, "ancilla": 4},
                    {"target": 5, "ancilla": 4},
                ],
                "angle": {"start": 1, "stop": 1, "number_of_steps": 5},
                "method": "postselection",
                "number_of_shots": 5,
            },
        ],
    )
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            ExperimentDescription.parse_obj(input)


class TestAngleDescription:
    @pytest.mark.parametrize("input", [{"start": 0, "stop": 4, "number_of_steps": 3}])
    def test_can_be_parsed_from_correct_input(self, input):
        description = AngleDescription(**input)
        assert description.stop == input["stop"]

    @pytest.mark.parametrize("input", [{"number_of_steps": 3}])
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            AngleDescription(**input)


class TestResultFourierDescription:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "method": "postselection",
                "number_of_shots": 100,
                "results": [
                    {
                        "target": 0,
                        "ancilla": 1,
                        "measurement_counts": [
                            {"phi": 0.1, "counts": {"00": 10, "11": 2}},
                            {"phi": 0.2, "counts": {"00": 10, "11": 2}},
                        ],
                    },
                    {
                        "target": 4,
                        "ancilla": 3,
                        "measurement_counts": [{"phi": 0.5, "counts": {"01": 14, "1": 14}}],
                    },
                ],
            }
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = ResultFourierDescription(**input)
        assert description.results == input["results"]

    @pytest.mark.parametrize(
        "input",
        [
            {"number_of_shots": 3},
            {
                "method": "some_method",
                "number_of_shots": 100,
                "results": [
                    {
                        "target": 0,
                        "ancilla": 1,
                        "measurement_counts": [
                            {"phi": 0.1, "counts": {"00": 10, "11": 2}},
                            {"phi": 0.2, "counts": {"00": 10, "11": 2}},
                        ],
                    },
                    {
                        "target": 4,
                        "ancilla": 3,
                        "measurement_counts": [{"phi": 0.5, "counts": {"01": 14, "1": 14}}],
                    },
                ],
            },
        ],
    )
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            ResultFourierDescription(**input)
