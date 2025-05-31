"""Module defining _components used in Fourier discrimination experiment."""

from typing import Union

import numpy as np


def discrimination_probability_upper_bound(
    phi: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Compute exact upper bound on the probability of discrimination.

    :param phi: angle parametrizing the performed measurement.
    :return: maximum probability with which identity and $p_{U(\\varphi)}$ can be discriminated.
    """
    return 0.5 + 0.25 * np.abs(1 - np.exp(1j * phi))


__all__ = ["discrimination_probability_upper_bound"]
