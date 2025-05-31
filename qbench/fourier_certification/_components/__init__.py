"""Module defining _components used in Fourier certification experiment."""

from typing import Union

import numpy as np

# from . import _generic, _ibmq, _lucy, _rigetti


def certification_probability_upper_bound(
    phi: Union[float, np.ndarray], delta: float
) -> Union[float, np.ndarray]:
    """Compute the minimized probability of type II error in certification scheme
      between measurements in P_U and P_1.

    :param phi: angle of measurement P_U to be certified from P_1.
    :param delta: a given statistical significance.

    :return: minimized probability of type II error.
    """

    if 1 / 2 * np.abs(1 + np.exp(-1j * phi)) > np.sqrt(delta):
        return (
            1 / 2 * np.abs(1 + np.exp(-1j * phi)) * np.sqrt(1 - delta)
            - np.sqrt(1 - 1 / 4 * np.abs(1 + np.exp(-1j * phi)) ** 2) * np.sqrt(delta)
        ) ** 2
    else:
        return 0
