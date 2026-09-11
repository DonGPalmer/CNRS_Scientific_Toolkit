/-
CNRSArithmetic compatibility adapter onto CNRSCore.Base.
-/
import CNRSCore.Base

open Zsqrtd

namespace CNRSArithmetic

abbrev beta : GaussianInt := CNRSCore.beta

@[simp] lemma beta_re : beta.re = -2 := CNRSCore.beta_re
@[simp] lemma beta_im : beta.im = 1 := CNRSCore.beta_im

lemma norm_beta : beta.norm = 5 := CNRSCore.norm_beta
lemma natAbs_norm_beta : beta.norm.natAbs = 5 := CNRSCore.natAbs_norm_beta

lemma irreducible_of_natAbs_norm_prime {z : GaussianInt}
    (hz : Nat.Prime z.norm.natAbs) : Irreducible z :=
  CNRSCore.irreducible_of_natAbs_norm_prime hz

lemma prime_beta : Prime beta := CNRSCore.prime_beta

end CNRSArithmetic
