import numpy as np
import pytest
from qiskit_braket_provider import BraketLocalBackend

from qbench.direct_sum import benchmark_using_controlled_unitary
from qbench.fourier import FourierComponents


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 20))
@pytest.mark.parametrize("gateset", [None, "rigetti", "lucy"])
def test_computed_discrimination_probability_is_feasible(phi: float, gateset):
    backend = BraketLocalBackend()
    circuits = FourierComponents(phi=phi, gateset=gateset)

    probability = benchmark_using_controlled_unitary(
        backend=backend,
        target=0,
        ancilla=1,
        state_preparation=circuits.state_preparation,
        black_box_dag=circuits.black_box_dag,
        v0_v1_direct_sum_dag=circuits.controlled_v0_v1_dag,
        num_shots_per_measurement=20,
    )

    assert 0 <= probability <= 1
