# Experimental finite CNRS-H integration contract

**Status:** Working integration candidate only; not stable Toolkit API, merged source, published v0.19.0, or new Lean proof.

The reviewed additions live under the qualified modules `cnrs.cnrs_h_finite_exact` and `cnrs.cnrs_h_toolkit_interop`. Do not change `cnrs/__init__.py` or the existing `CnrsHNative` / `CnrsHJet` classes. There are no new root-level exports.

The additional `cnrs.cnrs_h_limits.BoundedFiniteOps` is the opt-in resource-checked interface. It limits numeral spelling, integer bit size, localized denominator power, finite jet degree, convolution term count, and validates results. It operates on exact `R_A = Z[i][(-2+i)^(-1)]` coefficients only; it does not admit arbitrary `Q(i)` coefficients. Core classes remain available only as **experimental unchecked research primitives**. They are not suitable as untrusted-input APIs and this facade is not a hardened execution sandbox or wall-clock limit. Process quotas and a trusted data origin are still required.

`ToolkitDigitOps` is the separate reference interop witness using injected published digit addition and multiplication. It has its own limits and is not a replacement for the bounded finite facade. Do not consider it a stable ABI contract or a formal Lean extraction.

Integration tests should include `tests/test_cnrs_h_finite_exact.py`, `tests/test_cnrs_h_finite_interop.py` and `tests/test_cnrs_h_limits.py`, and run the full repository suite on GitHub Actions. Verify Python 3.9+, the wheel and sdist on isolated installations, and the complete formal source inventory before asking for merge approval. The candidate MUST have a new release identity before any public release: no changed wheel may be distributed as v0.19.0.
