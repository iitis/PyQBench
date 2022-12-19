"""Functionalities relating specifically to Fourier-discrimination experiments.

This module contains the following:

- Components (in the form of Qiskit Instructions) needed for performing postselection
  or direct sum experiment using Fourier parametrized family.
- Utility function computing upper bound on probability of correct discrimination.
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
    :return: maximum probability with which identity and P_U(phi) can be discriminated.
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
