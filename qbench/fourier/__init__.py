from typing import Optional, Protocol, Union

import numpy as np
from braket import circuits

from . import _generic, _rigetti


class CircuitsImplementation(Protocol):
    def _state_preparation(self, target: int, ancilla: int) -> circuits.Circuit:
        pass

    def _black_box_dag(self, qubit: int, phi: float) -> circuits.Circuit:
        pass

    def _v0_dag(self, qubit: int, phi: float) -> circuits.Circuit:
        pass

    def _v1_dag(self, qubit: int, phi: float) -> circuits.Circuit:
        pass

    def _v0_v1_direct_sum(self, target: int, ancilla: int, phi: float) -> circuits.Circuit:
        pass


_GATESET_MAPPING: dict[Optional[str], CircuitsImplementation] = {
    "rigetti": _rigetti,
    None: _generic,
}


class FourierCircuits:
    """Class creating circuits for Fourier-measurement experiment.

    :param phi: Fourier angle of measurement to discriminate.
    :param native_only: whether to only use gates native to Rigetti architecture.
     Defaults to faults, in which case gates in the circuits will be compiled by
     Braket.
    """

    def __init__(self, phi: float, gateset: Optional[str] = None):
        self.phi = phi
        self._module = _GATESET_MAPPING[gateset]

    def state_preparation(self, target: int, ancilla: int) -> circuits.Circuit:
        """Create circuit initializing system into maximally entangled state.

        .. note::
           The returned circuit is (assuming target=0, ancilla=1) of the form:

           0: ───H───@───
                     │
           1: ───────X───

        :return: A circuit mapping |00> to (|00> + |11>) / sqrt(2).
        """
        return self._module._state_preparation(target, ancilla)

    def unitary_to_discriminate(self, qubit: int) -> circuits.Circuit:
        """Create a unitary channel corresponding to the measurement to discriminate.

        .. note::
           The returned circuits can be viewed as a change of basis in which von Neumann
           measurement is to be performed, and it looks as follows (assuming qubit=0).

           0: ───H───Phase(-ϕ)───H───

        :return: A circuit implementing appropriate unitary channel.
        """

        return self._module._black_box_dag(qubit, self.phi)

    def v0_dag(self, qubit: int) -> circuits.Circuit:
        """Create circuit corresponding to the positive part of Holevo-Helstrom measurement.

        :return: A circuit implementing positive part of Holevo-Helstrom measurement.
        """
        return self._module._v0_dag(qubit, self.phi)

    def v1_dag(self, qubit) -> circuits.Circuit:
        """Create circuit corresponding to the negative part of Holevo-Helstrom measurement.

        :return: A circuit implementing positive part of Holevo-Helstrom measurement.
        """
        return self._module._v1_dag(qubit, self.phi)

    def controlled_v0_v1_dag(self, target: int, ancilla: int) -> circuits.Circuit:
        """Create circuit implementing controlled Holevo-Helstrom measurement.

        .. note::
           In usual basis ordering, the unitaries produced by this function would be
           block-diagonal, with blocks corresponding to positive and negative parts
           of Holevo-Helstrom measurement.

           However, Braket enumerates basis vectors in reverse, so the produced unitaries
           are not block-diagonal, unless the qubits are swapped.
           See accompanying tests to see how it's done.

           The following article contains more details on basis vectors ordering used
           (among others) by Braket:
           https://arxiv.org/abs/1711.02086

        :return: Circuit implementing V0 \\oplus V1.
        """
        return self._module._v0_v1_direct_sum(target, ancilla, self.phi)


def discrimination_probability_upper_bound(
    phi: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Compute upper bound on the probability of discrimination.

    :param phi: angle parametrizing the performed measurement.
    :return: maximum probability with which identity and P_U(phi)
     can be discriminated
    """
    return 0.5 + 0.25 * np.abs(1 - np.exp(1j * phi))
