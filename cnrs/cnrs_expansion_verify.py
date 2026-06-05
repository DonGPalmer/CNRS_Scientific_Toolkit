"""
cnrs_expansion_verify.py
------------------------
Verification suite for InfiniteExpansion.

Tests:
  E1  Gaussian integer expansion agrees with cnrs_repr (exact termination)
  E2  Partial sums converge to the target (error decreases)
  E3  Period detection works for known Gaussian rationals
  E4  The residual algorithm is correct at every step
  E5  Expansion of zero
"""

from __future__ import annotations
import random
from typing import List

from .cnrs_expansion import InfiniteExpansion, expand_gaussian
from .cnrs_repr import gaussian_to_cnrs_digits, Z0


TOL = 1e-10


def _rand_gaussian(radius: int = 8) -> complex:
    return complex(random.randint(-radius, radius),
                   random.randint(-radius, radius))


# ---------------------------------------------------------------------------
# E1: Gaussian integers — agree with cnrs_repr
# ---------------------------------------------------------------------------

def test_e1_gaussian_integers(samples: int = 300, seed: int = 10) -> None:
    """
    InfiniteExpansion of a Gaussian integer terminates and matches
    the reference gaussian_to_cnrs_digits from cnrs_repr.
    """
    random.seed(seed)
    for i in range(samples):
        g = _rand_gaussian()
        ref = gaussian_to_cnrs_digits(g)
        got = expand_gaussian(g)

        # Trim trailing zeros from both for comparison
        def trim(ds):
            while len(ds) > 1 and ds[-1] == 0:
                ds = ds[:-1]
            return ds

        ref_t = trim(list(ref))
        got_t = trim(list(got))

        if ref_t != got_t:
            raise AssertionError(
                f"E1 failed (sample {i}), g={g}:\n"
                f"  cnrs_repr:         {ref_t}\n"
                f"  InfiniteExpansion: {got_t}"
            )


# ---------------------------------------------------------------------------
# E2: Convergence — error decreases with more digits
# ---------------------------------------------------------------------------

def test_e2_convergence(samples: int = 100, seed: int = 11) -> None:
    """
    The partial sum error |target - sum_k d_k Z0^k| decreases (or reaches zero)
    as more digits are taken, for arbitrary complex targets.
    """
    random.seed(seed)
    for i in range(samples):
        # Use Gaussian rationals (exact representation in finitely many steps
        # for simple cases, infinite for others)
        # Pick a/b where a is Gaussian, b is small integer
        a = _rand_gaussian(radius=5)
        b = random.randint(1, 4)
        target = a / b

        exp = InfiniteExpansion(target)
        errors = [exp.error_after(n) for n in [5, 10, 20, 40]]

        # Errors should not increase (allow small floating point jitter)
        for j in range(len(errors) - 1):
            if errors[j+1] > errors[j] + 1e-6:
                raise AssertionError(
                    f"E2 convergence failed (sample {i}): errors increased\n"
                    f"  target={target}, errors={errors}"
                )


# ---------------------------------------------------------------------------
# E3: Period detection for Gaussian rationals
# ---------------------------------------------------------------------------

def test_e3_period_detection(seed: int = 12) -> None:
    """
    Known Gaussian rationals have detectable periods (or terminate).
    """
    random.seed(seed)

    # 1/(3-i) = 0.3 + 0.1i: should have a period
    target1 = 1 / (3 - 1j)
    exp1 = InfiniteExpansion(target1)
    result1 = exp1.detect_period(max_steps=100)
    assert result1 is not None, \
        f"E3 failed: no period detected for 1/(3-i), got None"
    preperiod, period = result1
    assert period > 0 or preperiod > 0, \
        f"E3 failed: period={period}, preperiod={preperiod}"

    # Gaussian integer: should 'terminate' (period == 0)
    for _ in range(10):
        g = _rand_gaussian(radius=4)
        exp = InfiniteExpansion(g)
        result = exp.detect_period(max_steps=200)
        assert result is not None, f"E3 failed: Gaussian integer {g} didn't terminate"
        _, period = result
        assert period == 0, \
            f"E3 failed: Gaussian integer {g} has non-zero period {period}"


# ---------------------------------------------------------------------------
# E4: Residual correctness at every step
# ---------------------------------------------------------------------------

def test_e4_residual_correctness(samples: int = 200, seed: int = 13) -> None:
    """
    At every step, verify:  target == prefix_value + residual * Z0^n
    """
    random.seed(seed)
    for i in range(samples):
        target = complex(random.uniform(-4, 4), random.uniform(-4, 4))
        exp = InfiniteExpansion(target)

        prev_residual = target
        digits_so_far = []
        for step, (digit, state) in enumerate(exp.steps(max_steps=20)):
            digits_so_far.append(digit)
            n = len(digits_so_far)

            # Verify: target == prefix_value + residual * Z0^n
            prefix = InfiniteExpansion.evaluate(digits_so_far)
            reconstructed = prefix + state.residual * (Z0 ** n)

            if abs(reconstructed - target) > 1e-9:
                raise AssertionError(
                    f"E4 residual correctness failed (sample {i}, step {step}):\n"
                    f"  target={target}\n"
                    f"  prefix={prefix}, residual={state.residual}\n"
                    f"  reconstructed={reconstructed}"
                )


# ---------------------------------------------------------------------------
# E5: Expansion of zero
# ---------------------------------------------------------------------------

def test_e5_zero() -> None:
    """Expansion of 0 should give digit [0] immediately."""
    exp = InfiniteExpansion(0+0j)
    digits = exp.take_until_exact()
    assert digits == [0] or all(d == 0 for d in digits), \
        f"E5 failed: expansion of 0 gave {digits}"
    assert exp.error_after(1) == 0.0, "E5 failed: error after 1 digit is non-zero"


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_all_tests() -> None:
    """Run the complete InfiniteExpansion verification suite."""
    print("Running InfiniteExpansion verification suite...")

    test_e1_gaussian_integers()
    print("  ✓ E1  Gaussian integers      (agrees with cnrs_repr, exact termination)")

    test_e2_convergence()
    print("  ✓ E2  Convergence            (error non-increasing with more digits)")

    test_e3_period_detection()
    print("  ✓ E3  Period detection       (terminates for integers, periodic for rationals)")

    test_e4_residual_correctness()
    print("  ✓ E4  Residual correctness   (target == prefix + residual * Z0^n at every step)")

    test_e5_zero()
    print("  ✓ E5  Zero                   (expands to [0])")

    print("All InfiniteExpansion tests passed.")
