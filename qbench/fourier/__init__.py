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

from ._cli import add_fourier_parser
from ._components import FourierComponents
from ._models import (
    FourierDiscriminationAsyncResult,
    FourierDiscriminationSyncResult,
    FourierExperimentSet,
)
from .experiment_runner import discrimination_probability_upper_bound

__all__ = [
    "discrimination_probability_upper_bound",
    "add_fourier_parser",
    "FourierComponents",
    "FourierDiscriminationAsyncResult",
    "FourierDiscriminationSyncResult",
    "FourierExperimentSet",
]
