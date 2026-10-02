# Independent mathematical review: recovery-transport sensitivity

**Review date:** 1 October 2026 (America/Los_Angeles). **Scope:** the extension of the public TMD 0.5.0 confidence projection, with comparison to public 0.3.0 transport sensitivity. This is an internal independent derivation and review, not external peer review or new biological evidence. No private research files were used.

**Finding:** the proposed signs, routewise multiplier bounds, biological interval transformation and common-factor eighth-power threshold are correct under the contracts below. The extension combines an existing transport-sensitivity argument with the 0.5.0 finite-sample confidence construction. It should not be described as a new statistical principle. The main implementation requirements concern honest transport declarations, exact boundary comparisons and the meaning of “sharp.”

## 1. Target and algebra

Suppress context subscripts temporarily. Let positive biological baseline and selected probabilities be q and p, and let their biological recovery probabilities be r_0 and r_1. Observed categorical probabilities obey b proportional to q*r_0 and t proportional to p*r_1. Let d_0 and d_1 denote the control recovery probabilities measured by fixed-route binomial controls. All products and ratios in this paragraph are routewise. Recovery probabilities can equal one, but the population components used in logarithms must be strictly positive.

For route order W,A,M and v=(-1/2,1,-1/2), define

    theta_bio = v · (log p - log q)
    theta_corr = v · (log t - log b - log d_1 + log d_0)
    e_i = (r_1i/r_0i)/(d_1i/d_0i).

The normalization constants cancel because sum(v)=0. Therefore

    theta_corr = theta_bio + v · log e
    J_corr = exp(2 theta_corr)
           = J_bio * e_A^2/(e_W*e_M).

The relation does not require exact control-to-biology transport. Exact transport of differential route recovery is the special case in which the residual contrast is zero. The stronger condition e_W=e_A=e_M is sufficient, but is not necessary: e_A^2=e_W*e_M also makes the residual contrast zero. Neither cancellation nor a small sensitivity interval identifies a mutation mechanism.

The public root MATHEMATICAL_EXTENSION.md derives the positive-probability baseline-adjusted contrast and its converse. Under its exponential-tilt parameterization, v also cancels the nuisance route score s=(1,0,-1), leaving the proposed biological selection contrast. Without that biological parameterization, theta_bio remains a well-defined phenomenological contrast.

## 2. Sign-aware bounds and their exact scope

Require finite positive bounds 0<L_i<=U_i<infinity. If e_i lies in [L_i,U_i], the multiplier m(e)=e_A^2/(e_W*e_M) has extrema

    M_lo = L_A^2/(U_W*U_M)
    M_hi = U_A^2/(L_W*L_M).

The lower corner uses the lower A endpoint and upper W/M endpoints; the upper corner reverses these choices. Thus an enclosing corrected interval [a,b] gives

    J_bio ∈ [a/M_hi, b/M_lo].

Both multipliers are positive finite rationals when their inputs are positive finite rationals. Rational division therefore preserves the exact decision arithmetic inherited from 0.5.0. Zero a and an infinite b are permissible limit endpoints: 0/M_hi=0 and infinity/M_lo=infinity. They represent infinite log-contrast bounds, not observed or identified structural zeros.

These multiplier bounds are sharp over the stated routewise box. In log coordinates the image is an interval because a linear functional maps a convex box onto an interval; its extrema are attained at the stated corners. Consequently the biological interval is the exact range over the product of the supplied scalar corrected interval and that box, with zero/infinite limits interpreted as closures.

That does **not** make it a sharp confidence set for the original probability model. The 0.5.0 corrected interval already ignores categorical simplex restrictions, and its certified probability endpoints can be wider than the ideal Clopper–Pearson roots. Separate context boxes can also ignore cross-context physical restrictions. These simplifications preserve enclosure but can admit biological contrasts with no jointly feasible probability vectors under additional constraints. Use “exact projection of the supplied intervals and boxes” or “conservative simultaneous biological bounds.”

If an asymmetric box excludes e=(1,1,1), its transformed interval can shift or narrow relative to the zero-mismatch interval. Only nested uncertainty sets guarantee nested output intervals. “Widening” is appropriate for symmetric boxes with R>=1, or for boxes explicitly containing the earlier uncertainty set.

## 3. Coverage and shared-contrast testing

Let E be the 0.5.0 event on which all 12C scalar population probabilities fall inside their certified marginal intervals. Its proof gives P(E)>=1-alpha for a fixed collection of contexts and valid marginal count laws, using one-sided error alpha/(24C). Dependence between component confidence events does not defeat the union bound. Dependence or clustering that invalidates the individual binomial/multinomial laws remains a problem.

On E, all corrected population contrasts lie inside the corresponding [a_c,b_c], irrespective of whether controls exactly transport to biology. If the true residuals also belong to the prespecified transport boxes, the algebra above places every true biological contrast inside its transformed interval. No additional error allocation is required for a deterministic sensitivity box asserted to contain the true residuals. This is a guarantee uniform over the stated nuisance set, conditional on that scientific restriction; declarations do not authenticate the restriction.

If the biological contrasts are shared, their common positive finite J must lie in every transformed interval on E. It follows that rejection only when

    max_c(a_c/M_hi,c) > min_c(b_c/M_lo,c)

has false-rejection probability at most alpha under the shared biological null, the count laws, and the transport restrictions. Equality is touching overlap and must not reject. This is an intersection test of conservative confidence sets, not a likelihood-ratio test or a returned P value. Nonrejection is compatibility at the stated resolution, not proof of equality or equivalence.

The guarantee inherits the 0.5.0 requirements: fixed prespecified contexts, totals and analysis; valid sampling units and known control denominators; positive population log components; and correct handling of observed zeros and missing data. Optional stopping, selecting contexts after examining outcomes, unknown exposures, amplified descendants, misclassification and omitted routes are not repaired by transport sensitivity.

If transport bounds are themselves estimated with simultaneous noncoverage probability gamma, using them as deterministic truths loses that uncertainty. A direct joint-event argument instead gives at least 1-alpha-gamma coverage, absent a sharper justified joint construction; independence is unnecessary for this union bound. Unjustified boxes have no coverage guarantee. A sensitivity curve reports conclusions under proposed bounds and does not estimate which bounds hold biologically.

## 4. Symmetric factor and exact compatibility frontier

For the differential residual bound e_ci∈[1/R,R], with R>=1 common across routes and contexts,

    m(e_c) ∈ [R^-4,R^4]
    J_bio,c ∈ [a_c/R^4, b_c*R^4].

Writing A=max_c a_c and B=min_c b_c, intersection is nonempty exactly when

    A <= B*R^8.

For initially disjoint intervals, A>B, valid 0.5.0 interval outputs ensure 0<B<A<infinity. The first compatible factor is

    R_star = (A/B)^(1/8).

At R=R_star the intervals touch and the test does not reject. For initially compatible intervals the first permitted factor is R_star=1. If A=0 or B=infinity, compatibility already holds. There is no between-context frontier to interpret for C=1.

Use the exact rational Q=A/B to make decisions: compare the exact rational R^8 with Q. R_star is generally irrational; a displayed decimal root must not determine rejection. An exact rational bracket l,u certified by l^8<=Q<=u^8 can accompany the exact Q. A factor equal to the exact threshold must produce nonrejection, including rational perfect-eighth-power examples.

An independent exact example is [a_1,b_1]=[1,2] and [a_2,b_2]=[512,1024]. Then Q=256=2^8. At R=2 the transformed intervals are [1/16,32] and [32,16384], touching at J=32. Factors below two reject; factors above two do not. The frontier is a property of these conservative intervals and the stipulated boxes. It is not an estimate of actual transport mismatch, a biological tipping point, or a globally sharp bound under unmodeled constraints.

Two distinctions are essential:

- R bounds the **differential** residual e_ci, which already compares the two biological/control branches. If each branch ratio r_hci/d_hci separately lies in [1/R,R], then e_ci can range over [R^-2,R^2]. The multiplier range is then [R^-8,R^8], and the analogous common-factor comparison uses R^16. A branch-level tolerance must not be mislabeled as a differential tolerance.
- A common numeric R permits different residual vectors in different contexts. If the same residual vector is known to apply to every context, it contributes one common contrast bias; biological equality is then equivalent to corrected equality. Widening each context independently discards that information and is conservative. More general cross-context restrictions require joint projection for a sharper test.

## 5. Boundary and contract checks

The mathematically supported scalar domain is finite 0<=a<=b with b positive, or finite a>=0 with b=infinity. Genuine 0.5.0 CP outputs have finite lower J bounds and strictly positive upper J bounds. Decline an upper bound of zero, an infinite lower bound, negative bounds, reversed endpoints, NaN, or undocumented infinity sentinels. Such values cannot represent a confidence interval for the stated positive finite target in this workflow.

An interval [0,infinity] remains completely uninformative after any finite positive transport transformation. A one-sided interval can remain informative: [0,u] and [l,infinity] reject a common positive J when l>u after transformation. Observed zero counts therefore do not automatically make every comparison unevaluable. Structural population zero probabilities, by contrast, make the finite log target undefined and require another model. No probability floor or pseudocount should be introduced.

One context receives a descriptive sensitivity interval and an explicit no-between-context-test status. It must not be reported as a successful shared-contrast test. A confidence intersection restricted to a positive finite touching point is compatible. Limits at zero/infinity are not finite biological contrast values; the supported endpoint domain prevents a purported overlap consisting solely of one of those limits.

The inherited 0.5.0 validator requires metadata.control_relative_recovery_transports=true. A bounded-mismatch extension should not silently manufacture that assertion. It must explicitly distinguish the statistical confidence calculation for the observable corrected contrast from its biological interpretation under the newly declared bounded-transport assumption. A wrapper around saved 0.5.0 results should document this distinction, validate their provenance and input shape, and avoid presenting the original exact-transport metadata as evidence that transport was authenticated.

## 6. Verification and source lineage

An independent standard-library Fraction calculation checked 512 asymmetric boxes against all 4,096 routewise corners. Every multiplier minimum and maximum agreed with the formulas. Each box was also applied to three representative interval forms, including zero lower and infinite upper bounds. Four symmetric factors checked [R^-4,R^4] and the exact R=2 touching example. These finite checks support the algebra; the proof above supplies the general argument. Section 7 records the subsequent review of the frozen implementation.

Public sources inspected:

- TMD 0.5.0 README.md, methods/BOUNDARY_CONFIDENCE_PROJECTION.md, audit/FINAL_MATH_REVIEW.md, and the relevant portions of inference/boundary_confidence.py, from the public TMD_research_extension_0_5_0_2026-09-30.zip extraction.
- The public root MATHEMATICAL_EXTENSION.md, especially its baseline-adjusted invariant and mechanism-identifiability discussion.
- The public root TMD_RESEARCH_EXTENSION_0_3_0.md and design/TRANSPORTABILITY_AND_PRECISION.md inside TMD_research_extension_0_3_0_2026-09-30.zip. The latter already derives the residual transport bias, sharp box bounds, symmetric log sensitivity, separate-branch tolerance doubling, and shared-interval compatibility. Its sampling intervals are asymptotic and exclude observed zero cells.

The defensible advance is therefore a boundary-compatible, certified finite-sample implementation of an existing sensitivity construction for the 0.5.0 fixed-route binomial design, with exact rational compatibility decisions and a transparent sensitivity frontier. It adds neither authenticated biological observations nor identification of mutation, accessibility, fitness, establishment, or a causal mechanism. The categorical randomized-mixture controls of 0.3.0 and fixed-route binomial controls of 0.5.0 remain different observation designs.

## 7. Frozen implementation review and independent execution

**Outcome: pass for the stated scope; no remaining actionable defect identified.** This finding applies to the source hashes below. The independent reviewer did not edit the implementation or its tests.

The executable contract distinguishes the observable control-corrected parameter from its biological interpretation. It requires explicit bounded-mismatch declarations and reports that the old exact-transport assertion is not adopted. Those declarations are assumptions, not authenticated evidence. The adapter independently rechecks the arithmetic of saved marginal endpoints and their exact J projection; it does not claim to reauthenticate sampling laws or re-prove saved binomial-tail certificates. Its finite positive target domain, explicit positive-infinity encoding, asymmetric multiplier division and strict intersection comparison agree with the mathematical derivation. The common-factor bisection uses only rational eighth-power comparisons, and its reported bracket encloses the first compatible R with absolute width at most 2^-80 in the reanalysis.

One boundary regression was found during review: genuine 0.5.0 zero-total categorical intervals have status `no_observations`, whereas the initial adapter admitted only `certified`. This caused valid no-data inputs to be declined. The implementation now admits `no_observations` only for exact [0,1] bounds with absent or empty certificates. New full-API tests cover the valid case and reject a narrower interval carrying that status. Direct checks of all six original public boundary/descriptive fixtures passed after this correction.

The reproducible reviewer-owned oracle, `verify_transport_review.py`, uses a separate factorization: first bound each route ratio t_i*d_0i/(b_i*d_1i), then combine them as the A ratio squared divided by the W and M ratios. It independently verified:

- All 640 context projections in the 160 original public synthetic records.
- All 160 baseline decision statuses and all 800 saved sensitivity-grid decisions through both independent arithmetic and the full executable API.
- All 40 initially rejecting records' exact power ratios and certified first-compatible-factor brackets.
- All six original public boundary/descriptive fixtures at R=1 and R=2, for 12 full-API evaluations. At R=1 their original rejection/nonrejection/descriptive meanings are preserved; the new API explicitly labels the target as finite.
- Both constructed mismatch contexts, including normalized observation probabilities from actual recovery probabilities, the exact residual identities, and containment of the biological J=1 under R=2.

The constructed example has positive legitimate recovery probabilities: baseline recovery and both control branches equal 1/2 in every route; selected biological recovery is (1/4,1,1/4) in one context and (1,1/4,1) in the other. Both latent biological distributions are uniform. Consequently J_bio=1 in both contexts while the observable corrected J values are 16 and 1/16. The chosen count realization rejects at R=1 and is compatible at R=2. Its output explicitly marks the R=1 bound false for this constructed population and R=2 true, avoiding interpretation of the deliberately invalid R=1 premise as verified. This remains a deterministic counterexample, not a false-positive frequency estimate or new biological evidence.

The final 44-test suite passed, and `run_reanalysis.py --check` reproduced both output JSON files byte for byte. The independently reviewed reanalysis source was also compared directly with its member in the public 0.5.0 ZIP and found byte-identical. These results are based on the archived public bytes, not regenerated probability endpoints from a different platform. Under the grid, all 40 stored strong-departure examples still reject at R=5/4, and none reject at R=3/2; these are properties of the reused synthetic records under hypothetical bounds, not general power estimates.

Reviewed SHA256 values:

| Artifact | SHA256 |
| --- | --- |
| transport_robustness/transport_robustness.py | `8bc7149ab700cf2a74b6ba1859e340c8c3e40b6ff970f718a3d8da59dafb3464` |
| transport_robustness/run_reanalysis.py | `70b88a4576dd908aff4008007eeebe0b04fae48b5c1b3b7fdb4911c869c3b37a` |
| transport_robustness/test_transport_robustness.py | `628b3b89149487c3e2f7551948cac7f6d8a6e2d333e5d043ef938f0160879600` |
| transport_robustness/sources/calibration/repeated_sample_results.json | `509783c2a67bf70e590b3daca4b7f9706cf4c9a6b578a5e4e318e47939dd819f` |
| transport_robustness/results/reanalysis.json | `d1f75d53360021447867784ef8f4512ca9aaae98ab5f02d08911bfac3634e412` |
| transport_robustness/results/mismatch_counterexample.json | `693c86491e5f7c670597e1ec3ee647116de2d942aa579afef5f33539815f5e78` |
| verify_transport_review.py | `7545f7da18ca8131fb869b00e2c57d4b055c5f44a1e5f8ab3f790ec3c9bb2f65` |

`TRANSPORT_CODE_REVIEW_RECEIPT.json` records the checks and additional source hashes. To reproduce from the directory containing this review and the extension:

```sh
python3 -m unittest discover -s transport_robustness -p 'test_transport_robustness.py' -v
python3 transport_robustness/run_reanalysis.py --check
python3 verify_transport_review.py --public-archive /path/to/TMD_research_extension_0_5_0_2026-09-30.zip
```

The public-archive argument additionally enables byte-identity and all six original boundary-fixture checks. Without it, the oracle still verifies the exact expected calibration-source hash, all 160 records and the constructed counterexample. Hashes and successful arithmetic checks establish reproducibility of these artifacts; they do not establish the scientific assumptions required for biological interpretation.
