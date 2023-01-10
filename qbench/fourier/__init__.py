"""Functionalities relating specifically to Fourier-discrimination experiments.


This package defines all instructions (components) needed for assembling
circuits for benchmarking using Fourier-parametrized family.

The Fourier family of measurements is defined as:

$$
U(\\varphi) = H \\begin{pmatrix} 1&0\\\\0&e^{i\\varphi}\\end{pmatrix}H^\\dagger
$$

All components are available as properties of :class:`FourierComponents` class. The
instances of this class can be constructed in such a way that the instructions they
provide are compatible with several different quantum devices available on the market.

Additionally, this module provides a function computing optimal discrimination probability
for Fourier family of measurements, which is defined as:

$$
p_{U(\\varphi)} = \\frac12 + \\frac14 \\lvert 1 - e^{i \\varphi}\\rvert.
$$

"""
from typing import Union

import numpy as np

from ._cli import add_fourier_parser
from ._components import FourierComponents
from ._models import (
    FourierDiscriminationAsyncResult,
    FourierDiscriminationSyncResult,
    FourierExperimentSet,
)


def discrimination_probability_upper_bound(
    phi: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """Compute exact upper bound on the probability of discrimination.

    :param phi: angle parametrizing the performed measurement.
    :return: maximum probability with which identity and $p_{U(\\varphi)}$ can be discriminated.
    """
    return 0.5 + 0.25 * np.abs(1 - np.exp(1j * phi))


__all__ = [
    "discrimination_probability_upper_bound",
    "add_fourier_parser",
    "FourierComponents",
    "FourierDiscriminationAsyncResult",
    "FourierDiscriminationSyncResult",
    "FourierExperimentSet",
]
