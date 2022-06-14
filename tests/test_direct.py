import numpy as np
import pytest
from braket import devices

from qbench.direct import benchmark_using_controlled_unitary
from qbench.fourier import FourierCircuits


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 100))
@pytest.mark.parametrize("native_only", [False, True])
def test_computed_discrimination_probability_is_feasible(phi: float, native_only):
    device = devices.LocalSimulator()
    circuits = FourierCircuits(phi=phi, native_only=native_only)

    probability = benchmark_using_controlled_unitary(
        device=device,
        target=0,
        ancilla=1,
        state_preparation=circuits.state_preparation,
        basis_change=circuits.unitary_to_discriminate,
        controlled_unitary=circuits.controlled_v0_v1_dag,
        num_shots_per_measurement=20,
    )

    assert 0 <= probability <= 1
