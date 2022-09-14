from pathlib import Path

import pytest
from pydantic import ValidationError, parse_obj_as
from qiskit.providers.aer import AerProvider
from qiskit_braket_provider import BraketLocalBackend
from yaml import safe_load

from qbench.models import (
    ARN,
    AnglesRange,
    AWSDeviceDescription,
    BackendFactoryDescription,
    FourierDiscriminationExperiment,
    ResultForAngle,
    SimpleBackendDescription,
)

WORK_DIR = Path.cwd()


class TestSimpleBackendDescription:
    @pytest.mark.parametrize(
        "provider",
        [
            "this is not a good provider specs",
            "provider.path:test:xyz",
            "1provider.path:Provider",
            "provider:2Provider",
            "provider.path:Provider)",
        ],
    )
    def test_does_not_validate_if_provider_string_is_incorrectly_formatted(self, provider):
        with pytest.raises(ValidationError):
            SimpleBackendDescription(provider=provider, name="lucy")

    @pytest.mark.parametrize(
        "description, backend_name",
        [
            (
                BackendFactoryDescription(
                    factory="qiskit_braket_provider:BraketLocalBackend", args=("braket_sv",)
                ),
                "braket_sv",
            ),
            (
                BackendFactoryDescription(
                    factory="qiskit_braket_provider:BraketLocalBackend",
                    kwargs={"name": "braket_dm"},
                ),
                "braket_dm",
            ),
        ],
    )
    def test_braket_local_backend_created_from_factory_description_has_correct_name(
        self, description, backend_name
    ):
        backend = description.create_backend()
        assert isinstance(backend, BraketLocalBackend)
        assert backend.name == "sv_simulator"
        assert backend.backend_name == backend_name


class TestBackendFactoryDescription:
    @pytest.mark.parametrize(
        "factory",
        [
            "this is not a good factory specs",
            "factory.path:test:xyz",
            "1factory.path:some_factory",
            "provider:2Factory",
            "provider.path:Factory:factory)",
        ],
    )
    def test_does_not_validate_if_factory_path_string_is_incorrectly_formatted(self, factory):
        with pytest.raises(ValidationError):
            BackendFactoryDescription(factory=factory, args=("BraketLocalBackend",))

    @pytest.mark.parametrize(
        "provider, name, provider_cls",
        [
            ("qiskit.providers.aer:AerProvider", "aer_simulator", AerProvider),
        ],
    )
    def test_backend_created_from_description_has_correct_name_and_provider(
        self, provider, name, provider_cls
    ):
        backend = SimpleBackendDescription(provider=provider, name=name).create_backend()

        assert backend.name() == name
        assert isinstance(backend.provider(), provider_cls)


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


class TestResultForAngle:
    @pytest.mark.parametrize(
        "input",
        [
            {"phi": 0.1, "counts": {"111": 20, "01": 5}},
            {"phi": 0.2, "counts": {"xyz": 20, "01": 5}},
        ],
    )
    def test_fails_to_validate_if_counts_does_not_contain_two_qubit_bitstrings_only(self, input):
        with pytest.raises(ValidationError):
            ResultForAngle(**input)


class TestExampleYamlInputsAreMatchingModels:
    def test_fourier_discrimination_experiment_input_matches_model(self):
        path = WORK_DIR / "../examples/fourier-discrimination-experiment.yml"
        with open(path) as f:
            data = safe_load(f)
            FourierDiscriminationExperiment(**data)
