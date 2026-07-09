# Gaussian-Rational Periodicity in Base \(z_0=-2+i\)

**Working theorem note for the CNRS programme**  
**Donald G. Palmer — July 2026**

## 1. Setting

Let

\[
z_0=-2+i,\qquad D=\{0,1,2,3,4\},
\]

and let \(\mathbb Z[i]\) be the Gaussian integers and \(\mathbb Q(i)\) their field of fractions.

For a Gaussian integer \(w=A+Bi\), define the residue map

\[
\phi(w)=A+2B\pmod 5.
\]

Because \(i\equiv 2\pmod{z_0}\), this is exactly the reduction map
\(\mathbb Z[i]\to \mathbb Z[i]/(z_0)\cong \mathbb F_5\).

A right-infinite \(z_0\)-adic digit sequence means

\[
\sum_{n\ge 0} d_n z_0^n,\qquad d_n\in D.
\]

A Laurent-periodic sequence allows a finite negative power offset:

\[
\sum_{n\ge 0} d_n z_0^{n-\nu},\qquad \nu\ge 0.
\]

These series are not ordinarily convergent in the complex norm because
\(|z_0|=\sqrt 5>1\). Their values are assigned algebraically by the finite
prefix plus periodic-tail closed form.

---

## 2. Main theorem

### Theorem (Gaussian-rational eventual periodicity)

Every Gaussian rational \(x\in\mathbb Q(i)\) has an eventually periodic
Laurent base-\(z_0\) expansion with digits in \(D\).

More precisely, write \(x=P/Q\) with \(P,Q\in\mathbb Z[i]\), \(Q\ne 0\).
Let

\[
\nu=v_{z_0}(Q)
\]

be the exponent of the Gaussian prime \(z_0\) in \(Q\), and write

\[
Q=z_0^\nu Q_0,\qquad z_0\nmid Q_0.
\]

Then

\[
x=z_0^{-\nu}\frac{P}{Q_0},
\]

and \(P/Q_0\) has an eventually periodic \(z_0\)-adic expansion

\[
\frac{P}{Q_0}=\sum_{n\ge 0}d_n z_0^n
\]

in the algebraic periodic-tail sense. Hence \(x\) has an eventually periodic
Laurent expansion beginning at power \(-\nu\).

Conversely, every eventually periodic Laurent base-\(z_0\) digit string with
digits in \(D\) represents an element of \(\mathbb Q(i)\).

Therefore:

\[
\boxed{
x\in\mathbb Q(i)
\iff
x\text{ has an eventually periodic Laurent base-}(-2+i)\text{ expansion.}
}
\]

---

## 3. Digit recurrence

Assume first that \(z_0\nmid Q\). Since \(\phi(Q)\ne 0\) in \(\mathbb F_5\),
it has an inverse modulo \(5\).

Set \(N_0=P\). For each \(n\ge 0\), choose the unique digit

\[
d_n\equiv \phi(N_n)\phi(Q)^{-1}\pmod 5,
\qquad d_n\in D.
\]

Then

\[
\phi(N_n-d_nQ)=0,
\]

so \(z_0\mid N_n-d_nQ\), and the next state

\[
N_{n+1}=\frac{N_n-d_nQ}{z_0}
\]

lies again in \(\mathbb Z[i]\).

Rearranging,

\[
\frac{N_n}{Q}
=
d_n+z_0\frac{N_{n+1}}{Q}.
\]

Iteration gives, for every \(m\ge 1\),

\[
\frac{P}{Q}
=
\sum_{n=0}^{m-1}d_n z_0^n
+
z_0^m\frac{N_m}{Q}.
\]

---

## 4. Boundedness lemma

### Lemma

The state sequence \((N_n)\subset\mathbb Z[i]\) is bounded.

### Proof

Because \(0\le d_n\le 4\),

\[
|N_{n+1}|
=
\frac{|N_n-d_nQ|}{|z_0|}
\le
\frac{|N_n|+4|Q|}{\sqrt 5}.
\]

Let

\[
R=\frac{4|Q|}{\sqrt 5-1}.
\]

If \(|N_n|>R\), then

\[
\frac{|N_n|+4|Q|}{\sqrt 5}<|N_n|.
\]

Thus outside the closed disk of radius \(R\), the state norm strictly
decreases. Once the sequence enters that disk, the same recurrence bounds it
by a fixed slightly larger disk. Therefore all states lie in a bounded subset
of the Gaussian integer lattice.

A bounded subset of \(\mathbb Z[i]\) is finite. Hence some state repeats.

\(\square\)

---

## 5. Eventual periodicity

Suppose

\[
N_r=N_s,\qquad 0\le r<s.
\]

The digit rule is deterministic, so the subsequent states and digits repeat:

\[
N_{r+k}=N_{s+k},\qquad d_{r+k}=d_{s+k}
\]

for every \(k\ge 0\). Therefore the digit sequence is eventually periodic,
with preperiod \(r\) and period \(T=s-r\).

If some \(N_m=0\), then all later digits are zero and the expansion
terminates.

This proves the forward direction for denominators coprime to \(z_0\).
The general case follows by removing the finite factor \(z_0^\nu\), which
shifts all powers by \(-\nu\).

---

## 6. Converse theorem

Suppose a Laurent expansion has finite prefix and repeating block:

\[
x=
\sum_{n=0}^{r-1}a_n z_0^{n-\nu}
+
\sum_{k\ge 0}\sum_{j=0}^{T-1}
b_jz_0^{r+j+kT-\nu}.
\]

The periodic part is algebraically

\[
z_0^{r-\nu}
\left(\sum_{j=0}^{T-1}b_jz_0^j\right)
\frac{1}{1-z_0^T}.
\]

Every quantity in this expression lies in \(\mathbb Q(i)\), so \(x\in\mathbb
Q(i)\).

---

## 7. Exact termination criterion

### Corollary

A Gaussian rational \(x=P/Q\), written in lowest Gaussian-integer terms,
has a finite Laurent base-\(z_0\) expansion if and only if every Gaussian
prime divisor of \(Q\) is associate to \(z_0\).

Equivalently,

\[
x\in \mathbb Z[i][z_0^{-1}].
\]

Thus a reduced denominator may be removed finitely exactly when

\[
Q=u z_0^m
\]

for some Gaussian unit \(u\in\{\pm1,\pm i\}\) and \(m\ge 0\).

This is the direct complex-base analogue of the ordinary base-\(b\)
termination criterion.

---

## 8. Important consequence for ordinary integer denominators

For a positive integer denominator \(q\), factorization in \(\mathbb Z[i]\)
must be used, not merely the rational-prime valuation \(v_5(q)\).

Since

\[
5=z_0\overline{z_0},
\]

a denominator \(5^m\) contains both the \(z_0\) and \(\overline{z_0}\)
prime factors. Therefore \(1/5\) does **not** terminate in base \(z_0\).
It has a shifted eventually periodic expansion.

A fraction \(P/5^m\) terminates only when the numerator cancels the entire
\(\overline{z_0}^{\,m}\) factor, equivalently when

\[
\overline{z_0}^{\,m}\mid P.
\]

This identifies a classification issue in a denominator-only API:
a pure power of \(5\) is not by itself sufficient to conclude termination.

---

## 9. Period bounds

The proof gives a finite, though coarse, period bound.

For denominator \(Q\) coprime to \(z_0\), all states eventually lie in a disk

\[
|N|\le R_Q
\]

with \(R_Q\) proportional to \(|Q|\). Hence the total number of possible
Gaussian-integer states is \(O(|Q|^2)\), so the sum of preperiod and period
length is also \(O(|Q|^2)\).

A sharper arithmetic bound should be sought through the finite quotient ring

\[
\mathbb Z[i]/(Q).
\]

When \(z_0\) is invertible modulo \(Q\), the periodic dynamics are governed by
multiplication by \(z_0^{-1}\) together with the canonical digit correction.
The period is therefore expected to divide, or be controlled by, an order in
a finite ring or one of its unit groups. Establishing the exact minimal-period
formula is a separate next theorem.

---

## 10. CNRS status

The result proved here is:

- **Established within the stated algebraic model** for the recurrence and
  algebraic periodic-tail value map.
- It does not assert ordinary complex convergence of the right-infinite
  \(z_0\)-adic series.
- It distinguishes three notions that must remain separate:
  1. finite Laurent representation;
  2. algebraically evaluated eventual periodicity;
  3. \(z_0\)-adic convergence in the corresponding completion.

The theorem supplies the formal basis for the Toolkit's finite, periodic, and
shifted-periodic rational-expansion classes.
