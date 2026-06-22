"""CNRS-H local-domain and convergence diagnostics."""
from ..cnrs_h_domain import (
    CnrsHDomain, INF, combine_domains, domain_from_radius,
    infer_symbolic_domain, estimate_next_term_error,
)
__all__ = [name for name in globals() if not name.startswith("_")]
