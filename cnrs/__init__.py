"""
cnrs — Complex Numeric Representational System
===============================================

A Python implementation of the CNRS arithmetic and calculus framework.

Base:   z0 = -2 + i  (a Gaussian integer, N(z0) = 5)
Digits: D = {0, 1, 2, 3, 4}

The package is organised in three layers:

  Layer 1 — CNRS-A: arithmetic layer
    Finite digit-string representation of Gaussian integers.
    Addition via a 14-state finite-state transducer.
    Multiplication via Cauchy convolution + carry normalisation.
    Division, subtraction, and high-level operator wrappers.

  Layer 2 — CNRS-H: calculus layer
    EGF (exponential generating function) digit-string representation.
    Differentiation and integration are exact digit-shift operations.
    Operator calculus: shift operators, discrete derivative/integral.

  Layer 3 — Analytic continuation (partial)
    Full Gaussian rational representation in three cases:
      - Finite Z[i][1/z0] values (terminating expansion).
      - Pure z0-adic periodic rationals (denominator coprime to 5).
      - Laurent-periodic z0-adic rationals (denominator divisible by 5).
    Evaluate via CnrsRational.z0_adic_value() (fast float),
    CnrsRational.z0_adic_value_fractions() (fully exact),
    or CnrsRational.z0_adic_value_exact() (exact internally).
    CNRS floating-point arithmetic (CNRS-float, experimental).
    Branch-index (Layer-2) and global analytic (Layer-3/4) objects.

  Scientific toolkit (v0.5.1)
    CnrsComplex: unified complex interface matching Python's built-in complex.

    OdeSolution / cnrs_solve_*: CNRS-H coefficient-recurrence ODE solvers.
    Exact (up to floating-point) linear ODE solutions via digit shift.

    ScaleLaw: CNRS-H backed scale-law toolkit.
    Construction, fitting, differentiation, allometric analysis, and
    Turing-threshold detection via CNRS-H EGF calculus.

    Biological scale dynamics (cnrs_bio):
    Gierer-Meinhardt activator-inhibitor model in the CNRS-H multi-scale
    framework. Scale-dependent Turing conditions, s_exit detection, and
    scale-gradient corrections. Parameters from Paper 18.

    Complex oscillators (cnrs_oscillator):
    Stuart-Landau, RLC, driven harmonic, and interference models via
    CNRS-H coefficient recurrence. Three-workflow comparisons showing
    what early real reduction loses vs. full complex-state preservation.

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
"""

__version__ = "0.5.1"


# ── Layer 1: CNRS-A arithmetic ────────────────────────────────────────────────

from .cnrs_repr import (
    Z0, DIGITS,
    gaussian_to_cnrs_digits,
    gaussian_to_cnrs_str,
    cnrs_to_gaussian,
    normalize_cnrs,
)

from .cnrs_add import add_cnrs
from .cnrs_mul import mul_cnrs
from .cnrs_div import div_by_base_power, div_by_base, div_cnrs
from .cnrs_ops import cnrs_add, cnrs_sub, cnrs_mul, cnrs_neg, cnrs_eq
from .cnrs_value import CVal

# ── Layer 2: CNRS-H calculus ──────────────────────────────────────────────────

from .cnrs_h import CnrsH
from .cnrs_hstream import HStream
from .cnrs_operator import Operator

# ── Analytic continuation ─────────────────────────────────────────────────────

from .cnrs_expansion import InfiniteExpansion
from .cnrs_rational import CnrsRational, gaussian_rational_to_cnrs
from .cnrs_float import CnrsFloat

# ── Layer-2 / Layer-3 / Layer-4 objects ──────────────────────────────────────

from .cnrs_layer2 import Layer2
from .cnrs_layer2_value import L2Val
from .cnrs_layer3 import L3Value
from .cnrs_layer4 import L4Value, L4State

# ── Scientific toolkit — complex interface ────────────────────────────────────

from .cnrs_complex import CnrsComplex, encode_array, decode_array, to_numpy


# ── Scientific toolkit — chain-rule automatic differentiation ────────────────
from .autodiff import (
    CnrsDual,
    as_dual,
    exp as autodiff_exp,
    log as autodiff_log,
    sin as autodiff_sin,
    cos as autodiff_cos,
    tan as autodiff_tan,
    sqrt as autodiff_sqrt,
    pow_const,
    derivative,
    value_and_derivative,
    compose,
)


# ── Scientific toolkit — minimal symbolic calculus ───────────────────────────
from .symbolic import (
    BranchState, DEFAULT_BRANCH_STATE,
    Expr, Const, Var, Log, Sqrt, Pow,
    exp as symbolic_exp,
    log as symbolic_log,
    sin as symbolic_sin,
    cos as symbolic_cos,
    tan as symbolic_tan,
    sqrt as symbolic_sqrt,
    pow_branch,
    Integral,
    integrate as symbolic_integrate,
    diff as symbolic_diff,
)


# ── Scientific toolkit — symbolic/CNRS-H bridge ─────────────────────────────
from .cnrs_h_bridge import (
    UnsupportedBridgeExpression,
    BridgeComparison,
    cnrs_h_from_symbolic,
    symbolic_derivative_to_cnrs_h,
    cnrs_h_derivative_of_symbolic,
    symbolic_integral_to_cnrs_h,
    cnrs_h_integral_of_symbolic,
    compare_symbolic_and_cnrs_h_derivative,
    compare_symbolic_and_cnrs_h_integral,
    max_coeff_error,
    evaluate_cnrsh_series,
)


# ── Scientific toolkit — direct CNRS-H chain rule ───────────────────────────
from .cnrs_h_chain import (
    ChainRuleComparison,
    CnrsHChainError,
    compose_series,
    chain_rule_lhs,
    chain_rule_rhs,
    verify_chain_rule,
    power_series,
    exp_series as cnrsh_exp_series,
    sin_series as cnrsh_sin_series,
    cos_series as cnrsh_cos_series,
    monomial as cnrsh_monomial,
    identity as cnrsh_identity,
    constant as cnrsh_constant,
)

# ── Scientific toolkit — ODE solvers ─────────────────────────────────────────

from .cnrs_ode import (
    cnrs_solve_linear,
    cnrs_solve_driven,
    cnrs_solve_second_order,
    OdeSolution,
)

# ── Scientific toolkit — scale laws ──────────────────────────────────────────

from .cnrs_scale import (
    ScaleLaw,
    FitResult,
    AllometricResult,
    TuringResult,
    fit_exponential,
    fit_egf,
    fit_allometric,
    turing_threshold,
)

# ── Scientific toolkit — biological scale dynamics ────────────────────────────

from .cnrs_bio import (
    GmParams,
    da_profile,
    dh_profile,
    d_ratio,
    gm_steady_state,
    gm_jacobian,
    gm_steady_state_check,
    turing_discriminant,
    turing_active,
    find_s_exit,
    d_eff,
    gm_k0_rhs,
    turing_profile,
    TuringProfile,
    compare_turing_workflows,
    TuringWorkflowResult,
)

# ── Scientific toolkit — complex oscillators ──────────────────────────────────

from .cnrs_oscillator import (
    StuartLandauParams,
    RlcParams,
    DrivenParams,
    OscillatorSolution,
    stuart_landau_linear,
    rlc_free,
    rlc_driven,
    driven_harmonic,
    interference_pair,
    ThreeWorkflowResult,
    compare_stuart_landau,
    compare_rlc,
    compare_interference,
)

# ── Scientific toolkit — NumPy/SciPy interoperability ─────────────────────────

from .cnrs_interop import (
    cnrsh_to_numpy,
    numpy_to_cnrsh,
    ode_solution_to_numpy,
    cnrs_complex_to_numpy,
    modulus_array,
    modulus_sq_array,
    real_array,
    imag_array,
    phase_array,
    phase_rate_array,
    cnrs_to_scipy_ivp,
    scipy_ivp_to_cnrsh,
    solve_and_compare,
    ComparisonResult,
    benchmark_linear,
    benchmark_second_order,
    BenchmarkResult,
    to_dataframe,
)

# ── Scientific toolkit — Component 7: multi-scale SS physics ─────────────────
from .cnrs_multiscale import (
    ScaleLadder,
    LadderEvalResult,
    ScaleGradientResult,
    scale_gradient_correction,
    ladder_profile,
    ladder_to_scalelaws,
    JunctionCondition,
    FieldEquationCheck,
    PsiZeroDeterminer,
)

# ── Scientific toolkit — Component 8: scale-sweep and regime detection ────────
from .cnrs_regime import (
    ScaleParameter,
    ScaleSweep,
    ScaleSweepResult,
    RegimeTransition,
    detect_transitions,
    logarithmic_scale,
    length_from_scale,
)

# ── Scientific toolkit — reaction-diffusion scale-exit ────────────────────────
from .cnrs_rd_scale_exit import (
    RDLinearKinetics,
    ExponentialDiffusionLaw,
    TuringPoint,
    ScaleTransition,
    ScaleExitResult,
    TuringThresholds,
    turing_thresholds,
    turing_diagnostic,
    scan_scale_exit,
    exponential_gm_scale_exit,
    gm_default_kinetics,
    ladder_diffusion_law,
    scalelaw_diffusion_law,
    scan_scale_exit_ladder,
)

__all__ = [
    # ── Version
    "__version__",
    # ── Constants
    "Z0", "DIGITS",
    # ── Representation
    "gaussian_to_cnrs_digits", "gaussian_to_cnrs_str",
    "cnrs_to_gaussian", "normalize_cnrs",
    # ── Arithmetic
    "add_cnrs", "mul_cnrs", "div_by_base_power", "div_by_base", "div_cnrs",
    "cnrs_add", "cnrs_sub", "cnrs_mul", "cnrs_neg", "cnrs_eq",
    "CVal",
    # ── Calculus
    "CnrsH", "HStream", "Operator",
    # ── Analytic continuation
    "InfiniteExpansion", "CnrsRational", "gaussian_rational_to_cnrs", "CnrsFloat",
    # ── Layered objects
    "Layer2", "L2Val", "L3Value", "L4Value", "L4State",
    # ── Scientific toolkit — complex interface
    "CnrsComplex", "encode_array", "decode_array", "to_numpy",
    # ── Scientific toolkit — chain-rule autodiff
    "CnrsDual", "as_dual",
    "autodiff_exp", "autodiff_log", "autodiff_sin", "autodiff_cos",
    "autodiff_tan", "autodiff_sqrt", "pow_const",
    "derivative", "value_and_derivative", "compose",
    

    # ── Scientific toolkit — symbolic/CNRS-H bridge
    "UnsupportedBridgeExpression", "BridgeComparison",
    "cnrs_h_from_symbolic",
    "symbolic_derivative_to_cnrs_h", "cnrs_h_derivative_of_symbolic",
    "symbolic_integral_to_cnrs_h", "cnrs_h_integral_of_symbolic",
    "compare_symbolic_and_cnrs_h_derivative",
    "compare_symbolic_and_cnrs_h_integral",
    "max_coeff_error", "evaluate_cnrsh_series",

    
    # ── Scientific toolkit — direct CNRS-H chain rule
    "ChainRuleComparison", "CnrsHChainError",
    "compose_series", "chain_rule_lhs", "chain_rule_rhs", "verify_chain_rule",
    "power_series", "cnrsh_exp_series", "cnrsh_sin_series", "cnrsh_cos_series",
    "cnrsh_monomial", "cnrsh_identity", "cnrsh_constant",


# ── Scientific toolkit — ODE solvers
    "cnrs_solve_linear", "cnrs_solve_driven", "cnrs_solve_second_order",
    "OdeSolution",
    # ── Scientific toolkit — scale laws
    "ScaleLaw", "FitResult", "AllometricResult", "TuringResult",
    "fit_exponential", "fit_egf", "fit_allometric", "turing_threshold",
    # ── Scientific toolkit — biological scale dynamics
    "GmParams",
    "da_profile", "dh_profile", "d_ratio",
    "gm_steady_state", "gm_jacobian", "gm_steady_state_check",
    "turing_discriminant", "turing_active",
    "find_s_exit", "d_eff", "gm_k0_rhs",
    "turing_profile", "TuringProfile",
    "compare_turing_workflows", "TuringWorkflowResult",
    # ── Scientific toolkit — complex oscillators
    "StuartLandauParams", "RlcParams", "DrivenParams",
    "OscillatorSolution",
    "stuart_landau_linear", "rlc_free", "rlc_driven",
    "driven_harmonic", "interference_pair",
    "ThreeWorkflowResult",
    "compare_stuart_landau", "compare_rlc", "compare_interference",
    # ── Scientific toolkit — interoperability
    "cnrsh_to_numpy", "numpy_to_cnrsh", "ode_solution_to_numpy",
    "cnrs_complex_to_numpy",
    "modulus_array", "modulus_sq_array", "real_array", "imag_array",
    "phase_array", "phase_rate_array",
    "cnrs_to_scipy_ivp", "scipy_ivp_to_cnrsh",
    "solve_and_compare", "ComparisonResult",
    "benchmark_linear", "benchmark_second_order", "BenchmarkResult",
    "to_dataframe",
    # ── Scientific toolkit — Component 7: multi-scale SS physics
    "ScaleLadder", "LadderEvalResult", "ScaleGradientResult",
    "scale_gradient_correction", "ladder_profile", "ladder_to_scalelaws",
    "JunctionCondition", "FieldEquationCheck", "PsiZeroDeterminer",
    # ── Scientific toolkit — Component 8: scale-sweep and regime detection
    "ScaleParameter", "ScaleSweep", "ScaleSweepResult", "RegimeTransition",
    "detect_transitions", "logarithmic_scale", "length_from_scale",
    # ── Scientific toolkit — reaction-diffusion scale-exit
    "RDLinearKinetics", "ExponentialDiffusionLaw",
    "TuringPoint", "ScaleTransition", "ScaleExitResult", "TuringThresholds",
    "turing_thresholds", "turing_diagnostic", "scan_scale_exit",
    "exponential_gm_scale_exit", "gm_default_kinetics",
    "ladder_diffusion_law", "scalelaw_diffusion_law", "scan_scale_exit_ladder",
]
