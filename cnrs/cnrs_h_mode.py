"""
cnrs_h_mode.py
==============
Dual-path CNRS-H adapter: native (CnrsHNative) or fast (CnrsH).

The two arithmetic backends have the same structural interface but very
different performance characteristics:

  CnrsH          — coefficients stored as Python complex; evaluation and
                   coefficient arithmetic use plain Python numerics.
                   Fast for evaluation-heavy workflows (~5–100 µs/op).

  CnrsHNative    — coefficients stored as CVal (CNRS-A digit strings);
                   all coefficient arithmetic routes through CNRS-A
                   transducers (add_cnrs / mul_cnrs).  Correct CNRS-run
                   arithmetic, but ~480× slower for multiplication and
                   ~11× slower for addition at order 20.

Automatic selection
-------------------
``CnrsHMode.from_coeffs(coeffs)`` inspects the coefficients and selects:

  - native=True  if every coefficient is a Gaussian integer (a + bi with
                 a, b ∈ Z).  These can be represented exactly in CNRS-A.
  - native=False if any coefficient is non-Gaussian (floats, irrational
                 eigenvalues, etc.).  Falls back to CnrsH.

Override
--------
Pass ``native=True`` or ``native=False`` explicitly to force a path:

  CnrsHMode.from_coeffs(coeffs, native=True)   # force native; raises if not Gaussian
  CnrsHMode.from_coeffs(coeffs, native=False)  # always use fast path

Interface
---------
The adapter presents the same narrow interface used by ScaleLaw and
OdeSolution:

  .coeffs          tuple of complex  (always Python complex, regardless of backend)
  .evaluate(s)     complex
  .differentiate() → CnrsHMode
  .integrate(c)    → CnrsHMode
  .native          bool — True if running on CnrsHNative

``native_mode()`` module-level helper returns True when the CnrsHNative
path would accept the given coefficient list (Gaussian-integer check).
"""

from __future__ import annotations

from typing import Optional, Sequence, Union

from .cnrs_h import CnrsH
from .cnrs_h_native import CnrsHNative, NonGaussianCoefficientError

_Scalar = Union[int, float, complex]
_GAUSSIAN_TOL = 1e-9


def _is_gaussian_int(z: complex, tol: float = _GAUSSIAN_TOL) -> bool:
    return (abs(z.real - round(z.real)) < tol and
            abs(z.imag - round(z.imag)) < tol)


def native_eligible(coeffs: Sequence[_Scalar]) -> bool:
    """Return True if every coefficient is a Gaussian integer."""
    return all(_is_gaussian_int(complex(c)) for c in coeffs)


class CnrsHMode:
    """
    Dual-path CNRS-H adapter.

    Wraps either a ``CnrsH`` (fast) or ``CnrsHNative`` (CNRS-A native)
    object and exposes a uniform interface for use by ScaleLaw and
    OdeSolution.  Callers can inspect ``.native`` to see which path is
    active.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, backend: Union[CnrsH, CnrsHNative]) -> None:
        self._backend = backend

    @classmethod
    def from_coeffs(
        cls,
        coeffs: Sequence[_Scalar],
        native: Optional[bool] = None,
    ) -> "CnrsHMode":
        """
        Build a CnrsHMode from an EGF coefficient list.

        Parameters
        ----------
        coeffs:
            EGF coefficients [d0, d1, ..., dN].
        native:
            None  → auto-select: native if all coefficients are Gaussian
                    integers, fast path otherwise.
            True  → force native; raises NonGaussianCoefficientError if
                    any coefficient is not a Gaussian integer.
            False → always use the fast (CnrsH) path.
        """
        if native is False:
            return cls(CnrsH.from_list(list(coeffs)))

        if native is True:
            # Attempt native; raises NonGaussianCoefficientError on failure
            return cls(CnrsHNative.from_gaussian_list(list(coeffs)))

        # Auto: use native only when every coefficient is Gaussian
        if native_eligible(coeffs):
            try:
                return cls(CnrsHNative.from_gaussian_list(list(coeffs)))
            except (NonGaussianCoefficientError, ValueError):
                # Coefficients are nominally Gaussian integers but too large
                # for exact CNRS-A expansion (floating-point precision limit).
                pass

        return cls(CnrsH.from_list(list(coeffs)))

    @classmethod
    def from_cnrs_h(cls, h: CnrsH) -> "CnrsHMode":
        """Wrap an existing CnrsH stream (always fast path)."""
        return cls(h)

    @classmethod
    def from_cnrs_h_native(cls, h: CnrsHNative) -> "CnrsHMode":
        """Wrap an existing CnrsHNative stream (always native path)."""
        return cls(h)

    # ------------------------------------------------------------------
    # Path inspection
    # ------------------------------------------------------------------

    @property
    def native(self) -> bool:
        """True if the native (CnrsHNative) path is active."""
        return isinstance(self._backend, CnrsHNative)

    @property
    def backend(self) -> Union[CnrsH, CnrsHNative]:
        """The underlying backend object."""
        return self._backend

    # ------------------------------------------------------------------
    # Uniform interface
    # ------------------------------------------------------------------

    @property
    def coeffs(self) -> tuple:
        """
        EGF coefficients as Python complex values.

        Always returns plain complex regardless of backend, so callers
        that inspect coefficients numerically (s_max estimation,
        eigenvalue extraction) work identically on both paths.
        """
        if isinstance(self._backend, CnrsHNative):
            return tuple(c.to_gaussian() for c in self._backend.coeffs)
        return self._backend.coeffs

    def evaluate(self, s: complex) -> complex:
        """Evaluate the EGF series at s."""
        return self._backend.evaluate(complex(s))

    def differentiate(self) -> "CnrsHMode":
        """Return the derivative as a CnrsHMode on the same backend."""
        return CnrsHMode(self._backend.differentiate())

    def integrate(self, constant: _Scalar = 0) -> "CnrsHMode":
        """Return the antiderivative as a CnrsHMode on the same backend.

        Native mode stores coefficients as ``CVal`` objects and therefore
        requires the integration constant to be a Gaussian integer.  Accept
        complex Gaussian-integer constants such as ``3+0j`` and ``1+2j`` by
        rounding them to the corresponding Gaussian integer complex value.
        Do not call ``int()`` on the constant: Python rejects complex inputs
        even when the imaginary part is zero.
        """
        if isinstance(self._backend, CnrsHNative):
            z = complex(constant)
            if not _is_gaussian_int(z):
                raise NonGaussianCoefficientError(
                    f"Integration constant {constant!r} is not a Gaussian "
                    "integer and cannot be stored in CnrsHNative."
                )
            gaussian_constant = complex(round(z.real), round(z.imag))
            return CnrsHMode(self._backend.integrate(gaussian_constant))
        return CnrsHMode(self._backend.integrate(constant))

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        path = "native" if self.native else "fast"
        n = len(self.coeffs)
        return f"CnrsHMode({path}, order={n})"
