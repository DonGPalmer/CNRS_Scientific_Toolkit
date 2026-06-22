"""Direct CNRS-H chain-rule façade."""
from ..cnrs_h_chain import (
    ChainRuleComparison, CnrsHChainError, compose_series, chain_rule_lhs, chain_rule_rhs,
    verify_chain_rule, power_series, exp_series, sin_series, cos_series, monomial,
    identity, constant, multiply_truncated, truncate_pad, max_coeff_error,
)
__all__ = [name for name in globals() if not name.startswith("_")]
