from typing import Optional, Union

from qiskit.circuit import Instruction, Parameter

from qbench.fourier import _generic, _ibmq, _lucy, _rigetti


class FourierComponents:
    """Class defining components for Fourier-measurement experiment."""

    def __init__(self, phi: Union[float, Parameter], gateset: Optional[str] = None):
        """Initialize new instance of FourierCircuits.

        :param phi: Fourier angle of measurement to discriminate.
        :param gateset: one of predefined basis gate sets to use. One of
        ["lucy", "rigetti", "ibmq"]. If not provided, high-level definitions of gates
        will be used without restrictions.
        """
        self.phi = phi
        self._module = _GATESET_MAPPING[gateset]

    @property
    def state_preparation(self) -> Instruction:
        """Instruction performing state preparation |00> -> bell state

        .. note::
           The corresponding circuit is:

                ┌───┐
           q_0: ┤ H ├──■──
                └───┘┌─┴─┐
           q_1: ─────┤ X ├
                     └───┘
        """
        return self._module.state_preparation()

    @property
    def u_dag(self) -> Instruction:
        """Matrix changing basis to the one in which alternative measurement is to be performed.

        .. note::
           This instruction is needed because on actual devices we can only measure in Z-basis.
           The corresponding unitary changes basis so that subsequent measurement in Z-basis can
           be considered as performing desired von Neumann measurement to be discriminated from
           the Z-basis one. The corresponding circuit is:

              ┌───┐┌─────────────┐┌───┐
           q: ┤ H ├┤ Phase(-phi) ├┤ H ├
              └───┘└─────────────┘└───┘
        """

        return self._module.u_dag(self.phi)

    @property
    def v0_dag(self) -> Instruction:
        """Instruction corresponding to the positive part of Holevo-Helstrom measurement.

        .. note::
           The corresponding circuit is:

              ┌──────────┐┌──────────────────┐
           q: ┤ Rz(-π/2) ├┤ Ry(-phi/2 - π/2) ├
              └──────────┘└──────────────────┘
        """
        return self._module.v0_dag(self.phi)

    @property
    def v1_dag(self) -> Instruction:
        """Instruction corresponding to the negative part of Holevo-Helstrom measurement.

        .. note::
           The corresponding circuit is:

              ┌──────────┐┌──────────────────┐┌────────┐
           q: ┤ Rz(-π/2) ├┤ Ry(-phi/2 - π/2) ├┤ Rx(-π) ├
              └──────────┘└──────────────────┘└────────┘
        """
        return self._module.v1_dag(self.phi)

    @property
    def controlled_v0_v1_dag(self) -> Instruction:
        """Direct sum of positive and negative part of Holevo-Helstrom measurement (V0 \\oplus V1).

        .. note::
           In usual basis ordering, the unitaries produced by this function would be
           block-diagonal, with blocks corresponding to positive and negative parts
           of Holevo-Helstrom measurement.

           However, Qiskit enumerates basis vectors in reverse, so the produced unitaries
           are not block-diagonal, unless the qubits are swapped.
           See accompanying tests to see how it's done.

           The following article contains more details on basis vectors ordering used
           (among others) by Qiskit and Braket:
           https://arxiv.org/abs/1711.02086
        """
        return self._module.v0_v1_direct_sum(self.phi)


_GATESET_MAPPING = {
    "lucy": _lucy,
    "rigetti": _rigetti,
    "ibmq": _ibmq,
    None: _generic,
}
