# Finite design diagnostics for conditional shared curvature

Original design analysis · 5 November 2026 · AI-assisted internal computational review

An exact conditional test can discard every contrast-bearing outcome, or retain a fiber too discrete to reject. This companion to the [conditional curvature engines](../conditional_curvature/README.md) makes those limitations computable before selecting a study allocation. It supplies a support criterion, a conditional information calculation, and complete finite operating probabilities for a small declared design. The mathematics is standard finite exponential-family conditioning, multinomial information, and constrained allocation. No new theorem, biological result, optimal test, or recommended scientific sample size is claimed.

The observation contract remains independent baseline and selected multinomials in each context, independent across contexts, with positive shared within-context offsets:

```text
K_c ~ Mult(B_c,q_c),  X_c ~ Mult(N_c,p_c),
p_ci proportional to q_ci exp(theta_c 1[i=A] + eta_c s_i), s=(1,0,-1).
```

The existing test conditions on selected totals N, selected W–M differences D, pooled route counts T=K+X, and total selected A. Under shared theta its weights are products of binomial coefficients. This diagnostic uses exactly the existing inclusive probability-ordering rejection rule. It changes no forecast, comparator, registry field, biological eligibility gate, stopping rule, released method, or error allocation. The contract does not establish biological transfer through unknown differential recovery or authenticate independence of descendant observations.

## What can vary after conditioning

For an observed selected vector X=(W,A,M) and baseline K, any other local allocation on the same conditioned support has

```text
X' = X + (-k,2k,-k),   K' = K + (k,-2k,k),
-L <= k <= U,
L = min(K_W,K_M,floor(X_A/2)),
U = min(X_W,X_M,floor(K_A/2)).
```

Across contexts, total selected A imposes `sum k_c=0`. Thus one context needs room to increase selected A, and another needs room to decrease it. There is more than one global allocation **if and only if** `U_c>0` and `L_d>0` for distinct contexts c,d. Merely having a large total count or one locally flexible context is insufficient.

Equivalently set `z_c=k_c+L_c`, `m_c=L_c+U_c`, and `S=sum L_c`. The fiber is the integer box slice `0<=z_c<=m_c`, `sum z_c=S`. Its size is the coefficient of `t^S` in `product_c(1+t+...+t^m_c)`. The code computes that coefficient by bounded integer convolution, without enumerating every Cartesian allocation.

Let r count contexts with `m_c>0`. When `r>=2` and `0<S<sum m_c`, the affine dimension of this integer fiber is r−1. To see why, for any pair of active coordinates the slice contains two points differing by their unit exchange: the other capacities can fill the remaining sum because `1<=S<=sum m_c−1`. Those exchanges span the sum-zero subspace. Under a law positive on the entire fiber, `Cov(A|F)` therefore has rank r−1. In the remaining singleton cases its rank is zero. For a declared contrast direction h, `Var(h·A|F)>0` exactly when h varies among the active contexts of a non-singleton fiber. Heterogeneity involving only fixed coordinates is invisible on that fiber. These claims concern the conditioned experiment, not full-model identifiability or causal identification.

A useful prospective consequence follows under strictly positive q and p: there is positive probability of a non-singleton fiber **if and only if at least two contexts each have B_c>=2 and N_c>=2**. Both arms must supply the two-unit exchange. Sufficiency follows by constructing opposite exchanges in two eligible contexts; positivity makes that count configuration have positive probability. For a direction h, those eligible contexts must also include differing h values for any positive conditional information to be possible. If there are r eligible contexts, the expected conditional covariance has rank `max(r-1,0)`: every pair of eligible contexts has a positive-probability exchange fiber. This is an information requirement, not a sufficient condition for rejection at a chosen alpha or for useful power.

## Conditional information and a cheap allocation screen

For two contexts, write `delta=theta_2-theta_1`. Given the fiber F, the alternative law is proportional to the null weights times `exp(delta A_2)`. Its Fisher information at delta=0 is exactly `Var_0(A_2|F)`. The program also averages this conditional variance over the declared null distribution of F. This expected information is a property of the conditioned experiment, not an achieved power percentage.

The known-offset test conditions on `F0=(N,D,A_total)`; the baseline-conditioned test additionally observes and conditions on T, giving F1. On the augmented independent-baseline experiment, the law of total variance gives

```text
E Var(A_2|F0) = E Var(A_2|F1)
               + E Var(E[A_2|F1] | F0).
```

Thus additional pooled-count conditioning cannot increase this expected null information. This does **not** impose a uniform power ordering on the two specific finite probability-ordering tests: their discrete rejection regions differ, as the example below shows.

There is also a simple full-model planning calculation. Define

```text
g(r)=log r_A - (log r_W + log r_M)/2,
theta_c=g(p_c)-g(q_c),
V(r)=1/r_A + 1/(4r_W) + 1/(4r_M).
```

For positive interior probabilities and B,N>0, the reciprocal full-model efficient Fisher information for theta, after the unknown q and tilt nuisance parameters, is exactly `V(p)/N+V(q)/B`. The same expression is the first-order asymptotic variance of the empirical contrast estimator. The multinomial covariance formula gives it directly: the log-contrast coefficients sum to zero, so the common negative covariance term cancels. Empirical log contrasts can be undefined at observed zeros; no pseudocount estimate is used by the exact test.

At a fixed equal-cost per-context budget B+N, minimizing that expression gives `B/N=sqrt(V(q)/V(p))`. At p=q the continuous optimum is equal allocation. With per-unit costs c_B,c_N and fixed monetary budget, the ratio is `sqrt(V(q)c_N/(V(p)c_B))`. These are local information allocations for stipulated probabilities and costs, not exact finite-test power optima. Sparse routes inflate V; a numerical allocation cannot be supplied without plausible positive laws, costs, and a scientific target.

Across contexts let `I_c=[V(p_c)/N_c+V(q_c)/B_c]^-1`. For a heterogeneity direction h and unknown common theta, the full-model efficient information is `sum I_c(h_c-hbar_I)^2`, with the I-weighted mean hbar_I. At a shared-theta null it bounds the expected conditional information from above: a conditional score removes the conditional expectation given the nuisance sufficient statistics, while a full efficient score removes their best linear projection. Removing all functions of those statistics cannot leave more squared residual. For two uniform contexts with B=N=4 this ceiling for delta is `2/9`, whereas the exact conditional information is approximately `0.0541778`. The finite information identities are exact; using information to approximate power or confidence widths requires additional asymptotic justification.

## Complete finite allocation example

The example fixes two contexts and **eight observations per context across both arms**, before outcomes. Every integer split B+N=8 is included. Both baseline laws and context 1 selected law are uniform. Tilts are zero. Context 2 has

```text
exp(theta_2) = tau in {1,3/2,4},
p_2 = (1,tau,1)/(2+tau).
```

The illustrative standalone alpha is 1/20. Tau=1 is the null; the other two are explicit synthetic heterogeneity alternatives. In particular tau=4 means selected context 2 probabilities `(1/6,2/3,1/6)`, not a measured biological effect. The existing contrast `J_c=p_cA^2 q_cW q_cM/(p_cW p_cM q_cA^2)` obeys `J_2/J_1=tau^2`, so tau=4 is a sixteenfold J ratio. Information reported for delta would be divided by four if parameterized by `log(J_2/J_1)=2 delta`. All route probabilities are positive. The computation enumerates 222,651 complete joint tables across the nine splits, each evaluated under all three laws with integer multinomial numerators and exact rational denominators. No Monte Carlo draws, normal approximation, p-value tolerance, or estimated-q substitution are used.

Here “attainable fiber probability” is the probability, under the stated alternative, of landing on a fiber containing **some** allocation with null p<=alpha. It upper-bounds unconditional power, but is not itself power. Conditional minimum attainable p describes one realized fiber; it does not say how likely that fiber is under a design. “Power” in this table means only the exact unconditional rejection probability under the declared synthetic joint law. None of these quantities is biological power.

| B | N | Null rejection | Power, tau=3/2 | Power, tau=4 | Attainable fiber probability, tau=4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 0.00000% | 0.00000% | 0.00000% | 0.00000% |
| 1 | 7 | 0.00000% | 0.00000% | 0.00000% | 0.00000% |
| 2 | 6 | 0.00916% | 0.01747% | 0.12738% | 0.54832% |
| 3 | 5 | 0.05492% | 0.07385% | 0.26154% | 2.33487% |
| 4 | 4 | 0.11770% | 0.15249% | 0.41867% | 4.66926% |
| 5 | 3 | 0.05492% | 0.07401% | 0.20820% | 3.52553% |
| 6 | 2 | 0.00916% | 0.01094% | 0.01947% | 0.82511% |
| 7 | 1 | 0.00000% | 0.00000% | 0.00000% | 0.00000% |
| 8 | 0 | 0.00000% | 0.00000% | 0.00000% | 0.00000% |

The balanced split maximizes power among these nine splits for these two alternatives and this rule. That finite result does not establish a generally optimal allocation. Even for the larger specified difference, balanced-split power is only `240301/57395628`, approximately 0.419%. The probability of a rejecting-capable fiber is `2679949/57395628`, approximately 4.67%; approximately 83.86% of outcomes have singleton fibers. At the null, reversing B and N leaves all these diagnostics unchanged because both arms have the same generating law and their exchange maps each conditioned fiber bijectively. With unequal arm laws, swapping just the counts has no such symmetry; the table exhibits the resulting power asymmetry.

At B=N=4, expected null conditional information is approximately `0.054177793`, versus `0.317547079` for known q at the same selected N: about 17.06% retained. The known-q comparison assumes exactly known offsets and ignores baseline counts. It is an information benchmark, not an equally costed available procedure when q is unknown.

The finite significance behavior is subtler. At N=4 the known-q probability-ordering test cannot reject at 5% on any fiber, whereas the baseline-conditioned procedure sometimes can. A concrete witness has

```text
X_1=(2,0,2), X_2=(0,4,0),
K_1=(0,4,0), K_2=(2,0,2).
```

For known uniform q the three allocations have weights proportional to `(1,24,1)`, giving observed p=1/13. Conditioning on both pooled vectors `(2,4,2)` changes the weights to `(1,576,1)`, giving p=1/289. The lower-information experiment can therefore produce a rejection that this particular known-q test does not. This reflects different discrete probability-ordering regions, not a gain in information from unknown q or general power dominance. A known-q analyst could also choose to use the independent baselines and the latter valid test; the comparison here holds the two existing test definitions fixed.

## Implementation and review

`design_diagnostics.py` exposes an observed-table geometry function and a deliberately narrow exact design calculator: two contexts, uniform baselines, zero tilts, theta_1=0, and a short list of positive rational exp(theta_2) values including the null. It does not accept arbitrary biological designs or authenticate observation assumptions. Geometry supports up to eight contexts and the existing 200-per-arm/800-total limits. Exact design enumeration accepts at most twelve observations per context across arms and one million complete joint tables; its retained dictionaries can still be large. Tau rational numerators/denominators are limited to 32 bits, and alpha to 256 bits. These are refusal limits, not scientific choices or comprehensive memory/runtime guarantees. Exceeding a bound leaves the calculation uncomputed; no approximation is substituted.

From an existing TMD checkout, write outputs to a scratch directory:

```sh
python -B research/conditional_design/design_diagnostics.py \
  --budget 8 --output /tmp/tmd-conditional-design.json
python -B research/conditional_design/verify_design_diagnostics.py \
  --repo . --output /tmp/tmd-conditional-design-verification.json
```

For an observed-table geometry check, use `--geometry input.json`, where the JSON has exactly `baseline` and `selected` arrays of W,A,M count rows in the same context order. Duplicate keys, nonstandard JSON constants, booleans, negative counts, and exceeded geometry bounds are rejected. The output rank assumes positive probability on the whole enumerated fiber. Geometry alone returns neither a p-value nor evidence that an observation law is valid.

`DESIGN_BUDGET_8.json` retains every exact fraction and descriptive decimal. `VERIFICATION.json` records 33,972 producer assertions, including exhaustive comparisons with the unchanged baseline engine for B=N=2 and B=N=3, complete comparisons with the known-offset engine for N=0..8, null arm-swap symmetry, malformed inputs, the discreteness witness, and unchanged source/registry hashes. The [independent review](INDEPENDENT_REVIEW.md) separately reconstructs all nine split results from binomial conditional weights and raw multinomial masses, and checks higher-context support geometry and affine ranks. This is AI-assisted internal computational review, not external peer review, biological replication, or registration.

The useful next step is to supply scientifically justified observation laws, contrast directions, realistic positive probabilities, costs and error allocation before computing a study-specific design. A nontrivial support or an information allocation by itself cannot resolve those missing inputs. Existing prospective registry fields and native evidence gates remain unchanged. A separate [bounded native-organism source screen](SOURCE_SCREEN.md) identifies strain-identity and compensatory-background leads while retaining its abstract-only limits.

Original code is MIT and original documentation CC BY 4.0 under the repository terms. No third-party source-author code is copied or executed.
