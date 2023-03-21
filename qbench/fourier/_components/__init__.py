"""Module defining components used in Fourier discrimination experiment."""
from typing import Optional, Union

from qiskit.circuit import Instruction, Parameter

from . import _generic, _ibmq, _lucy, _rigetti


class FourierComponents:
    """Class defining components for Fourier-discrimination experiment.

    :param phi: angle defining measurement to discriminate. May be a number or an instance of
      a Qiskit Parameter. See
      :qiskit_tutorial:`here <circuits_advanced/01_advanced_circuits.html#Parameterized-circuits>`_
      if you are new to parametrized circuits in Qiskit.

    :param gateset: name of the one of the predefined basis gate sets to use. It controls which
      gates will be used to construct the circuit components. Available choices are:

      - :code:`"lucy"`: gateset comprising gates native to
        `OQC Lucy <https://aws.amazon.com/braket/quantum-computers/oqc/>`_ computer.
      - :code:`"rigetti"`: gateset comprising gates native to
        `Rigetti <https://www.rigetti.com/>`_ computers.
      - :code:`"ibmq"`: gateset comprising gates native to
        `IBMQ <https://quantum-computing.ibm.com/lab>`_ computers.

      If no gateset is provided, high-level gates will be used without restriction on basis gates.
    """

    def __init__(self, phi: Union[float, Parameter], gateset: Optional[str] = None):
        """Initialize new instance of FourierComponents."""
        self.phi = phi
        self._module = _GATESET_MAPPING[gateset]

    @property
    def state_preparation(self) -> Instruction:
        """Instruction performing transformation $|00\\rangle$ -> Bell state

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
        r"""Unitary $U^\dagger$ defining Fourier measurement.

        The corresponding circuit is:

        .. code::

                 ┌───┐┌───────────┐┌───┐
              q: ┤ H ├┤ Phase(-φ) ├┤ H ├
                 └───┘└───────────┘└───┘

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

                 ┌──────────┐┌────────────────┐
              q: ┤ Rz(-π/2) ├┤ Ry(-φ/2 - π/2) ├
                 └──────────┘└────────────────┘

        """
        return self._module.v0_dag(self.phi)

    @property
    def v1_dag(self) -> Instruction:
        """Instruction corresponding to the negative part of Holevo-Helstrom measurement.

        The corresponding circuit is:

        .. code::

                 ┌──────────┐┌────────────────┐┌────────┐
              q: ┤ Rz(-π/2) ├┤ Ry(-φ/2 - π/2) ├┤ Rx(-π) ├
                 └──────────┘└────────────────┘└────────┘
        """
        return self._module.v1_dag(self.phi)

    @property
    def v0_v1_direct_sum_dag(self) -> Instruction:
        r"""Direct sum $V_0^\dagger\oplus V_1^\dagger$ of both parts of Holevo-Helstrom measurement.

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
