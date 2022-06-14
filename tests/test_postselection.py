import numpy as np
import pytest
from braket import devices

from qbench.fourier import FourierCircuits
from qbench.postselection import benchmark_using_postselection


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
@pytest.mark.parametrize("native_only", [False, True])
def test_computed_discrimination_probability_is_feasible(phi: float, native_only):
    device = devices.LocalSimulator()
    circuits = FourierCircuits(phi=phi, native_only=native_only)

    probability = benchmark_using_postselection(
        device=device,
        target=0,
        ancilla=1,
        state_preparation=circuits.state_preparation,
        basis_change=circuits.unitary_to_discriminate,
        v0=circuits.v0_dag,
        v1=circuits.v1_dag,
        num_shots_per_measurement=20,
    )

    assert 0 <= probability <= 1
