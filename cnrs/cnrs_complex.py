"""
cnrs_complex.py
===============
CnrsComplex — a unified complex number interface for the CNRS toolkit.

CnrsComplex wraps CnrsFloat and presents an interface that mirrors Python's
built-in complex type, making CNRS representation transparent to scientists.
The goal is *CNRS in the middle, decimals at the edges*: ordinary Python or
numpy complex numbers go in, ordinary Python or numpy numbers come back out,
and CNRS does its structural work in between.

Architecture
------------
A CnrsComplex holds a CnrsFloat internally (mantissa digits, exponent,
mantissa length L).  All arithmetic decodes to Python complex, operates
in Python, and re-encodes at the same L.  This keeps the interface clean
and the error budget predictable.

Error budget
------------
Each encode introduces at most 2 * |z0|^{-(L-1)} = 2 * 5^{-(L-1)/2} error.
At the default L=14 this is ~5e-6; at L=10, ~1e-4.  Each arithmetic
operation (which decodes and re-encodes) adds at most one further unit of
this error.  For a chain of N operations the accumulated error is at most
N * 2 * 5^{-(L-1)/2}.

Default L
---------
DEFAULT_L = 14 is the toolkit default.  It gives ~5e-6 absolute error for
values of magnitude ~1, and is adequate for complex oscillator and
multiscale biology calculations.  Increase L for higher precision.

Public API
----------
Construction:
    CnrsComplex(value, L=14)           from Python complex/float/int
    CnrsComplex.from_polar(r, theta, L) from polar form r*exp(i*theta)
    CnrsComplex.from_cnrs_float(f)     from existing CnrsFloat
    CnrsComplex.zero(L=14)             the zero element
    CnrsComplex.one(L=14)              the unit element
    CnrsComplex.array(values, L=14)    encode a list or numpy array

Properties (read-only):
    .value       Python complex (decoded)
    .real        float
    .imag        float
    .L           mantissa length
    .cnrs_float  the underlying CnrsFloat

Operations (all return CnrsComplex at same L):
    z + w,  z - w,  z * w,  z / w
    -z
    z + c,  z - c,  z * c,  z / c    where c is int/float/complex
    c + z,  c - z,  c * z,  c / z    (reflected operators)

Measurement (all return Python float or complex):
    abs(z)           modulus |z|
    z.phase()        argument arg(z) in (-pi, pi]
    z.conjugate()    complex conjugate as CnrsComplex
    z.modulus_sq()   |z|^2 as float
    z.real_part()    Re(z) as float   (same as z.real)
    z.imag_part()    Im(z) as float   (same as z.imag)

Encoding quality:
    z.encoding_error(true_value)   |decoded - true| as float
    z.relative_error(true_value)   above / |true|

Array utilities (module-level):
    encode_array(values, L=14)     -> list[CnrsComplex]
    decode_array(czs)              -> list[complex]  (or np.ndarray if numpy available)
    to_numpy(czs)                  -> np.ndarray of complex128

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 42, 2026-06-06
"""

from __future__ import annotations

import cmath
import math
from typing import List, Sequence, Union

from .cnrs_float import (
    CnrsFloat,
    encode as _encode,
    decode as _decode,
    encoding_error as _encoding_error,
    relative_error as _relative_error,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_L: int = 14
"""Default mantissa length.  Error bound ~5e-6 for |value| ~ 1."""

_Number = Union[int, float, complex, "CnrsComplex"]


# ---------------------------------------------------------------------------
# CnrsComplex
# ---------------------------------------------------------------------------

class CnrsComplex:
    """
    A CNRS floating-point complex number with a clean scientific interface.

    Wraps CnrsFloat.  Arithmetic is exact up to the CnrsFloat encoding error
    (at most 2 * 5^{-(L-1)/2} per operation at mantissa length L).

    Parameters
    ----------
    value : int, float, or complex
        The complex value to encode.
    L : int
        Mantissa length (default 14).  Larger L gives smaller error.
    """

    __slots__ = ("_f",)

    def __init__(self, value: Union[int, float, complex], L: int = DEFAULT_L):
        if isinstance(value, CnrsComplex):
            self._f: CnrsFloat = value._f
        elif isinstance(value, CnrsFloat):
            self._f = value
        else:
            self._f = _encode(complex(value), L)

    # ------------------------------------------------------------------
    # Alternative constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_polar(cls, r: float, theta: float, L: int = DEFAULT_L) -> "CnrsComplex":
        """
        Construct from polar form r * exp(i * theta).

        Parameters
        ----------
        r : float   Modulus (>= 0).
        theta : float   Argument in radians.
        L : int     Mantissa length.
        """
        return cls(r * cmath.exp(1j * theta), L)

    @classmethod
    def from_cnrs_float(cls, f: CnrsFloat) -> "CnrsComplex":
        """Wrap an existing CnrsFloat without re-encoding."""
        obj = object.__new__(cls)
        obj._f = f
        return obj

    @classmethod
    def zero(cls, L: int = DEFAULT_L) -> "CnrsComplex":
        """The zero element."""
        return cls(0j, L)

    @classmethod
    def one(cls, L: int = DEFAULT_L) -> "CnrsComplex":
        """The unit element."""
        return cls(1+0j, L)

    @classmethod
    def array(cls, values: Sequence, L: int = DEFAULT_L) -> List["CnrsComplex"]:
        """
        Encode a sequence of values as CnrsComplex objects.

        Parameters
        ----------
        values : sequence of int/float/complex (or numpy array)
        L : int   Mantissa length for all elements.

        Returns
        -------
        list of CnrsComplex
        """
        return [cls(complex(v), L) for v in values]

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def cnrs_float(self) -> CnrsFloat:
        """The underlying CnrsFloat representation."""
        return self._f

    @property
    def L(self) -> int:
        """Mantissa length."""
        return self._f.L

    @property
    def value(self) -> complex:
        """Decoded Python complex value."""
        return _decode(self._f)

    @property
    def real(self) -> float:
        """Real part of the decoded value."""
        return _decode(self._f).real

    @property
    def imag(self) -> float:
        """Imaginary part of the decoded value."""
        return _decode(self._f).imag

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------

    def phase(self) -> float:
        """Argument arg(z) in (-pi, pi]."""
        return cmath.phase(_decode(self._f))

    def modulus_sq(self) -> float:
        """|z|^2 as a Python float."""
        v = _decode(self._f)
        return v.real * v.real + v.imag * v.imag

    def real_part(self) -> float:
        """Re(z). Equivalent to .real."""
        return _decode(self._f).real

    def imag_part(self) -> float:
        """Im(z). Equivalent to .imag."""
        return _decode(self._f).imag

    def conjugate(self) -> "CnrsComplex":
        """Complex conjugate as a new CnrsComplex at the same L."""
        return CnrsComplex(_decode(self._f).conjugate(), self._f.L)

    def encoding_error(self, true_value: complex) -> float:
        """Absolute encoding error |decoded - true_value|."""
        return _encoding_error(complex(true_value), self._f)

    def relative_error(self, true_value: complex) -> float:
        """Relative encoding error |decoded - true_value| / |true_value|."""
        return _relative_error(complex(true_value), self._f)

    # ------------------------------------------------------------------
    # Arithmetic helpers
    # ------------------------------------------------------------------

    def _coerce(self, other: _Number) -> complex:
        """Convert other to Python complex for arithmetic."""
        if isinstance(other, CnrsComplex):
            return _decode(other._f)
        return complex(other)

    def _op(self, result: complex) -> "CnrsComplex":
        """Encode an arithmetic result at the same L."""
        return CnrsComplex(result, self._f.L)

    # ------------------------------------------------------------------
    # Arithmetic operators
    # ------------------------------------------------------------------

    def __add__(self, other: _Number) -> "CnrsComplex":
        return self._op(_decode(self._f) + self._coerce(other))

    def __radd__(self, other: _Number) -> "CnrsComplex":
        return self._op(self._coerce(other) + _decode(self._f))

    def __sub__(self, other: _Number) -> "CnrsComplex":
        return self._op(_decode(self._f) - self._coerce(other))

    def __rsub__(self, other: _Number) -> "CnrsComplex":
        return self._op(self._coerce(other) - _decode(self._f))

    def __mul__(self, other: _Number) -> "CnrsComplex":
        return self._op(_decode(self._f) * self._coerce(other))

    def __rmul__(self, other: _Number) -> "CnrsComplex":
        return self._op(self._coerce(other) * _decode(self._f))

    def __truediv__(self, other: _Number) -> "CnrsComplex":
        denom = self._coerce(other)
        if abs(denom) == 0:
            raise ZeroDivisionError("CnrsComplex division by zero")
        return self._op(_decode(self._f) / denom)

    def __rtruediv__(self, other: _Number) -> "CnrsComplex":
        v = _decode(self._f)
        if abs(v) == 0:
            raise ZeroDivisionError("CnrsComplex division by zero")
        return self._op(self._coerce(other) / v)

    def __neg__(self) -> "CnrsComplex":
        return self._op(-_decode(self._f))

    def __pos__(self) -> "CnrsComplex":
        return CnrsComplex.from_cnrs_float(self._f)

    def __abs__(self) -> float:
        """Modulus |z| as a Python float."""
        return abs(_decode(self._f))

    def __eq__(self, other: object) -> bool:
        """
        Equality within one ULP of the coarser operand.

        For exact equality comparisons use .value directly.
        """
        if isinstance(other, CnrsComplex):
            return _decode(self._f) == _decode(other._f)
        if isinstance(other, (int, float, complex)):
            return _decode(self._f) == complex(other)
        return NotImplemented

    def __complex__(self) -> complex:
        """Allow complex(z) to return the decoded value."""
        return _decode(self._f)

    def __float__(self) -> float:
        """Allow float(z) for purely real values.

        Raises ValueError if the imaginary part exceeds the encoding error
        bound 2 * 5^{-(L-1)/2}, indicating the value is genuinely complex.
        """
        from .cnrs_float import ABS_Z0
        v = _decode(self._f)
        bound = 2.0 * ABS_Z0 ** (-(self._f.L - 1))
        if abs(v.imag) > bound:
            raise ValueError(
                f"CnrsComplex with non-zero imaginary part {v.imag!r} "
                "cannot be converted to float"
            )
        return v.real

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        v = _decode(self._f)
        return (f"CnrsComplex({v.real:+.6g}{v.imag:+.6g}j, L={self._f.L})")

    def __str__(self) -> str:
        v = _decode(self._f)
        return f"({v.real:+.6g}{v.imag:+.6g}j)"


# ---------------------------------------------------------------------------
# Module-level array utilities
# ---------------------------------------------------------------------------

def encode_array(values: Sequence, L: int = DEFAULT_L) -> List[CnrsComplex]:
    """
    Encode a sequence of values as CnrsComplex objects.

    Parameters
    ----------
    values : sequence of int / float / complex (or numpy array)
    L : int   Mantissa length for all elements (default 14).

    Returns
    -------
    list of CnrsComplex
    """
    return [CnrsComplex(complex(v), L) for v in values]


def decode_array(czs: Sequence[CnrsComplex]) -> List[complex]:
    """
    Decode a sequence of CnrsComplex objects to Python complex values.

    Parameters
    ----------
    czs : sequence of CnrsComplex

    Returns
    -------
    list of complex
    """
    return [_decode(z.cnrs_float) for z in czs]


def to_numpy(czs: Sequence[CnrsComplex]):
    """
    Convert a sequence of CnrsComplex to a numpy array of complex128.

    Requires numpy.

    Parameters
    ----------
    czs : sequence of CnrsComplex

    Returns
    -------
    numpy.ndarray of complex128
    """
    try:
        import numpy as np
    except ImportError as exc:
        raise ImportError(
            "numpy is required for to_numpy(); install with: pip install numpy"
        ) from exc
    return np.array([_decode(z.cnrs_float) for z in czs], dtype=np.complex128)
