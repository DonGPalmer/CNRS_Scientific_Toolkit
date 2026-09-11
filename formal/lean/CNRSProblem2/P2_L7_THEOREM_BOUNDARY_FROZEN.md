# P2-L7 theorem boundary — frozen before certification

Status: **FROZEN FOR P2-L7 CANDIDATE**

P2-L7 may add only explicit branch transport and its exact interaction with the
governed P2-L6 branch-aware finite-Hurwitz interface.

## Required declarations

### Value transport

- `shiftBranchedFiniteHurwitz`
- `shiftBranchedFiniteHurwitz_fst`
- `shiftBranchedFiniteHurwitz_snd`
- `shiftBranchedFiniteHurwitz_zero`
- `shiftBranchedFiniteHurwitz_add`
- `shiftBranchedFiniteHurwitz_injective`
- `shiftBranchedFiniteHurwitz_inj`
- `shiftBranchedFiniteHurwitz_neg`
- `shiftBranchedFiniteHurwitz_deriv`
- `shiftBranchedFiniteHurwitz_branch_eq_iff`
- `shiftBranchedFiniteHurwitz_branch_sub`

### Fail-closed serialized transport

- `shiftBranchedFiniteHurwitzCode`
- `shiftBranchedFiniteHurwitzCode_encode`
- `shiftBranchedFiniteHurwitzCode_eq_some_iff`
- `shiftBranchedFiniteHurwitzCode_eq_none_iff`
- `shiftBranchedFiniteHurwitzCode_valid`
- `rawValue_shiftBranchedFiniteHurwitzCode`
- `shiftBranchedFiniteHurwitzCode_normalize`
- `shiftBranchedFiniteHurwitzCode_zero`
- `shiftBranchedFiniteHurwitzCode_add`

### Equivariance and policy preservation

- `shiftBranchedFiniteHurwitzCode_neg_commute`
- `shiftBranchedFiniteHurwitzCode_deriv_commute`
- `addBranchedFiniteHurwitzCode_shift_encode`
- `mulBranchedFiniteHurwitzCode_shift_encode`
- `addBranchedFiniteHurwitzCode_shift_encode_ne`
- `mulBranchedFiniteHurwitzCode_shift_encode_ne`

## Frozen policy

Transport changes only the explicit integer branch. Binary arithmetic remains
partial and requires equal decoded branches. A common transport preserves both
branch equality and branch inequality.

Changing this policy, adding a rule for arithmetic across unequal branches, or
expanding to analytic/path/infinite-stream semantics requires a documented
unfreeze decision.
