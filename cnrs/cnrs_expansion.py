"""
cnrs_expansion.py
-----------------
CNRS-A greedy expansion engine for complex values.

This module implements the digit-by-digit greedy algorithm for the CNRS-A
base z0 = -2+i.  It is reliable for:

  - Gaussian integers:   expansion terminates in finite digits.
  - Z[i][1/z0] fractions: expansion terminates (finite fractional digits).

It is NOT reliable as a general analytic continuation engine for arbitrary
complex targets.  For Gaussian rationals p/q, the exact z0-adic algorithm
in cnrs_rational.py (gaussian_rational_to_cnrs) should be used instead:
that module works with exact integer arithmetic and guarantees correct
period detection.

InfiniteExpansion applied to a non-Gaussian-integer floating-point target
uses floating-point residuals, which accumulate rounding error.  The digit
sequence does not generally converge to the target for values outside
Z[i] or Z[i][1/z0].

Correct use cases
-----------------
  1. Expanding Gaussian integers (verification / diagnostics).
  2. Diagnostic residual tracking for approximate complex values.
  3. Educational illustration of the greedy algorithm.

Not correct for
---------------
  Arbitrary complex values, Gaussian rationals (use cnrs_rational instead),
  analytic continuation (use cnrs_continuation).

Background
----------
The correct greedy residual algorithm is:

  residual_0 = z
  d_0        = remainder(residual_0)
  residual_1 = (residual_0 - d_0) / Z0
  d_1        = remainder(residual_1)
  ...

For Gaussian integers this terminates (residual reaches 0).
For other targets, digits are generated but the partial sums may not
converge to the target.

Classes
-------
  InfiniteExpansion  : generates the greedy digit sequence for a complex target
  ExpansionState     : lightweight immutable state for one step
  ExpansionError     : raised when a digit cannot be found

Relation to CnrsH and CnrsRational
------------------------------------
InfiniteExpansion operates at the CNRS-A (number) layer using floating-point.
CnrsRational operates at the CNRS-A layer using exact integer arithmetic.
CnrsH operates at the function (calculus) layer.
None of these depends on the others.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Tuple

from .cnrs_repr import Z0, DIGITS, cnrs_remainder, _is_gaussian


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ExpansionError(ValueError):
    """Raised when the CNRS-A expansion cannot continue."""
    pass


# ---------------------------------------------------------------------------
# ExpansionState: one step of the expansion
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExpansionState:
    """
    Immutable state of the CNRS-A greedy expansion at one step.

    Fields
    ------
    target : complex
        The original value being expanded.
    residual : complex
        The remaining value to be represented after digits so far.
        Satisfies:  target == prefix_value + residual * Z0^(len(digits))
    digits : tuple[int, ...]
        Digits emitted so far, LSB-first.
    """
    target: complex
    residual: complex
    digits: Tuple[int, ...]

    @property
    def prefix_value(self) -> complex:
        """Evaluate the current prefix as a Gaussian partial sum."""
        z = complex(0)
        for k, d in enumerate(self.digits):
            z += d * (Z0 ** k)
        return z

    @property
    def error(self) -> float:
        """Absolute error: |target - prefix_value|."""
        return abs(self.target - self.prefix_value)

    def is_exact(self, tol: float = 1e-12) -> bool:
        """True if the residual is zero (expansion has terminated)."""
        return abs(self.residual) < tol

    def __str__(self) -> str:
        s = "".join(str(d) for d in reversed(self.digits)) or "0"
        return f"ExpansionState(target={self.target}, prefix={s!r}, residual={self.residual:.4f})"


# ---------------------------------------------------------------------------
# InfiniteExpansion
# ---------------------------------------------------------------------------

class InfiniteExpansion:
    """
    CNRS-A greedy expansion of a complex value using floating-point residuals.

    Generates digits one at a time using the residual algorithm:

        residual_0 = target
        d_n = remainder(residual_n)
        residual_{n+1} = (residual_n - d_n) / Z0

    Reliable for:
        Gaussian integers — terminates in finite digits.
        Z[i][1/z0] fractions — terminates (finite fractional digits).

    NOT reliable for:
        General Gaussian rationals — use cnrs_rational.gaussian_rational_to_cnrs
        instead, which uses exact integer arithmetic.
        Arbitrary floating-point targets — floating-point residuals accumulate
        error; the digit sequence does not generally converge.

    Usage
    -----
        exp = InfiniteExpansion(3 + 2j)
        digits = exp.take(20)          # first 20 digits, LSB-first
        value  = exp.evaluate(digits)  # reconstruct partial sum

    Or iterate:
        for digit, state in exp.steps(max_steps=30):
            print(digit, state.error)
            if state.is_exact():
                break
    """

    def __init__(self, target: complex, tol: float = 1e-12):
        """
        Parameters
        ----------
        target : complex
            The value to expand.  Need not be a Gaussian integer.
        tol : float
            Tolerance for declaring the expansion terminated.
        """
        self.target = target
        self.tol = tol
        self._initial_state = ExpansionState(
            target=target,
            residual=target,
            digits=()
        )

    def _next_state(self, state: ExpansionState) -> Tuple[int, ExpansionState]:
        """
        Compute one expansion step from the current state.

        Returns
        -------
        (digit, new_state)
        """
        if state.is_exact(self.tol):
            # Expansion has terminated; emit zeros
            new_state = ExpansionState(
                target=state.target,
                residual=complex(0),
                digits=state.digits + (0,)
            )
            return 0, new_state

        # Find the CNRS digit for the current residual
        residual = state.residual
        d = self._find_digit(residual)

        new_residual = (residual - d) / Z0
        new_state = ExpansionState(
            target=state.target,
            residual=new_residual,
            digits=state.digits + (d,)
        )
        return d, new_state

    def _find_digit(self, residual: complex) -> int:
        """
        Find the digit d in {0..4} for the given residual.

        For exact Gaussian integers, cnrs_remainder works directly.
        For general complex values, we choose the digit that minimises
        |(residual - d) / Z0| (closest approach to a Gaussian integer).
        """
        # First try exact (works for Gaussian integers and rationals
        # whose current residual is a Gaussian integer)
        for d in DIGITS:
            q = (residual - d) / Z0
            if _is_gaussian(q):
                return d

        # Fallback: minimise distance from next residual to nearest Gaussian integer
        best_d = 0
        best_err = float('inf')
        for d in DIGITS:
            q = (residual - d) / Z0
            qr = complex(round(q.real), round(q.imag))
            err = abs(q - qr)
            if err < best_err:
                best_err = err
                best_d = d

        return best_d

    # ------------------------------------------------------------------
    # Generation API
    # ------------------------------------------------------------------

    def steps(self, max_steps: int = 100) -> Iterator[Tuple[int, ExpansionState]]:
        """
        Iterate over (digit, state) pairs.

        Yields up to max_steps steps. Terminates early if the residual
        reaches zero.
        """
        state = self._initial_state
        for _ in range(max_steps):
            digit, state = self._next_state(state)
            yield digit, state
            if state.is_exact(self.tol):
                break

    def take(self, n: int) -> List[int]:
        """
        Return the first n digits (LSB-first).
        """
        digits = []
        state = self._initial_state
        for _ in range(n):
            d, state = self._next_state(state)
            digits.append(d)
        return digits

    def take_until_exact(self, max_steps: int = 10000) -> List[int]:
        """
        Expand until the residual is zero (for Gaussian integers).

        Raises ExpansionError if max_steps is exceeded.
        Always returns at least one digit (zero for the zero value).
        """
        digits = []
        state = self._initial_state
        for _ in range(max_steps):
            if state.is_exact(self.tol):
                break
            d, state = self._next_state(state)
            digits.append(d)
        else:
            if not state.is_exact(self.tol):
                raise ExpansionError(
                    f"Expansion did not terminate in {max_steps} steps "
                    f"for target={self.target}"
                )
        # Zero value: expansion terminates immediately with no digits emitted
        if not digits:
            digits = [0]
        return digits

    # ------------------------------------------------------------------
    # Evaluation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate(digits: List[int]) -> complex:
        """
        Evaluate a digit list (LSB-first) as a CNRS-A partial sum.

            value = sum_k digits[k] * Z0^k
        """
        z = complex(0)
        for k, d in enumerate(digits):
            z += d * (Z0 ** k)
        return z

    @staticmethod
    def evaluate_str(s: str) -> complex:
        """Evaluate a CNRS-A digit string (MSB-first)."""
        from .cnrs_repr import cnrs_to_gaussian
        return cnrs_to_gaussian(s)

    def error_after(self, n: int) -> float:
        """
        Return |target - partial_sum| after n digits.
        """
        digits = self.take(n)
        return abs(self.target - self.evaluate(digits))

    # ------------------------------------------------------------------
    # Period detection (for Gaussian rationals)
    # ------------------------------------------------------------------

    def detect_period(self, max_steps: int = 200) -> Optional[Tuple[int, int]]:
        """
        Detect if the expansion is eventually periodic.

        Returns (preperiod, period_length) if a period is found,
        or None if no period is detected within max_steps.

        Uses Floyd's cycle detection on the residual values.
        """
        residuals = {}
        state = self._initial_state
        for step in range(max_steps):
            key = (round(state.residual.real, 8), round(state.residual.imag, 8))
            if key in residuals:
                preperiod = residuals[key]
                period = step - preperiod
                return preperiod, period
            residuals[key] = step
            _, state = self._next_state(state)
            if state.is_exact(self.tol):
                return step + 1, 0  # terminates: period 0

        return None  # no period detected

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        digits = self.take(12)
        s = "".join(str(d) for d in reversed(digits))
        return f"InfiniteExpansion({self.target}, prefix={s!r}...)"

    def __repr__(self) -> str:
        return str(self)


# ---------------------------------------------------------------------------
# Convenience: expand a Gaussian integer and verify it matches cnrs_repr
# ---------------------------------------------------------------------------

def expand_gaussian(g: complex) -> List[int]:
    """
    Expand a Gaussian integer using InfiniteExpansion and return digits LSB-first.

    This should agree exactly with gaussian_to_cnrs_digits from cnrs_repr.
    """
    exp = InfiniteExpansion(g)
    return exp.take_until_exact()
