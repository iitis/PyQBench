from typing import Union

import numpy as np
from braket import circuits


class FourierCircuits:
    def __init__(self, phi: float, native_only: bool = False):
        self.phi = phi
        self.native_only = native_only

    @staticmethod
    def state_preparation(target: int, ancilla: int) -> circuits.Circuit:
        """Create circuit initializing system into maximally entangled state.

        .. note::
           The returned circuit is (assuming target=0, ancilla=1) of the form:

           0: ───H───@───
                     │
           1: ───────X───

        :return: A circuit mapping |00> to (|00> + |11>) / sqrt(2).
        """
        return circuits.Circuit().h(target).cnot(target, ancilla)

    def unitary_to_discriminate(self, qubit: int) -> circuits.Circuit:
        """Create function that produces a unitary channel parametrized by angle phi.

        .. note::
           The returned circuits can be viewed as a change of basis in which von Neumann
           measurement is to be performed and it looks as follows (assuming target=0).

           0: ───H───Phase(-ϕ)───H───

        :param phi: Rotation angle used in PHASE gate.
        :return: A function mapping qubit index (target) to circuit implementing
         appropriate unitary channel.
        """

        return circuits.Circuit().h(qubit).phaseshift(qubit, -self.phi).h(qubit)

    def v0_dag(self, qubit: int) -> circuits.Circuit:
        """Return function producing positive part of Holevo-Helstrom measurement.

        :param phi: rotation angle.
        :param native_only: use only gates native to current Rigetti QPUs. Use this if you
         don't trust the compiler.
        :return: Function mapping qubit to a circuit implementing positive part of
         Holevo-Helstrom measurement.
        """
        return (
            circuits.Circuit()
            .rz(qubit, -np.pi / 2)
            .rx(qubit, np.pi / 2)
            .rz(qubit, -(self.phi + np.pi) / 2)
            .rx(qubit, -np.pi / 2)
            if self.native_only
            else (circuits.Circuit().rz(qubit, -np.pi / 2).ry(qubit, -(self.phi + np.pi) / 2))
        )

    def v1_dag(self, qubit) -> circuits.Circuit:
        """Return function producing positive part of Holevo-Helstrom measurement.

        :param phi: rotation angle.
        :param native_only: use only gates native to current Rigetti QPUs. Use this if you
         don't trust the compiler.
        :return: Function mapping qubit to a circuit implementing positive part of
         Holevo-Helstrom measurement.
        """

        return (
            circuits.Circuit()
            .rz(qubit, np.pi / 2)
            .rx(qubit, np.pi / 2)
            .rz(qubit, -(np.pi - self.phi) / 2)
            .rx(qubit, -np.pi / 2)
            if self.native_only
            else circuits.Circuit()
            .rz(qubit, -np.pi / 2)
            .ry(qubit, -(self.phi + np.pi) / 2)
            .rx(qubit, -np.pi)
        )

    def controlled_v0_v1_dag(self, target: int, ancilla: int) -> circuits.Circuit:
        """Create a function producing controlled Holevo-Helstrom measurement.

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

        :param phi: rotation angle for positive and negative part.
        :param native_only: use only gates native to Rigetti architecture.
        :return: Circuit implementing V0 \\oplus V1.
        """
        return (
            circuits.Circuit().phaseshift(target, np.pi)
            + self.v0_dag(ancilla)
            + circuits.Circuit().cnot(target, ancilla)
        )


def discrimination_probability_upper_bound(
    phi: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Compute upper bound on the probability of discrimination.

    :param phi: angle parametrizing the performed measurement.
    :return: maximum probability with which identity and P_U(phi)
     can be discriminated
    """
    return 0.5 + 0.25 * np.abs(1 - np.exp(1j * phi))
