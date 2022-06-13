import numpy as np
import pytest
from braket import devices

from qbench import fourier
from qbench.postselection import benchmark_using_postselection


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
@pytest.mark.parametrize("native_only", [False, True])
def test_computed_discrimination_probability_is_feasible(phi: float, native_only):
    device = devices.LocalSimulator()

    probability = benchmark_using_postselection(
        device=device,
        target=0,
        ancilla=1,
        state_preparation=fourier.state_preparation,
        basis_change=fourier.unitary_to_discriminate(phi),
        v0=fourier.v0_dag(phi, native_only=native_only),
        v1=fourier.v1_dag(phi, native_only=native_only),
        num_shots_per_measurement=20,
    )

    assert 0 <= probability <= 1
