# Independent review of calibrated eligibility-gate bounds

The mathematical extension passes independent review under the stated sampling,
truth, and transport premises. The new identification statement is a sharp lower
bound on the full-cohort true-W/A/M fraction from gate marginals. Its projection
through the previous classification bounds is a conservative outer procedure.
This review does not establish native control transfer or biological validity.

For `T=P(true W/A/M)`, `a=P(G+|eligible)`, and
`f=P(G+|Other)`, the gate mixture is `g=aT+f(1-T)`.
If `a<=1`, `f<=F<1`, and `g>=gL`, then
`gL<=F+(1-F)T`, giving `T>=max(0,(gL-F)/(1-F))`.
If `F=1`, no positive lower bound follows. No lower sensitivity bound is
required; a lower sensitivity bound would generally help upper-bound T instead.

For `gL>F`, taking `T=(gL-F)/(1-F)`, `a=1`, and `f=F`
attains equality. If `gL=1>F`, this gives `T=1`; the unused Other
conditional kernel can still be assigned the value F. If `gL<=F`, a closed
model witness is `T=0`, `f=gL`, and arbitrary a. A target conditional on
eligibility needs `T>0`, so zero is then an infimum: choose any positive
`T=epsilon` and `a=f=gL`. Conditional probabilities at an unoccupied class
are arbitrary stochastic kernels rather than empirically defined quantities.

On a simultaneous confidence event, `g>=Lg`,
`f_native<=f_control<=Uf`, `o_i<=Uo_i`, and
`d_native_i>=d_control_i>=Ld_i`. Thus
`T>=beta=max(0,(Lg-Uf)/(1-Uf))` when `Uf<1`, and
`p_i<=min(1,Uo_i/(beta*Ld_i))` when its denominator is positive.
Here p is conditional on true full-cohort eligibility. If beta or Ld_i is
zero, the corresponding cap is one. Endpoint monotonicity has the required
directions: beta increases with Lg and decreases with Uf.

There are `16*C` one-sided components: each of two arms contributes three
observed-label upper endpoints, three correct-call lower endpoints, one native
gate-positive lower endpoint, and one known-Other false-gate upper endpoint.
Assigning error `alpha/(16*C)` gives simultaneous coverage at least
`1-alpha` by the union bound. Dependence between gate and label measurements
on the same units does not alter this argument. Valid fixed-denominator
binomial marginals and the one-sided native/control transport statements remain
external premises. The finite-count audit separately checks the preserved CP
engine against direct exact binomial sums.

The cap projection can discard joint restrictions. For example, define G+ to
mean the observed label W. Let observed W/A/M/U probabilities be
`(1/2,1/4,1/4,0)`, all three eligible correct-call lower bounds equal one,
and Other false-gate probability be zero. The gate bound is beta `1/2` and
the relaxed caps are `(1,1/2,1/2)`, admitting
`p=(1/10,9/20,9/20)`. But the full coupled model requires
`oW=T*pW=1/2`, hence T=5, which is impossible. A cap witness therefore
must not be called a full joint gate/classifier or count-confidence witness.

Two further counterexamples protect the denominator and calibration claims.
First, `T=1/10,a=1,f=0` gives gate rate `1/10` and positive predictive
value one. With `o=(1/5,1/5,1/5,2/5)` and diagonal lower bounds all
`3/5`, the latent conditional law `(4/5,1/10,1/10)` is feasible with
Other entrants. Substituting PPV=1 for beta falsely forces the uniform latent
law. Second, for `T=1/2,a=1,f=1/2`, one native gate trial and one
independent known-Other trial yield `(positive,negative)` with probability
`3/8`. The empirical plug-in beta then equals one, exceeding T. With
alpha `1/20` and one context, conservative CP endpoints instead give beta
zero. Zero observed control false positives never justifies a population upper
bound of zero; zero control trials require upper bound one.

The exact-rational gate oracle imports no producer implementation and passed:

- 87,178 necessity cases and 625 sharp gate endpoint witnesses.
- 975 positive-T approaching witnesses for zero beta.
- 8,281 conservative endpoint monotonicity cases.
- 28,000 label-completion cases and 10,520 unrestricted joint completions.

The finite-count audit passed 182 endpoint tail checks, 1,066 one-sided
coverage checks, and 492 perfectly dependent gate/label cases. These finite
checks support the implementations; the proofs above establish the general
claims. The previous classification engine supplies the unchanged capped
simplex Q/J formulas and their already reviewed boundary conventions.

The frozen producer comparison also passed: 625 gate-marginal cases, 2,916
eligibility-cap cases, all 64 one-sided endpoints across the count fixtures,
and exact reproduction of all three stored fixture results. Its source SHA-256
is `5c5645e83b3f38ecfb8e196bb5332a555ef752ffab42d4315b6ce7ebbf5d2f6f`.
The calibrated synthetic example rejects a common J; the same example with no
Other controls gives beta zero and does not reject. The saved comparison receipt
records fixture hashes and the precise scope of the scalar CP reuse.

All scripts and receipts in this review were prepared outside the repository;
the review does not alter repository source files.
