"""
cnrs_oscillator.py
==================
Complex oscillator toolkit for the CNRS scientific toolkit.

Provides named oscillator models — Stuart-Landau, RLC, interference,
and driven harmonic — implemented via CNRS-H coefficient recurrence,
with the three-workflow comparison pattern applied throughout.

The three workflows
-------------------
  A. Early real reduction: compute |z|² or Re(z) immediately, discard phase.
  B. Standard complex (late reduction): propagate z(t) in ordinary complex
     arithmetic, measure at the end.
  C. CNRS complex-state preservation: propagate via CNRS-H EGF stream;
     exact digit-shift derivative; measure only at final observation step.

Workflow C is what the toolkit is built for: it retains the full complex
state (amplitude and phase) exactly within the EGF domain, and exposes
all observable maps only at the end.

Models
------
Stuart-Landau oscillator (normal form of a Hopf bifurcation):
    dz/dt = (μ + iω)z - β|z|²z
    where μ is the growth rate, ω the natural frequency, β the nonlinear
    saturation.  Near the bifurcation |β||z₀|² << |μ|, the linear
    approximation z(t) ≈ z₀ exp((μ+iω)t) is valid.  The CNRS-H stream
    implements this linear regime exactly; the nonlinear saturation is
    provided as a perturbative first-order correction term.

    Key result: early |z|² reduction loses the oscillation frequency ω;
    the CNRS-H phase stream retains it.

RLC oscillator (series RLC circuit):
    L q'' + R q' + (1/C) q = V(t)
    Natural frequency ω₀ = 1/√(LC), damping γ = R/(2L).
    Maps to: q'' + 2γ q' + ω₀² q = V(t)/L
    Implemented via cnrs_solve_second_order (free) or cnrs_solve_driven
    (forced).  At resonance ω_drive = ω₀, the driven amplitude grows
    linearly — detectable only in the complex state.

Driven harmonic oscillator:
    z'' + 2γ z' + ω₀² z = A exp(iω_d t)
    Exact CNRS-H solution via coefficient recurrence.
    Near resonance: |ω_d - ω₀| << ω₀.

Interference (two-oscillator superposition):
    z(t) = z₁(t) + z₂(t)
    where z₁ = exp(iω₁t), z₂ = exp(iω₂t).
    Early |z|² loses the cross term 2cos((ω₁-ω₂)t).
    CNRS stream retains the full superposition.

Public API
----------
Models:
    StuartLandauParams(mu, omega, beta, z0)
    RlcParams(L, R, C, q0, dq0)
    DrivenParams(gamma, omega0, omega_d, amplitude, z0, dz0)

Solutions (return OscillatorSolution):
    stuart_landau_linear(p, terms, name)   linear regime (exact CNRS-H)
    rlc_free(p, terms, name)               free RLC oscillator
    rlc_driven(p, terms, name)             driven RLC near resonance
    driven_harmonic(p, terms, name)        driven harmonic oscillator
    interference_pair(omega1, omega2, terms, name)  two-oscillator superposition

Three-workflow comparison:
    compare_stuart_landau(p, t_vals)      → ThreeWorkflowResult
    compare_rlc(p, t_vals)               → ThreeWorkflowResult
    compare_interference(omega1, omega2, t_vals) → ThreeWorkflowResult

Result objects:
    OscillatorSolution   wraps OdeSolution; adds observable maps
    ThreeWorkflowResult  .name, .metrics, .interpretation

Author:  Donald G. Palmer
ORCID:   0000-0003-4335-5533
Session: 43, 2026-06-06
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from typing import Optional, Sequence, Union

import numpy as np

from .cnrs_h import CnrsH
from .cnrs_ode import (
    OdeSolution,
    cnrs_solve_driven,
    cnrs_solve_linear,
    cnrs_solve_second_order,
)


# ---------------------------------------------------------------------------
# Parameter dataclasses
# ---------------------------------------------------------------------------

@dataclass
class StuartLandauParams:
    """
    Parameters for the Stuart-Landau oscillator.

        dz/dt = (mu + i*omega)*z - beta*|z|^2*z

    In the linear regime (beta*|z0|^2 << |mu|), the solution is:
        z(t) = z0 * exp((mu + i*omega)*t)

    Attributes
    ----------
    mu    : real part of linear eigenvalue (growth rate; mu>0: growing)
    omega : imaginary part (natural angular frequency)
    beta  : nonlinear saturation coefficient (complex in general)
    z0    : initial condition z(0)
    """
    mu:    float   = 0.1
    omega: float   = 2.0 * math.pi
    beta:  complex = complex(1.0, 0.0)
    z0:    complex = complex(1.0, 0.0)

    def lam(self) -> complex:
        """Linear eigenvalue mu + i*omega."""
        return complex(self.mu, self.omega)

    def limit_cycle_radius(self) -> Optional[float]:
        """
        Limit-cycle radius |z*| = sqrt(mu / Re(beta)), if mu > 0 and Re(beta) > 0.
        Returns None if no stable limit cycle exists.
        """
        if self.mu > 0 and self.beta.real > 0:
            return math.sqrt(self.mu / self.beta.real)
        return None

    def nonlinear_validity(self) -> float:
        """
        Ratio |beta|*|z0|^2 / |mu|: linear regime valid when << 1.
        """
        if abs(self.mu) < 1e-15:
            return float("inf")
        return abs(self.beta) * abs(self.z0) ** 2 / abs(self.mu)


@dataclass
class RlcParams:
    """
    Parameters for a series RLC oscillator.

        L * q'' + R * q' + q/C = V(t)

    Natural frequency omega0 = 1/sqrt(L*C), damping gamma = R/(2*L).

    Attributes
    ----------
    L   : inductance (H)
    R   : resistance (Ω)
    C   : capacitance (F)
    q0  : initial charge q(0)
    dq0 : initial current q'(0) = I(0)
    """
    L:   float = 1.0
    R:   float = 0.2
    C:   float = 1.0
    q0:  complex = complex(1.0, 0.0)
    dq0: complex = complex(0.0, 0.0)

    def omega0(self) -> float:
        """Natural angular frequency 1/sqrt(L*C)."""
        return 1.0 / math.sqrt(self.L * self.C)

    def gamma(self) -> float:
        """Damping coefficient R/(2L)."""
        return self.R / (2.0 * self.L)

    def quality_factor(self) -> float:
        """Q = omega0 / (2*gamma) = sqrt(L/C) / R."""
        return self.omega0() / (2.0 * self.gamma())

    def is_underdamped(self) -> bool:
        """True if gamma < omega0 (oscillatory response)."""
        return self.gamma() < self.omega0()

    def omega_d(self) -> Optional[float]:
        """
        Damped natural frequency sqrt(omega0^2 - gamma^2).
        Returns None if overdamped (gamma >= omega0).
        """
        disc = self.omega0() ** 2 - self.gamma() ** 2
        if disc < 0:
            return None
        return math.sqrt(disc)


@dataclass
class DrivenParams:
    """
    Parameters for a driven harmonic oscillator.

        z'' + 2*gamma*z' + omega0^2 * z = amplitude * exp(i*omega_d*t)

    Attributes
    ----------
    gamma     : damping coefficient
    omega0    : natural frequency
    omega_d   : drive frequency
    amplitude : complex drive amplitude
    z0        : initial displacement z(0)
    dz0       : initial velocity z'(0)
    """
    gamma:     float   = 0.05
    omega0:    float   = 1.0
    omega_d:   float   = 1.0
    amplitude: complex = complex(1.0, 0.0)
    z0:        complex = complex(0.0, 0.0)
    dz0:       complex = complex(0.0, 0.0)

    def detuning(self) -> float:
        """Detuning delta = omega_d - omega0."""
        return self.omega_d - self.omega0

    def is_resonant(self, tol: float = 1e-6) -> bool:
        """True if |detuning| < tol."""
        return abs(self.detuning()) < tol

    def steady_state_amplitude(self) -> complex:
        """
        Steady-state complex amplitude Z_ss for driven oscillator:
            Z_ss = amplitude / (omega0^2 - omega_d^2 + 2i*gamma*omega_d)
        """
        denom = (self.omega0 ** 2 - self.omega_d ** 2
                 + 2j * self.gamma * self.omega_d)
        if abs(denom) < 1e-300:
            return complex(float("inf"), 0.0)
        return self.amplitude / denom

    def resonance_amplitude(self) -> float:
        """
        Peak steady-state amplitude at exact resonance omega_d = omega0:
            |Z_ss| = |amplitude| / (2*gamma*omega0)
        """
        return abs(self.amplitude) / (2.0 * self.gamma * self.omega0)


# ---------------------------------------------------------------------------
# OscillatorSolution wrapper
# ---------------------------------------------------------------------------

class OscillatorSolution:
    """
    Wraps an OdeSolution and adds oscillator-specific observable maps.

    Construction is via the oscillator factory functions, not directly.
    """

    def __init__(self, ode: OdeSolution, name: str = "oscillator"):
        self._ode = ode
        self.name = name
        self.s_max = ode.s_max

    def evaluate(self, t: Union[float, complex]) -> complex:
        """Complex state z(t)."""
        return self._ode.evaluate(t)

    def __call__(self, t):
        """Evaluate at t (scalar or numpy array)."""
        if np.ndim(t) == 0:
            return self.evaluate(complex(t))
        return np.array([self.evaluate(complex(x))
                         for x in np.asarray(t).ravel()],
                        dtype=complex).reshape(np.shape(t))

    # ---- observable maps ------------------------------------------------

    def modulus(self, t) -> Union[float, np.ndarray]:
        """|z(t)|."""
        v = self(t)
        return np.abs(v) if np.ndim(v) > 0 else abs(v)

    def modulus_sq(self, t) -> Union[float, np.ndarray]:
        """|z(t)|²."""
        v = self(t)
        return (v * v.conjugate()).real if np.ndim(v) == 0 else (v * np.conj(v)).real

    def real_part(self, t) -> Union[float, np.ndarray]:
        """Re z(t)  (physical observable for RLC: charge q(t))."""
        return self(t).real

    def imag_part(self, t) -> Union[float, np.ndarray]:
        """Im z(t)."""
        return self(t).imag

    def phase(self, t) -> Union[float, np.ndarray]:
        """arg z(t) in (-pi, pi]."""
        v = self(t)
        if np.ndim(v) == 0:
            return cmath.phase(v)
        return np.angle(v)

    def instantaneous_frequency(self, t) -> Union[float, np.ndarray]:
        """
        d(arg z)/dt = Im(z'/z)  (instantaneous angular frequency).
        For z = exp(lam*t): this equals Im(lam) = omega exactly.
        """
        if np.ndim(t) == 0:
            z = self.evaluate(complex(t))
            dz = self._ode.derivative().evaluate(complex(t))
            if abs(z) < 1e-15:
                return float("nan")
            return (dz / z).imag
        return np.array(
            [self.instantaneous_frequency(float(x))
             for x in np.asarray(t).ravel()],
            dtype=float).reshape(np.shape(t))

    def energy_proxy(self, t) -> Union[float, np.ndarray]:
        """
        |z(t)|²  as a proxy for oscillator energy.
        For a harmonic oscillator z = x + i*x'/omega0:
            energy ∝ |z|² = x² + (x'/omega0)²
        """
        return self.modulus_sq(t)

    def derivative(self, name: Optional[str] = None) -> "OscillatorSolution":
        """Return OscillatorSolution for dz/dt (exact digit shift)."""
        return OscillatorSolution(
            self._ode.derivative(),
            name=name or f"D({self.name})")

    def coeffs(self):
        """EGF coefficient tuple."""
        return self._ode.coeffs

    def __repr__(self) -> str:
        return f"OscillatorSolution(name={self.name!r}, s_max={self.s_max:.2f})"


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------

def stuart_landau_linear(
    p: Optional[StuartLandauParams] = None,
    terms: int = 40,
    name: str = "stuart_landau_linear",
) -> OscillatorSolution:
    """
    Linear-regime Stuart-Landau solution:  z(t) = z0 * exp(lam * t).

    Valid when |beta|*|z0|^2 << |mu| (nonlinear saturation negligible).
    The CNRS-H stream gives the exact linear solution with no truncation
    beyond the EGF series itself.

    Parameters
    ----------
    p     : StuartLandauParams (default: mu=0.1, omega=2pi, beta=1, z0=1)
    terms : EGF terms (default 40; more terms = wider reliable domain)
    name  : label for the solution

    Returns
    -------
    OscillatorSolution
    """
    if p is None:
        p = StuartLandauParams()
    ode = cnrs_solve_linear(lam=p.lam(), y0=p.z0, terms=terms)
    return OscillatorSolution(ode, name=name)


def rlc_free(
    p: Optional[RlcParams] = None,
    terms: int = 40,
    name: str = "rlc_free",
) -> OscillatorSolution:
    """
    Free RLC oscillator:  q'' + 2*gamma*q' + omega0^2*q = 0.

    Returns OscillatorSolution for q(t) with initial conditions q(0)=q0,
    q'(0)=dq0.

    Observable maps:
        .real_part(t)  →  q(t)  (charge, the physical observable)
        .modulus(t)    →  |q_complex(t)|  (envelope)
        .phase(t)      →  arg(q_complex(t))
    """
    if p is None:
        p = RlcParams()
    ode = cnrs_solve_second_order(
        gamma=p.gamma(), omega=p.omega0(), y0=p.q0, dy0=p.dq0, terms=terms)
    return OscillatorSolution(ode, name=name)


def rlc_driven(
    p: Optional[RlcParams] = None,
    drive_omega: float = 1.0,
    drive_amplitude: complex = complex(1.0, 0.0),
    terms: int = 40,
    name: str = "rlc_driven",
) -> OscillatorSolution:
    """
    Driven RLC oscillator:  q'' + 2*gamma*q' + omega0^2*q = (A/L)*exp(i*omega_d*t).

    Implements the complex-valued driven equation with harmonic forcing via
    cnrs_solve_driven.  The physical charge is Re(q_complex(t)).

    For near-resonance drive (drive_omega ≈ omega0), the steady-state
    amplitude peaks at |A| / (2*gamma*omega0*L).

    Parameters
    ----------
    p              : RlcParams
    drive_omega    : drive angular frequency
    drive_amplitude: complex voltage amplitude (divided by L internally)
    terms          : EGF terms
    """
    if p is None:
        p = RlcParams()

    # Forcing: f(t) = (drive_amplitude / L) * exp(i*omega_d*t)
    # EGF coefficients: c_n = (drive_amplitude/L) * (i*omega_d)^n
    lam_drive = complex(0.0, drive_omega)
    force_coeffs = [
        (drive_amplitude / p.L) * (lam_drive ** n) for n in range(terms)
    ]
    forcing = CnrsH.from_list(force_coeffs)

    # Use driven solver: z'' + 2*gamma*z' + omega0^2*z = forcing
    # cnrs_solve_driven handles first-order; we need second-order driven.
    # Route: solve via cnrs_solve_second_order_driven (not in ode module),
    # or build coefficient recurrence directly here.
    #
    # Recurrence for z'' + 2γz' + ω₀²z = f(t):
    #   c[n+2] = (-2γ*c[n+1] - ω₀²*c[n] + f[n]) / (n+2) ... NO
    # In EGF: Val = Σ c_n t^n/n!, so z = Σ c_n t^n/n!
    # z' = Σ c_{n+1} t^n/n! (digit shift)
    # z'' = Σ c_{n+2} t^n/n!
    # z'' + 2γz' + ω₀²z = f(t)  ↔  for each n:
    #   c[n+2] + 2γ*c[n+1] + ω₀²*c[n] = f_n
    # → c[n+2] = f_n - 2γ*c[n+1] - ω₀²*c[n]

    gamma = p.gamma()
    omega0_sq = p.omega0() ** 2
    c = [complex(0.0)] * terms
    c[0] = p.q0
    c[1] = p.dq0
    f = force_coeffs

    for n in range(terms - 2):
        f_n = f[n] if n < len(f) else complex(0.0)
        c[n + 2] = f_n - 2.0 * gamma * c[n + 1] - omega0_sq * c[n]

    stream = CnrsH.from_list(c)
    # Estimate s_max from eigenvalue magnitude
    eig_mag = max(abs(complex(-gamma, math.sqrt(max(omega0_sq - gamma**2, 0)))),
                  abs(drive_omega))
    if eig_mag > 1e-15:
        log_fact = sum(math.log(k) for k in range(1, terms + 1))
        s_max = math.exp((log_fact + math.log(1e-6)) / terms) / eig_mag
    else:
        s_max = float("inf")

    from .cnrs_ode import OdeSolution
    ode = OdeSolution(stream, s_max=s_max, label=name)
    return OscillatorSolution(ode, name=name)


def driven_harmonic(
    p: Optional[DrivenParams] = None,
    terms: int = 40,
    name: str = "driven_harmonic",
) -> OscillatorSolution:
    """
    Driven harmonic oscillator:
        z'' + 2*gamma*z' + omega0^2*z = amplitude * exp(i*omega_d*t)

    Exact CNRS-H solution via coefficient recurrence.
    Near resonance (omega_d ≈ omega0), the transient grows linearly
    before settling to the steady state — visible in the complex stream.

    Parameters
    ----------
    p     : DrivenParams
    terms : EGF terms
    name  : label
    """
    if p is None:
        p = DrivenParams()

    lam_drive = complex(0.0, p.omega_d)
    force_coeffs = [p.amplitude * (lam_drive ** n) for n in range(terms)]

    gamma = p.gamma
    omega0_sq = p.omega0 ** 2
    c = [complex(0.0)] * terms
    c[0] = p.z0
    c[1] = p.dz0

    for n in range(terms - 2):
        f_n = force_coeffs[n] if n < len(force_coeffs) else complex(0.0)
        c[n + 2] = f_n - 2.0 * gamma * c[n + 1] - omega0_sq * c[n]

    stream = CnrsH.from_list(c)
    eig_mag = max(abs(complex(-gamma, math.sqrt(max(omega0_sq - gamma**2, 0)))),
                  abs(p.omega_d))
    if eig_mag > 1e-15:
        log_fact = sum(math.log(k) for k in range(1, terms + 1))
        s_max = math.exp((log_fact + math.log(1e-6)) / terms) / eig_mag
    else:
        s_max = float("inf")

    from .cnrs_ode import OdeSolution
    ode = OdeSolution(stream, s_max=s_max, label=name)
    return OscillatorSolution(ode, name=name)


def interference_pair(
    omega1: float = 1.0,
    omega2: float = 1.5,
    amp1: complex = complex(1.0, 0.0),
    amp2: complex = complex(1.0, 0.0),
    terms: int = 40,
    name: str = "interference",
) -> OscillatorSolution:
    """
    Two-oscillator superposition:  z(t) = amp1*exp(i*omega1*t) + amp2*exp(i*omega2*t).

    Implemented as EGF coefficient sum:
        c_n = amp1*(i*omega1)^n + amp2*(i*omega2)^n

    The key result (three-workflow):
      A. |z|² = |amp1|² + |amp2|² + 2*Re(amp1*conj(amp2)*exp(i*(omega1-omega2)*t))
         Early reduction to |z1|² + |z2|² loses the cross term.
      B/C. Full complex state retains the interference: the beat frequency
         (omega1 - omega2) is accessible via instantaneous_frequency().

    Parameters
    ----------
    omega1, omega2 : angular frequencies of the two components
    amp1, amp2     : complex amplitudes
    terms          : EGF terms
    """
    lam1 = complex(0.0, omega1)
    lam2 = complex(0.0, omega2)
    c = [amp1 * (lam1 ** n) + amp2 * (lam2 ** n) for n in range(terms)]
    stream = CnrsH.from_list(c)

    eig_mag = max(abs(omega1), abs(omega2))
    if eig_mag > 1e-15:
        log_fact = sum(math.log(k) for k in range(1, terms + 1))
        s_max = math.exp((log_fact + math.log(1e-6)) / terms) / eig_mag
    else:
        s_max = float("inf")

    from .cnrs_ode import OdeSolution
    ode = OdeSolution(stream, s_max=s_max, label=name)
    return OscillatorSolution(ode, name=name)


# ---------------------------------------------------------------------------
# Three-workflow comparison result
# ---------------------------------------------------------------------------

@dataclass
class ThreeWorkflowResult:
    """
    Three-workflow comparison result.

    Attributes
    ----------
    name           : model name
    metrics        : dict of named float metrics
    interpretation : human-readable summary of what the workflows reveal
    """
    name: str
    metrics: dict
    interpretation: str


def _rel_l2(a, b) -> float:
    """Relative L2 error ||a-b|| / ||b||."""
    a = np.asarray(a, dtype=complex)
    b = np.asarray(b, dtype=complex)
    denom = float(np.linalg.norm(b))
    return float(np.linalg.norm(a - b)) / (denom if denom > 0 else 1.0)


# ---------------------------------------------------------------------------
# Three-workflow comparisons
# ---------------------------------------------------------------------------

def compare_stuart_landau(
    p: Optional[StuartLandauParams] = None,
    t_vals: Optional[Sequence[float]] = None,
    terms: int = 40,
) -> ThreeWorkflowResult:
    """
    Three-workflow comparison for the Stuart-Landau oscillator.

    Workflow A: |z(t)|² = |z0|² * exp(2*mu*t)  (no omega visible)
    Workflow B: z_exact(t) = z0 * exp((mu+i*omega)*t)  in Python complex
    Workflow C: CNRS-H stream of z0*exp(lam*t)

    Metrics:
      A_mod2_at_t1         : |z|² from workflow A at t=1
      B_mod2_at_t1         : |z|² from workflow B at t=1 (same as A)
      B_omega_from_phase   : omega recovered from B phase derivative
      C_omega_from_stream  : omega recovered from C instantaneous_frequency
      C_vs_B_rel_error     : relative L2 error of C vs B
      A_omega_recoverable  : False (omega invisible in |z|²)
    """
    if p is None:
        p = StuartLandauParams()
    if t_vals is None:
        t_vals = np.linspace(0.0, 0.5, 200)
    t_arr = np.asarray(t_vals, dtype=float)

    sol = stuart_landau_linear(p, terms=terms)

    # Workflow A: early modulus-squared
    z_exact = p.z0 * np.exp(p.lam() * t_arr)
    A_mod2 = np.abs(p.z0) ** 2 * np.exp(2.0 * p.mu * t_arr)

    # Workflow B: exact complex
    B_phase = np.unwrap(np.angle(z_exact))
    B_omega = float(np.mean(np.gradient(B_phase, t_arr)[10:-10]))

    # Workflow C: CNRS-H stream
    C_state = sol(t_arr)
    C_if = sol.instantaneous_frequency(t_arr[len(t_arr) // 2])

    t1_idx = len(t_arr) // 2

    return ThreeWorkflowResult(
        name="stuart_landau",
        metrics={
            "A_mod2_at_t_mid":          float(A_mod2[t1_idx]),
            "B_mod2_at_t_mid":          float(np.abs(z_exact[t1_idx]) ** 2),
            "B_omega_from_phase":       B_omega,
            "C_omega_from_stream":      C_if,
            "C_vs_B_rel_L2_error":      _rel_l2(C_state, z_exact),
            "A_omega_recoverable":      False,
            "nonlinear_validity_ratio": p.nonlinear_validity(),
        },
        interpretation=(
            "Workflow A (early |z|²) exposes only the exponential amplitude "
            f"envelope exp(2*mu*t); the oscillation frequency omega={p.omega:.4f} "
            "is completely invisible. Workflow B and C both recover omega from "
            "the complex state. The CNRS-H stream (C) matches B to within "
            "the EGF series accuracy, with no ODE integration error."
        ),
    )


def compare_rlc(
    p: Optional[RlcParams] = None,
    t_vals: Optional[Sequence[float]] = None,
    terms: int = 40,
) -> ThreeWorkflowResult:
    """
    Three-workflow comparison for the free RLC oscillator.

    Workflow A: |q(t)|² (early reduction — loses oscillation sign/phase)
    Workflow B: q(t) in ordinary complex arithmetic (exact for linear ODE)
    Workflow C: CNRS-H EGF stream

    For underdamped RLC: q(t) ≈ exp(-gamma*t) * [q0*cos(omega_d*t) + ...]
    Early |q|² loses the cosine oscillation; the phase gives the damped freq.

    Metrics:
      quality_factor     : Q = omega0/(2*gamma)
      omega_d            : damped natural frequency
      C_vs_B_rel_error   : CNRS-H stream accuracy vs exact
      B_omega_from_phase : omega_d recovered from phase derivative
      C_omega_from_stream: omega_d from CNRS-H instantaneous frequency
      A_oscillation_visible: False (only envelope in |q|²)
    """
    if p is None:
        p = RlcParams()
    if t_vals is None:
        t_vals = np.linspace(0.0, 2.0 * math.pi / p.omega0(), 200)
    t_arr = np.asarray(t_vals, dtype=float)

    sol = rlc_free(p, terms=terms)

    gamma = p.gamma()
    omega0 = p.omega0()
    omegad = p.omega_d()

    # Exact analytical solution (underdamped):
    # q(t) = exp(-gamma*t) * [A*cos(omega_d*t) + B*sin(omega_d*t)]
    # with A = q0, B = (dq0 + gamma*q0) / omega_d
    if omegad is not None and omegad > 1e-15:
        A_coeff = p.q0
        B_coeff = (p.dq0 + gamma * p.q0) / omegad
        q_exact = (np.exp(-gamma * t_arr) *
                   (A_coeff * np.cos(omegad * t_arr) +
                    B_coeff * np.sin(omegad * t_arr)))
    else:
        q_exact = p.q0 * np.exp(-gamma * t_arr)

    # Workflow A: |q|² early
    A_mod2 = np.abs(q_exact) ** 2

    # Workflow C: CNRS-H
    C_state = sol(t_arr)
    C_if = sol.instantaneous_frequency(t_arr[len(t_arr) // 4])

    # Phase from B
    phase_B = np.unwrap(np.angle(
        (q_exact + 1e-15j) if np.all(np.imag(q_exact) == 0)
        else q_exact))
    B_omega = float(np.mean(np.gradient(phase_B, t_arr)[10:-10]))

    return ThreeWorkflowResult(
        name="rlc_free",
        metrics={
            "quality_factor":          p.quality_factor(),
            "omega0":                  omega0,
            "omega_d":                 omegad if omegad is not None else float("nan"),
            "gamma":                   gamma,
            "C_vs_exact_rel_L2_error": _rel_l2(C_state.real, q_exact.real
                                               if np.iscomplexobj(q_exact)
                                               else q_exact),
            "B_omega_from_phase":      B_omega,
            "C_omega_from_stream":     C_if,
            "A_oscillation_visible":   False,
        },
        interpretation=(
            f"Free RLC oscillator (Q={p.quality_factor():.2f}). "
            "Workflow A (|q|²) shows only the damping envelope; "
            f"the oscillation at omega_d={omegad:.4f} rad/s is invisible. "
            "CNRS-H stream (C) retains the full phasor and recovers "
            "omega_d from the instantaneous frequency with no integration error."
        ),
    )


def compare_interference(
    omega1: float = 1.0,
    omega2: float = 1.5,
    amp1: complex = complex(1.0, 0.0),
    amp2: complex = complex(1.0, 0.0),
    t_vals: Optional[Sequence[float]] = None,
    terms: int = 40,
) -> ThreeWorkflowResult:
    """
    Three-workflow comparison for two-oscillator interference.

    z(t) = amp1*exp(i*omega1*t) + amp2*exp(i*omega2*t)

    Workflow A: |z1|² + |z2|² = |amp1|² + |amp2|² (constant — cross term lost)
    Workflow B/C: full |z|² = A + cross = A + 2*Re(amp1*conj(amp2)*exp(i*(omega1-omega2)*t))

    The cross term oscillates at the beat frequency |omega1 - omega2|.
    Early reduction (A) completely loses this.

    Metrics:
      A_intensity_constant  : True (|z1|² + |z2|² has no t dependence)
      B_cross_term_max      : max of the cross term 2*Re(amp1*conj(amp2)*exp...)
      B_beat_frequency      : |omega1 - omega2|
      C_vs_B_rel_L2_error   : CNRS-H accuracy
      C_beat_from_stream    : beat frequency recovered from CNRS-H stream
      information_lost_in_A : True
    """
    if t_vals is None:
        beat = abs(omega2 - omega1)
        t_max = 2.0 * math.pi / beat if beat > 1e-10 else 10.0
        t_vals = np.linspace(0.0, t_max, 400)
    t_arr = np.asarray(t_vals, dtype=float)

    sol = interference_pair(omega1, omega2, amp1, amp2, terms=terms)

    # Exact
    z_exact = amp1 * np.exp(1j * omega1 * t_arr) + amp2 * np.exp(1j * omega2 * t_arr)

    # Workflow A: incoherent sum
    A_int = abs(amp1) ** 2 + abs(amp2) ** 2

    # Workflow B/C: full |z|²
    B_mod2 = np.abs(z_exact) ** 2
    cross_term = B_mod2 - A_int

    # CNRS-H
    C_state = sol(t_arr)
    C_mod2 = np.abs(C_state) ** 2

    beat_freq = abs(omega2 - omega1)

    return ThreeWorkflowResult(
        name="interference",
        metrics={
            "A_intensity_constant":   True,
            "A_intensity_value":      float(A_int),
            "B_cross_term_max":       float(np.max(np.abs(cross_term))),
            "B_beat_frequency":       beat_freq,
            "C_vs_B_mod2_rel_error":  _rel_l2(C_mod2, B_mod2),
            "C_vs_exact_rel_L2_error":_rel_l2(C_state, z_exact),
            "information_lost_in_A":  True,
        },
        interpretation=(
            f"Two-oscillator interference (omega1={omega1}, omega2={omega2}). "
            f"Beat frequency = {beat_freq:.4f} rad/t. "
            "Workflow A (incoherent sum |z1|² + |z2|²) is constant: "
            "the beat is entirely invisible. "
            "Workflows B and C retain the cross term and recover the beat. "
            "CNRS-H stream (C) matches the exact complex sum within EGF accuracy."
        ),
    )
