"""
CNRS science layer

Science-facing objects and workflows built around CNRS-H local states.

The preferred v0.7+ pattern keeps the CNRS-H jet/state as the primary
representation and applies observation maps only when an explicit real-valued
quantity is needed.
"""
from .branch import CnrsBranch
from .observation import observe, real, imag, abs_value, abs2, phase, phase_current, observation_table
from .scale_law import CnrsScaleLaw, fit_egf_scale_law, exp_scale_law
from .three_workflows import ThreeWorkflowResult, compare_interference, compare_complex_scale_law, compare_branch_winding

from .state import CnrsScientificState, CnrsScientificStateError, scientific_state_from_symbolic
