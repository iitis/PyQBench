"""Module defining components used in Fourier discrimination experiment."""
from typing import Optional, Union

from qiskit.circuit import Instruction, Parameter

from . import _generic, _ibmq, _lucy, _rigetti


class FourierComponents:
    """Class defining components for Fourier-discrimination experiment.

    :param phi: Fourier angle of measurement to discriminate. May be a qiskit Parameter.
    :param gateset: one of the predefined basis gate sets to use:
      ["lucy", "rigetti", "ibmq"]. If not provided, high-level definitions of gates
      will be used without restrictions on basis gates.
    """

    def __init__(self, phi: Union[float, Parameter], gateset: Optional[str] = None):
        """Initialize new instance of FourierComponents."""
        self.phi = phi
        self._module = _GATESET_MAPPING[gateset]

    @property
    def state_preparation(self) -> Instruction:
        """Instruction performing state preparation |00> -> bell state

        The corresponding circuit is:

        .. code::

                   ┌───┐
              q_0: ┤ H ├──■──
                   └───┘┌─┴─┐
              q_1: ─────┤ X ├
                        └───┘

        """
        return self._module.state_preparation()

    @property
    def u_dag(self) -> Instruction:
        r"""Unitary $U^\dagger$ defining alternative measurement.

        The corresponding circuit is:

        .. code::

                 ┌───┐┌─────────────┐┌───┐
              q: ┤ H ├┤ Phase(-phi) ├┤ H ├
                 └───┘└─────────────┘└───┘

        .. note::

           This instruction is needed because on actual devices we can only measure in Z-basis.
           The $U^\dagger$ unitary changes basis so that subsequent measurement in Z-basis can
           be considered as performing desired von Neumann measurement to be discriminated from
           the Z-basis one.
        """

        return self._module.u_dag(self.phi)

    @property
    def v0_dag(self) -> Instruction:
        """Instruction corresponding to the positive part of Holevo-Helstrom measurement.

        The corresponding circuit is:

        .. code::

                 ┌──────────┐┌──────────────────┐
              q: ┤ Rz(-π/2) ├┤ Ry(-phi/2 - π/2) ├
                 └──────────┘└──────────────────┘

        """
        return self._module.v0_dag(self.phi)

    @property
    def v1_dag(self) -> Instruction:
        """Instruction corresponding to the negative part of Holevo-Helstrom measurement.

        The corresponding circuit is:

        .. code::

                 ┌──────────┐┌──────────────────┐┌────────┐
              q: ┤ Rz(-π/2) ├┤ Ry(-phi/2 - π/2) ├┤ Rx(-π) ├
                 └──────────┘└──────────────────┘└────────┘
        """
        return self._module.v1_dag(self.phi)

    @property
    def v0_v1_direct_sum_dag(self) -> Instruction:
        r"""Direct sum $V_0^\dagger\oplusV_1^\dagger$ of both parts of Holevo-Helstrom measurement.

        .. note::
           In usual basis ordering, the unitaries returned by this property would be
           block-diagonal, with blocks corresponding to positive and negative parts
           of Holevo-Helstrom measurement.

           However, Qiskit enumerates basis vectors in reverse, so the produced unitaries
           are not block-diagonal, unless the qubits are swapped.
           See accompanying tests to see how it's done.

           The following article contains more details on basis vectors ordering used
           (among others) by Qiskit:
           https://arxiv.org/abs/1711.02086
        """
        return self._module.v0_v1_direct_sum(self.phi)


_GATESET_MAPPING = {
    "lucy": _lucy,
    "rigetti": _rigetti,
    "ibmq": _ibmq,
    None: _generic,
}
