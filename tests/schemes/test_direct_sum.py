import numpy as np
import pytest
from qiskit_braket_provider import BraketLocalBackend

from qbench.fourier import FourierComponents
from qbench.schemes.direct_sum import benchmark_using_direct_sum


@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 20))
@pytest.mark.parametrize("gateset", [None, "rigetti", "lucy", "ibmq"])
def test_computed_discrimination_probability_is_feasible(phi: float, gateset):
    backend = BraketLocalBackend()
    circuits = FourierComponents(phi=phi, gateset=gateset)

    probability = benchmark_using_direct_sum(
        backend=backend,
        target=0,
        ancilla=1,
        state_preparation=circuits.state_preparation,
        u_dag=circuits.u_dag,
        v0_v1_direct_sum_dag=circuits.v0_v1_direct_sum_dag,
        num_shots_per_measurement=20,
    )

    assert 0 <= probability <= 1
