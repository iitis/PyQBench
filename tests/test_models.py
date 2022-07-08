import pytest
from pydantic import ValidationError, parse_obj_as

from qbench.models import (
    ARN,
    AnglesRange,
    AWSDeviceDescription,
    FourierDiscriminationExperiment,
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


class TestAWSDeviceDescription:
    def test_disable_qubit_rewiring_is_optional_and_false_by_default(self):
        input = {
            "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
        }

        description = AWSDeviceDescription(**input)
        assert description.arn == input["arn"]
        assert not description.disable_qubit_rewiring

    def test_can_be_parsed_from_full_input(self):
        input = {
            "arn": "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy",
            "disable_qubit_rewiring": True,
        }

        description = AWSDeviceDescription(**input)
        assert description.arn == input["arn"]
        assert description.disable_qubit_rewiring

    @pytest.mark.parametrize("input", [{"disable-qubit-rewiring": True}])
    def test_cannot_be_parsed_if_arn_is_missing(self, input):
        with pytest.raises(ValidationError):
            AWSDeviceDescription(**input)


class TestFourierDiscriminationExperiment:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "num_steps": 3},
                "method": method,
                "num_shots": 5,
            }
            for method in ("postselection", "direct_sum")
        ],
    )
    def test_can_be_parsed_from_correct_input(self, input):
        description = FourierDiscriminationExperiment(**input)
        assert description.type == input["type"]

    def test_fails_to_validate_if_qubit_index_is_not_integral(self):
        input = {
            "type": "fourier_discrimination",
            "qubits": [{"target": 0, "ancilla": 1.0}, {"target": 5, "ancilla": 2}],
            "angle": {"start": 0, "stop": 4, "num_steps": 3},
            "method": "direct_sum",
            "num_shots": 5,
        }

        with pytest.raises(ValidationError):
            FourierDiscriminationExperiment(**input)

    @pytest.mark.parametrize(
        "input",
        [
            {
                "type": "fourier_discrimination",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "num_steps": 3},
                "method": "postselection",
            },
            {
                "type": "fourier_discrimination",
                "gateset": "rigetti",
                "qubits": [{"target": 0, "ancilla": 1.5}, {"target": 5, "ancilla": 2}],
                "angle": {"start": 0, "stop": 4, "num_steps": 3},
                "number_of_shots": 5,
            },
            {
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 5}],
                "angle": {"start": 0, "stop": 4, "num_steps": 3},
                "method": "postselection",
                "number_of_shots": 5,
            },
        ],
    )
    def test_fails_to_validate_if_some_fields_are_missing(self, input):
        with pytest.raises(ValidationError):
            FourierDiscriminationExperiment(**input)

    def test_fails_to_validate_if_experiment_type_is_different_from_fourier_discrimination(self):
        input = {
            "type": "fourier",
            "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
            "angle": {"start": 0, "stop": 4, "num_steps": 3},
            "method": "postselection",
            "number_of_shots": 5,
        }

        with pytest.raises(ValidationError):
            FourierDiscriminationExperiment(**input)

    def test_fails_to_validate_if_method_is_unknown(self):
        input = {
            "type": "fourier",
            "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
            "angle": {"start": 0, "stop": 4, "number_of_steps": 3},
            "method": "unknown-method",
            "number_of_shots": 5,
        }

        with pytest.raises(ValidationError):
            FourierDiscriminationExperiment(**input)

    def test_cannot_be_parsed_if_there_are_duplicate_qubit_pairs(self):
        input = {
            "type": "fourier_discrimination",
            "qubits": [
                {"target": 5, "ancilla": 3},
                {"target": 5, "ancilla": 4},
                {"target": 5, "ancilla": 4},
            ],
            "angle": {"start": 1, "stop": 1, "num_steps": 5},
            "method": "postselection",
            "number_of_shots": 5,
        }
        with pytest.raises(ValidationError):
            FourierDiscriminationExperiment(**input)


class TestAnglesRange:
    @pytest.mark.parametrize("input", [{"start": 0, "stop": 4, "num_steps": 3}])
    def test_can_be_parsed_from_correct_input(self, input):
        description = AnglesRange(**input)
        assert description.start == input["start"]
        assert description.stop == input["stop"]

    def test_degenerate_range_can_contain_only_one_angle(self):
        angle_range = AnglesRange(start=10, stop=10, num_steps=1)
        assert angle_range.stop == angle_range.start == 10
        assert angle_range.num_steps == 1

        with pytest.raises(ValidationError):
            AnglesRange(start=10, stop=10, num_steps=2)
