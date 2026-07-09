"""Independent reference checks for the principal scientific workflow modules."""
import cmath, math
import numpy as np
from cnrs.cnrs_ode import cnrs_solve_linear, cnrs_solve_second_order
from cnrs.cnrs_scale import ScaleLaw
from cnrs.cnrs_bio import GmParams, da_profile, dh_profile, d_ratio, gm_steady_state, gm_jacobian
from cnrs.cnrs_oscillator import StuartLandauParams, stuart_landau_linear
from cnrs.cnrs_interop import solve_and_compare


def test_linear_ode_against_closed_form_grid():
    lam=-0.35+1.2j; y0=1.3-0.2j
    sol=cnrs_solve_linear(lam,y0,terms=45)
    for s in np.linspace(0,1.5,13):
        assert abs(sol.evaluate(float(s),warn=False)-y0*cmath.exp(lam*s)) < 1e-11


def test_second_order_against_cosine():
    sol=cnrs_solve_second_order(0,2,y0=1,dy0=0,terms=45)
    for s in np.linspace(0,2,17):
        assert abs(sol.evaluate(float(s),warn=False).real-math.cos(2*s)) < 1e-10


def test_scale_law_exponential_reference():
    law=ScaleLaw.exponential(-0.4, scale=2.5, terms=40)
    for s in np.linspace(0,2,9):
        assert abs(law.evaluate(float(s)).real-2.5*math.exp(-0.4*s)) < 1e-10


def test_biology_profiles_and_steady_state_reference():
    p=GmParams()
    for s in [0,.25,.5,1.0]:
        assert abs(da_profile(terms=45).evaluate(s).real - p.da0*math.exp(-s/3)) < 1e-10
        assert abs(dh_profile(terms=45).evaluate(s).real - p.dh0*math.exp(-2*s)) < 1e-10
        assert abs(d_ratio(terms=45).evaluate(s).real - (p.dh0/p.da0)*math.exp(-5*s/3)) < 1e-8
    u,v=gm_steady_state(p)
    assert abs(u-(1+p.c))<1e-14 and abs(v-u*u)<1e-14
    J=gm_jacobian(p)
    assert np.trace(J)<0 and np.linalg.det(J)>0


def test_complex_oscillator_against_closed_form():
    p=StuartLandauParams(mu=-0.2, omega=1.1, beta=0.0, z0=1.2-0.3j)
    osc=stuart_landau_linear(p, terms=50)
    lam=-0.2+1.1j
    for t in np.linspace(0,2,9):
        assert abs(osc.evaluate(float(t))-(1.2-0.3j)*cmath.exp(lam*t)) < 1e-10


def test_interop_workflow_returns_consistent_endpoints():
    grid=np.linspace(0,1,30)
    result=solve_and_compare(-0.2+0.7j,1+0.1j,grid,terms=40)
    assert np.max(np.abs(result.cnrs_vals-result.exact_vals)) < 1e-10
    assert np.max(np.abs(result.scipy_vals-result.exact_vals)) < 1e-8
