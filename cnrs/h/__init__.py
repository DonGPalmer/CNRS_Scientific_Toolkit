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
