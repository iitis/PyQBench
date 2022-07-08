import pytest
from pydantic import ValidationError, parse_obj_as

from qbench.models import (
    ARN,
    AnglesRange,
    AWSDeviceDescription,
    FourierDiscriminationExperiment,
    FourierDiscriminationResult,
)


class TestARNValidation:
    @pytest.mark.parametrize(
        "input",
        [
            "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
            "arn:aws:braket:::device/quantum-simulator/amazon/tn1",
            "arn:aws:braket:::device/quantum-simulator/amazon/dm1",
            "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6",
            "arn:aws:braket:::device/qpu/d-wave/Advantage_system4",
            "arn:aws:braket:us-west-2::device/qpu/d-wave/Advantage_system6",
            "arn:aws:braket:::device/qpu/ionq/ionQdevice",
            "arn:aws:braket:::device/qpu/rigetti/Aspen-11",
            "arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-1",
            "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        assert parse_obj_as(ARN, input) == input

    @pytest.mark.parametrize(
        "input",
        [
            "test",
            "xyz:definitely:not/arn",
            "arn:aws:braket::device/quantum-simulator/amazon/sv1",
            "arn:aws:braket:device/quantum-simulator/amazon/sv1",
        ],
    )
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            parse_obj_as(ARN, input)


class TestDeviceDescription:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
                "disable_qubit_rewiring": False,
            },
            {
                "arn": "arn:aws:braket:::device/quantum-simulator/amazon/tn1",
                "disable_qubit_rewiring": True,
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
        description = AWSDeviceDescription(**input)
        assert description.arn == input["arn"]
        assert description.disable_qubit_rewiring == input.get("disable_qubit_rewiring", False)

    @pytest.mark.parametrize("input", [{"disable-qubit-rewiring": True}])
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            AWSDeviceDescription(**input)


class TestExperimentDescription:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                "method": method,
                "number_of_shots": 5,
            }
            for method in ("postselection", "direct_sum")
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = FourierDiscriminationExperiment(**input)
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
                "gateset": "rigetti",
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
            FourierDiscriminationExperiment(**input)


class TestAngleDescription:
    @pytest.mark.parametrize("input", [{"start": 0, "stop": 4, "number_of_steps": 3}])
    def test_can_be_parsed_from_correct_input(self, input):
        description = AnglesRange(**input)
        assert description.stop == input["stop"]

    @pytest.mark.parametrize("input", [{"number_of_steps": 3}])
    def test_cannot_be_parsed_from_incorrect_input(self, input):
        with pytest.raises(ValidationError):
            AnglesRange(**input)


class TestResultFourierDescription:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "metadata": {
                    "experiment": {
                        "type": "fourier_discrimination",
                        "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                        "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                        "method": "postselection",
                        "number_of_shots": 5,
                    },
                    "device_description": {
                        "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
                        "disable_qubit_rewiring": False,
                    },
                },
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
                        "measurement_counts": [{"phi": 0.5, "counts": {"01": 14, "01": 14}}],
                    },
                ],
            }
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = FourierDiscriminationResult(**input)
        assert description.results == input["results"]

    @pytest.mark.parametrize(
        "input",
        [
            {
                "metadata": {
                    "experiment": {
                        "type": "fourier_discrimination",
                        "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                        "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
                        "method": "postselection",
                        "number_of_shots": 5,
                    },
                    "device": {
                        "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
                        "disable_qubit_rewiring": False,
                    },
                },
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
            FourierDiscriminationResult(**input)
