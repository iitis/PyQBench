import pytest
from qiskit_braket_provider import AWSBraketProvider

from qbench.fourier import FourierCircuits
from qbench.utils import assert_can_be_run_in_verbatim_mode


@pytest.fixture(scope="module")
def aspen():
    return AWSBraketProvider().get_backend("Aspen-M-2")


@pytest.fixture()
def circuits():
    # We only use one value of phi that is not a characteristic multiple of pi/2
    # It should be enough to verify that circuits can be run, while not incurring
    # too big costs when tests are run.
    return FourierCircuits(phi=0.1, gateset="rigetti")


@pytest.mark.skipif("not config.getoption('rigetti')")
class TestRigettiDeviceCanRunDecomposedCircuitsInVerbatimMode:
    def test_black_box_can_be_run(self, aspen, circuits):
        assert_can_be_run_in_verbatim_mode(aspen, circuits.black_box_dag)

    def test_v0_dag_can_be_run(self, aspen, circuits):
        assert_can_be_run_in_verbatim_mode(aspen, circuits.v0_dag)

    def test_v1_dag_can_be_run(self, aspen, circuits):
        assert_can_be_run_in_verbatim_mode(aspen, circuits.v1_dag)

    def test_v0_v1_direct_sum_dag_can_be_run(self, aspen, circuits):
        assert_can_be_run_in_verbatim_mode(aspen, circuits.controlled_v0_v1_dag)
