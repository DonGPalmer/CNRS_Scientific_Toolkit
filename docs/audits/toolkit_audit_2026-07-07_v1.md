# CNRS Scientific Toolkit — Full In-Session Audit

**Donald G. Palmer | July 7, 2026 (Session 72) | Version 1**

**Repo:** `DonGPalmer/CNRS_Scientific_Toolkit`, branch `main`, pyproject version **0.10.2**
**Companion script:** `toolkit_audit_crossval_v1.py` (15/15 checks pass)
**Live regression run (this session):** `1126 passed, 6 xfailed` in ~15 s

This audit discharges the standing Session-45 item ("CNRS Python suite NOT
audited — repo not accessible in session"). Repo access was established this
session via GitHub API, raw fetch, and tarball download; the toolkit was
installed and executed inside the session sandbox. Method: (1) contamination
sweep against recently refuted/corrected programme claims; (2) independent
cross-validation of core arithmetic against a fresh reference implementation
written without toolkit reuse, per standing protocol; (3) CNRS-H calculus
spot-checks against SymPy; (4) theorem-to-implementation traceability review;
(5) test-suite and metadata hygiene review.

---

## 1. Headline: the toolkit is clean and correct where it matters

**No contamination by refuted or corrected claims.**

- **Four-Value Carry-Set Conjecture (refuted Session 71):** zero occurrences
  anywhere in code, tests, or docs. Better: `cnrs_mul.py` explicitly documents
  that multiplication carries are *not* bounded to a fixed state set, "unlike
  the addition transducer (where carry is bounded to the 14-state [set])" —
  the implementation was never built on the refuted conjecture.
- **This session's physics corrections (F1-3 kernel, L-1/L-3 time dilation):**
  the toolkit's physics layer carries none of them. `cnrs_physics_check.py`
  encodes standard QM reference functions (QHO, hydrogen 1s/2s) used purely
  as EGF verification targets; `cnrs_bio.py` encodes Paper 18's
  reaction-diffusion demonstration profiles. No gravitational kernel, no
  dilation formula, no horizon claim exists in the codebase.

**Independent cross-validation: 15/15.** A fresh reference implementation of
base-(−2+i) greedy expansion (500-sample self-test) was written from scratch
and run against the toolkit:

| Check | Result |
|---|---|
| A1 encode matches independent greedy expansion | 400/400 |
| A2 string decode round-trips | 400/400 |
| A3 addition (14-state transducer) vs complex arithmetic | 300/300 |
| A4 multiplication vs complex arithmetic | 300/300 |
| A5 subtraction vs complex arithmetic | 300/300 |
| A6 digit alphabet always within {0..4} | 200/200 |
| A7 normalization idempotent on canonical strings | 200/200 |
| A8 addition carry set has exactly 14 states (P3 theorem) | confirmed |
| H1 CNRS-H shift D = EGF differentiation | pass |
| H2 CNRS-H evaluate vs SymPy | pass |
| H3 eigenvalue relation D[e^{αρ}] = α e^{αρ} on coefficients | pass |
| H4 D(integrate(f)) = f | pass |
| H5 `compose_native` (Faà di Bruno) vs SymPy series of exp(ρ+ρ²), order 8 | pass |
| H6 `compose(g, invert_native(g))` = identity (Lagrange round-trip) | pass |

**Relevance to today's e-base/hybrid decision:** H3 verifies the eigenvalue
relation *on the shipped implementation* — the two-carrier bridge's proposed
current anchor is not only proved in the capstone but implemented and now
independently spot-checked. The decision note's characterization of CNRS-H
(EGF coefficient calculus; unbounded Gaussian-integer coefficients via
`CVal`; shift = d/dρ) matches `cnrs/h/` and `cnrs_h_native.py` exactly.

**Epistemic discipline is present in the code itself.**
`theorem_alignment.py` ships a 12-record registry mapping features to a
seven-level status vocabulary (theorem_backed / computationally_verified /
conditional / scaffold / bridge / validation / open); `native_status.py` and
`docs/CLAIM_STATUS.md` separate implemented from open claims. README's
capability table matches TC Ch. 21's status register: division "structured
workflows" (partial), CNRS-H "research implementation," metric completeness
and e-base marked open research questions. CI runs pytest on every push/PR.

**xfail inventory: honest.** All 6 expected failures live in one file
(`test_evaluate_limitations.py`), document one known limitation
(`evaluate()` ignores `power_offset` in Laurent-periodic cases), quantify the
error, and name the correct alternative (`z0_adic_value()`). These are
limitation markers, not buried failures.

---

## 2. Findings (all staleness-class; no correctness defects found)

**T-1 (record-side): version staleness against the programme record.** Repo
is at **v0.10.2**; the programme record throughout — BC v72, Framework v15,
TC bibliography, and `CNRS_master_summary_v5` as corrected this morning —
says v0.10.0. Not a repo defect: v0.10.1/0.10.2 are verification and
release-engineering releases (no new mathematical claims), published after
the record's last sync. **Policy decision for Don:** track patch versions in
programme documents, or pin to minor version with a "current: see repo"
pointer. The latter ends this staleness class permanently.

**T-2 (repo-side): internal test-count staleness.** README (two places),
`docs/TEST_STATUS.md`, and the v0.10.2 release notes all state
`1121 passed, 6 xfailed`; live `main` runs **1126 passed** — five tests
added since the v0.10.2 notes. Fix at next release (or generate the number
in CI rather than hand-maintaining it).

**T-3 (repo-side, minor): `docs/CLAIM_STATUS.md` top block is v0.9.0/v0.8.1
era** (headline validation `1015 passed`), with newer content layered as
addenda. The layering is deliberate and historical, but the top-of-file
"current validation" block no longer reflects current state.

**T-4 (observation/API suggestion, not a defect):**
`CnrsH.exponential(d, terms)` builds `d·e^ρ` (all coefficients = d), not
`e^{dρ}` — the docstring is accurate, but the parameter invites misreading
(this audit's harness initially misread it). Given the eigenvalue relation's
new architectural prominence (e-base/hybrid decision note, Option H), a
convenience constructor for the eigenfunction `h_α` (coefficients `α^n`)
would be a natural, cheap addition.

**T-5 (cosmetic):** mixed line endings (`\r\n`) in a few modules
(`cnrs_add.py`, `cnrs_global_solver.py`).

---

## 3. What was NOT audited (scope boundary)

Per-module review of the research-layer workflows (`cnrs_multiscale.py`,
`cnrs_ode.py`, oscillator/reaction-diffusion workflows) was survey-level
only: their formulas were checked for contamination by the session's physics
corrections (clean) but not re-derived line-by-line. The division
classification and rational-value layers were exercised only through the
regression suite. A deeper per-module pass can be scheduled if wanted; the
theorem-alignment registry gives it a ready structure.

---

## 4. Record updates recommended

1. BC/FR v73: log repo accessibility (supersedes the Session-45 limitation
   and the "read-only via raw.githubusercontent.com" note — full download,
   install, and execution now work in-session), the v0.10.2/1126 findings,
   and this audit's completion.
2. Don's decision on T-1 version-tracking policy.
3. Optionally forward T-2/T-3/T-4/T-5 to the toolkit's own issue list for the
   next release.

**Epistemic status:** all PASS/FAIL claims above are established within
current model (independent implementation + live execution, seed-fixed,
reproducible via the companion script). The T-4 API suggestion and policy
recommendations are planning judgments.
