import CNRSProblem2.BranchCover
import CNRSProblem2.CanonicalLiftedLog
import CNRSProblem2.BranchSerialization
import CNRSProblem2.FiniteLaurentValueCodec
import CNRSProblem2.FiniteHurwitz
import CNRSProblem2.BranchedFiniteHurwitz
import CNRSProblem2.BranchTransport
import CNRSProblem2.BranchOrbit
import CNRSProblem2.CNRSIntegration
import CNRSProblem2.FiniteHurwitzAntiderivative

/-!
CNRS Problem 2 formalization.

P2-L1 establishes the branch-cover coordinate carrier and multiplicative
algebra. P2-L2 adds canonical `(-π, π]` coordinates, the nonzero-complex
projection, mutually inverse lifted logarithm/exponential maps, and the
canonical multiplication wrap cocycle. P2-L3 adds lossless branch-control
serialization, abstract composition with a verified value codec, and exact
canonical-coordinate recovery. P2-L4 adds the finite-Laurent CNRS-A value
carrier over `R_A`, canonical fail-closed value coding, exact finite-code
operations, and concrete composition with the P2-L3 branch codec.
P2-L5 adds the finite-support CNRS-H carrier over the P2-L4 coefficient ring,
binomial-convolution ring algebra, shift differentiation with the exact
Leibniz rule, and a canonical fail-closed sparse codec and code operations.
P2-L6 composes that codec with the P2-L3 branch-index codec, preserves branch
metadata under unary operations, and makes binary operations fail closed when
the decoded branches differ. P2-L7 adds explicit integer branch transport,
a genuine reindexing action, and exact equivariance with the P2-L6 operations.
P2-L8 classifies diagonal branch-transport orbits of ordered pairs by their
two finite-Hurwitz values and relative branch, provides a canonical
first-branch-zero representative and fail-closed pair canonicalization, and
identifies the exact zero-relative-branch domain of the P2-L6 binary operations.
P2-L9 connects the canonical sheet coordinate of a branch point to explicit
finite-Hurwitz branch metadata, with full-turn transport equivariance,
fail-closed attached-state coding, and compatibility with the P2-L8 relative
pair normal form.
P2-L10 adds a chosen-constant finite Hurwitz antiderivative, exact two-sided
reversal with differentiation, fail-closed serialized operations, and branch,
transport, attachment, and relative-pair compatibility.
-/
