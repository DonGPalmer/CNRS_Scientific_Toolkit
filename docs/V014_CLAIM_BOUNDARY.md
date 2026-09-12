# v0.14.0 claim boundary

Status: FROZEN FOR IMPLEMENTATION

## Claims permitted only after all release gates pass

The Toolkit may state that v0.14.0:

- provides a lazy, replayable digit stream for exact Gaussian-rational CNRS division;
- detects termination or eventual periodicity by an exact bounded state search;
- emits deterministic, independently revalidated division witnesses;
- agrees exactly with the existing canonical eventually-periodic API on the acceptance domain;
- is theorem-aligned with the cited Lean development where the alignment registry names the corresponding definitions or theorems.

“Exact” refers to integer, Gaussian-integer, and rational arithmetic in the Python implementation. “Theorem-aligned” means that separately implemented Python behavior is checked against stated formal concepts; it does not mean the Python code was extracted from Lean or proved correct by Lean.

## Claims expressly prohibited

v0.14.0 must not claim:

- that the Python runtime is Lean-extracted, Lean-certified, or formally verified;
- that LIMIT_REACHED proves aperiodicity, nontermination, or failure of representation;
- a universal numerical upper bound on cycle discovery unless separately proved and cited;
- support for arbitrary real or complex input streams;
- closure of arbitrary infinite CNRS streams under division;
- streaming multiplication or general infinite-stream field arithmetic;
- analytic convergence, analytic continuation, or certified approximation error;
- completion of a P3 or later formal milestone not present in the certified Lean source.

## Required language

README, release notes, API documentation, and provenance must use “exact Gaussian-rational streaming division” or an equivalently narrow phrase. Any formal-method statement must preserve the distinction between Lean-verified mathematics and independently implemented Python runtime behavior.

## Gate to broaden a claim

A broader claim requires all of:

1. a named theorem or specification covering the broader domain;
2. an implementation-to-theorem mapping;
3. adversarial and property-based acceptance evidence;
4. an independent audit of source identity, runtime behavior, and wording;
5. an explicit governed approval recorded after the audit.

Passing tests alone does not broaden this boundary.
