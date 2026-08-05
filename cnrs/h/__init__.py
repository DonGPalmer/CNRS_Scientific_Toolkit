"""CNRS-H native calculus layer.

This package is the primary home for coefficient calculus: series, jets,
composition, chain rule, domain diagnostics, and Taylor-model metadata.
"""
from .series import CnrsH, HStream
from .calculus import Operator
from .compose import compose_series, multiply_truncated, truncate_pad
from .chain_rule import (
    ChainRuleComparison,
    CnrsHChainError,
    chain_rule_lhs,
    chain_rule_rhs,
    verify_chain_rule,
    power_series,
    exp_series,
    sin_series,
    cos_series,
    monomial,
    identity,
    constant,
)
from .jet import (
    CnrsHJet,
    CnrsHJetError,
    JetChainRuleComparison,
    jet_from_cnrsh,
    jet_from_symbolic,
    jet_constant,
    jet_identity,
    verify_jet_chain_rule,
    BranchState,
)
from ..cnrs_h_branch import (
    BranchConflict,
    BranchMergeResult,
    merge_branch_states,
    branch_state_from_symbolic,
    branch_merge_report,
    branch_note_for_composition,
)
from ..cnrs_h_path import (
    ContinuationPathError,
    PathSegment,
    BranchPoint,
    WindingEvent,
    ContinuationPath,
    circle_path,
    winding_number,
    winding_events,
    update_branch_state_along_path,
    continue_log,
    continue_sqrt,
    path_history_note,
)

from ..cnrs_h_continuation import (
    CnrsHContinuationError,
    BranchDelta,
    ContinuationRebuildResult,
    branch_delta_from_events,
    shift_symbolic_branches,
    continued_jet_from_symbolic,
)

from .domain import (
    CnrsHDomain,
    INF,
    combine_domains,
    domain_from_radius,
    infer_symbolic_domain,
    estimate_next_term_error,
)
from .taylor_model import (
    CnrsHTaylorModel,
    TaylorModelError,
    TaylorModelChainRuleComparison,
    taylor_model_from_jet,
    taylor_model_from_symbolic,
    verify_taylor_model_chain_rule,
)

__all__ = [name for name in globals() if not name.startswith("_")]

from ..generalized_branch import (
    GeneralizedBranchError,
    BranchObject,
    BranchTransition,
    BranchRegistry,
    GeneralizedContinuationResult,
    apply_branch_registry,
    continue_symbolic_with_registry,
)
from ..cnrs_h_continuation import (
    GeneralizedContinuationRebuildResult,
    continued_jet_from_branch_registry,
)
