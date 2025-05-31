"""Functionalities relating specifically to Fourier-certification experiments.


This package defines all instructions (_components) needed for assembling
circuits for benchmarking using Fourier-parametrized family.

The Fourier family of measurements is defined as:

$$
U(\\varphi) = H \\begin{pmatrix} 1&0\\\\0&e^{i\\varphi}\\end{pmatrix}H^\\dagger
$$

All _components are available as properties of :class:`FourierComponents` class. The
instances of this class can be constructed in such a way that the instructions they
provide are compatible with several different quantum devices available on the market.

Additionally, this module provides a function computing the minimized probability of
type II error.

"""

from ._cli import add_fourier_certification_parser
from ._components.components import FourierComponents
from ._models import (
    FourierCertificationAsyncResult,
    FourierCertificationSyncResult,
    FourierExperimentSet,
)

__all__ = [
    "add_fourier_certification_parser",
    "FourierComponents",
    "FourierCertificationAsyncResult",
    "FourierCertificationSyncResult",
    "FourierExperimentSet",
]
