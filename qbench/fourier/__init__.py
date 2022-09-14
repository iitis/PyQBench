"""Implementation of components and exact probabilities needed in Fourier experiment."""
from typing import Optional, Union

import numpy as np
from qiskit.circuit import Instruction

from . import _generic, _lucy, _rigetti

_GATESET_MAPPING = {
    "lucy": _lucy,
    "rigetti": _rigetti,
    None: _generic,
}


class FourierComponents:
    """Class defining components for Fourier-measurement experiment."""

    def __init__(self, phi: float, gateset: Optional[str] = None):
        """Initialize new instance of FourierCircuits.

        :param phi: Fourier angle of measurement to discriminate.
        :param gateset: one of predefined basis gate sets to use. One of ["lucy", "rigetti"].
         If not provided, high-level definitions of gates will be used without restrictions.
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
    def black_box_dag(self) -> Instruction:
        """Black box to be discriminated from Z-basis measurement.

        .. note::
           This instruction is needed because on actual devices we can only measure in Z-basis.
           The corresponding unitary changes basis so that subsequent measurement in Z-basis can
           be considered as performing desired von Neumann measurement to be discriminated from
           the Z-basis one. The corresponding circuit is:

              ┌───┐┌─────────────┐┌───┐
           q: ┤ H ├┤ Phase(-phi) ├┤ H ├
              └───┘└─────────────┘└───┘
        """

        return self._module.black_box_dag(self.phi)

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


def discrimination_probability_upper_bound(
    phi: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Compute upper bound on the probability of discrimination.

    :param phi: angle parametrizing the performed measurement.
    :return: maximum probability with which identity and P_U(phi)
     can be discriminated
    """
    return 0.5 + 0.25 * np.abs(1 - np.exp(1j * phi))


def add_fourier_parser(parent_parser):
    parser = parent_parser.add_parser("disc-fourier")

    subcommands = parser.add_subparsers()

    benchmark = subcommands.add_parser(
        "benchmark",
        description=(
            "Run benchmarking experiment utilizing measurement discrimination "
            "with parametrized Fourier family of measurements."
        ),
    )

    benchmark.add_argument(
        "experiment-file", help="path to the file describing the experiment", type=str
    )
    benchmark.add_argument(
        "backend-file", help="path to the file describing the backend to be used", type=str
    )

    benchmark.add_argument(
        "--output",
        help="optional path to the output file. If not provided, output will be printed to stdout",
        type=str,
    )

    plot = subcommands.add_parser("plot")

    plot.add_argument(
        "result",
        help=(
            "result of discrimination experiment which can be obtained by running "
            "qbench benchmark"
        ),
        type=str,
    )

    plot.add_argument(
        "--output",
        help=(
            "optional path to the output file. If not provided, the plots will be shown "
            "but not saved. The extension of the output file determines the output format "
            "and it can be any of the ones supported by the matplotlib"
        ),
        type=str,
    )
