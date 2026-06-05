"""
CNRS Scientific Toolkit v0.1

Experimental scientific workflow helpers built on top of the core CNRS package.

The science layer is intentionally interoperable: standard Python complex/float
values at the boundaries, CNRS representations inside selected workflows.
"""
from .branch import CnrsBranch
from .observation import observe, real, imag, abs_value, abs2, phase, phase_current, observation_table
from .scale_law import CnrsScaleLaw, fit_egf_scale_law, exp_scale_law
from .three_workflows import ThreeWorkflowResult, compare_interference, compare_complex_scale_law, compare_branch_winding
