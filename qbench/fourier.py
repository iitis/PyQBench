from typing import Callable

import numpy as np
from braket import circuits


def state_preparation_circuit(target: int = 0, ancilla: int = 1) -> circuits.Circuit:
    """Create circuit initializing system into maximally entangled state.

    :param target: Index of qubit on which von Neumann measurement will be performed.
    :param ancilla: Index of qubit on which conditional measurement will be performed.
    :return: A circuit mapping |00> to (|00> + |11>) / sqrt(2).
    """
    return circuits.Circuit().h(target).cnot(target, ancilla)


def basis_change(phi: float) -> Callable[[int], circuits.Circuit]:
    """Create function that produces basis change circuit for given qubits.

    :param phi: Rotation angle used in PHASE gate.
    :param target: Index of qubit on which von Neumann measurement will be performed.
    :return: A circuit H-PHASE(phi)-H
    """

    def _circuit_factory(target: int) -> circuits.Circuit:
        return circuits.Circuit().h(target).phaseshift(target, phi).h(target)

    return _circuit_factory


def v0_circuit(phi: float, target: int, native_only: bool = False):
    """Circuit implementing V0 operation on given qubit.

    :param phi: rotation angle.
    :param target: qubit V0 should be applied to
    :param native_only: use only gates native to current Rigetti QPUs. Use this if you
     don't trust the compiler.
    :return: Circuit performing V0 operation.
    """
    return (
        circuits.Circuit()
        .rx(target, np.pi / 2)
        .rz(target, (phi + np.pi) / 2)
        .rx(target, -np.pi / 2)
        .rz(target, -np.pi / 2)
        if native_only
        else circuits.Circuit().ry(target, (phi + np.pi) / 2).rz(target, -np.pi / 2)
    )


def v1_circuit(phi: float, target: int, native_only: bool = False):
    """Circuit implementing V0 operation on given qubit.

    :param phi: rotation angle.
    :param target: qubit V1 should be applied to.
    :param native_only: use only gates native to current Rigetti QPUs. Use this if you
     don't trust the compiler.
    :return: Circuit performing V1 operation.
    """
    return (
        circuits.Circuit()
        .rx(target, np.pi / 2)
        .rz(target, (np.pi - phi) / 2)
        .rx(target, -np.pi / 2)
        .rz(target, np.pi / 2)
        if native_only
        else circuits.Circuit()
        .rx(target, np.pi)
        .ry(target, (phi + np.pi) / 2)
        .rz(target, -np.pi / 2)
    )


def controlled_v0_v1(phi, native_only: bool = True):
    """Create a function producing controlled v0 oplus v1 unitary..

    .. note::
       Braket enumerates basis vectors in "reverse". Hence, unitary of this circuit
       returned by `circuit.as_unitary() is not block-diagonal`, unless the qubits
       are swapped. See accompanying tests to see how it's done.

       The following article contains more details on basis vectors ordering used
       (among others) by Braket:
       https://arxiv.org/abs/1711.02086

    :param phi: rotation angle for both V0 and V1 blocks.
    :param control: index of the control qubit.
    :param target: index of the target qubit.
    :param native_only: use only gates native to Rigetti architecture.
    :return: Circuit implementing V0 \\oplus V1.
    """

    def _circuit_factory(target, ancilla) -> circuits.Circuit:
        return circuits.Circuit().cnot(target, ancilla) + v0_circuit(
            phi, ancilla, native_only=native_only
        )

    return _circuit_factory
