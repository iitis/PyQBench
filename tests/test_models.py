from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError
from qiskit.providers.aer import AerProvider
from qiskit_braket_provider import BraketLocalBackend
from yaml import safe_load

from qbench.models import (
    AnglesRange,
    BackendFactoryDescription,
    FourierDiscriminationExperiment,
    FourierDiscriminationResult,
    IBMQBackendDescription,
    ResultForAngle,
    SimpleBackendDescription,
)

EXAMPLES_PATH = Path(__file__).parent / "../examples"


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


class TestFourierDiscriminationExperiment:
    @pytest.mark.parametrize(
        "input",
        [
            {
                "type": "discrimination-fourier",
                "qubits": [{"target": 0, "ancilla": 1}, {"target": 5, "ancilla": 2}],
                "angles": {"start": 0, "stop": 4, "num_steps": 3},
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

    def test_start_and_stop_can_contain_arithmetic_expression_with_pi(self):
        angles_range = AnglesRange(start="2 * pi", stop="3 * pi", num_steps=10)
        assert angles_range.start == 2 * np.pi
        assert angles_range.stop == 3 * np.pi
        assert angles_range.num_steps == 10


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
        path = EXAMPLES_PATH / "fourier-discrimination-experiment.yml"
        with open(path) as f:
            data = safe_load(f)
            FourierDiscriminationExperiment(**data)

    @pytest.mark.parametrize(
        "filename", ["simple-backend.yml", "simple-backend-with-run-options.yml"]
    )
    def test_simple_backend_input_matches_model(self, filename):
        path = EXAMPLES_PATH / filename
        with open(path) as f:
            data = safe_load(f)
            SimpleBackendDescription(**data)

    @pytest.mark.parametrize(
        "filename", ["backend-factory.yml", "backend-factory-with-run-options.yml"]
    )
    def test_backend_factory_input_matches_model(self, filename):
        path = EXAMPLES_PATH / filename
        with open(path) as f:
            data = safe_load(f)
            BackendFactoryDescription(**data)

    def test_fourier_discrimination_result_matches_model(self):
        path = EXAMPLES_PATH / "fourier-discrimination-result.yml"
        with open(path) as f:
            data = safe_load(f)
            FourierDiscriminationResult(**data)

    def test_fourier_discrimination_async_result_matches_model(self):
        path = EXAMPLES_PATH / "fourier-discrimination-async-result.yml"
        with open(path) as f:
            data = safe_load(f)
            FourierDiscriminationResult(**data)

    def tests_ibmq_backend_input_matches_model(self):
        path = EXAMPLES_PATH / "ibmq-backend.yml"
        with open(path) as f:
            data = safe_load(f)
            IBMQBackendDescription(**data)
