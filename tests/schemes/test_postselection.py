import numpy as np
import pytest
from qiskit_braket_provider import BraketLocalBackend

from qbench.fourier import FourierComponents
from qbench.schemes.postselection import benchmark_discrimination_using_postselection


# TODO Have a look and decide, if it's worthy to test AmazonBraket's Lucy and Rigetti
@pytest.mark.parametrize("phi", np.linspace(0, 2 * np.pi, 20))
# @pytest.mark.parametrize("gateset", [None, "rigetti", "lucy", "ibmq"])
@pytest.mark.parametrize("gateset", [None, "ibmq"])
def test_computed_discrimination_probability_is_feasible(phi: float, gateset):
    backend = BraketLocalBackend()
    circuits = FourierComponents(phi=phi, gateset=gateset)

    probability = benchmark_discrimination_using_postselection(
        backend=backend,
        target=0,
        ancilla=1,
        state_preparation=circuits.state_preparation,
        u_dag=circuits.u_dag,
        v0_dag=circuits.v0_dag,
        v1_dag=circuits.v1_dag,
        num_shots_per_measurement=20,
    )

    assert 0 <= probability <= 1
