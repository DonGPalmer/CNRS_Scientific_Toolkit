"""Comparison helpers for native CNRS-H and reference methods."""
from ..cnrs_h_bridge import (
    BridgeComparison, compare_symbolic_and_cnrs_h_derivative,
    compare_symbolic_and_cnrs_h_integral, max_coeff_error, evaluate_cnrsh_series,
)
from ..cnrs_h_chain import ChainRuleComparison, verify_chain_rule
from ..cnrs_h_jet import JetChainRuleComparison, verify_jet_chain_rule
from ..cnrs_h_taylor_model import TaylorModelChainRuleComparison, verify_taylor_model_chain_rule

__all__ = [
    "BridgeComparison", "compare_symbolic_and_cnrs_h_derivative", "compare_symbolic_and_cnrs_h_integral",
    "max_coeff_error", "evaluate_cnrsh_series", "ChainRuleComparison", "verify_chain_rule",
    "JetChainRuleComparison", "verify_jet_chain_rule", "TaylorModelChainRuleComparison",
    "verify_taylor_model_chain_rule",
]
