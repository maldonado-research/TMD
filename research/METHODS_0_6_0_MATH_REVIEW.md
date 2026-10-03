# Frozen TMD 0.6.0 candidate: independent mathematical review

Review date: 2 October 2026 (America/Los_Angeles; execution date 3 October 2026 UTC). Candidate: `/workspace/tmd-publication/candidate_validation/TMD_methods_candidate_0_6_0_2026-10-01/`, source commit `465850ee33f746cf42f1b3d5075fba2ea57332ad`. This review concerns the immutable PR1 candidate; later R1/R2/R3 work is excluded. The candidate, credentials and external systems were not changed. No biological claim is made.

**Finding: no blocking mathematical error found within the stated model and accepted interval domain.** The transport derivation, conditional simultaneous-confidence argument, scalar interval projection and symmetric frontier agree with the implementation. This finding does not authenticate the data-generating laws or residual bounds.

## Equation and implementation checks

1. With route weights `v=(-1/2,1,-1/2)`, the observation normalizers cancel. If `e_i=(r_1i/r_0i)/(d_1i/d_0i)`, then `theta_corr=theta_bio+v dot log(e)` and `J_corr=J_bio e_A^2/(e_W e_M)`. The signs in METHODS.md lines 13–25 are correct. The probability-projection exponent groups in the historical implementation and the new adapter agree with this identity.
2. Over positive finite routewise residual boxes, `mlo=L_A^2/(U_W U_M)` and `mhi=U_A^2/(L_W L_M)` are attained corner extrema. The biological interval is `[Jlo/mhi,Jhi/mlo]`; `multiplier_bounds` and `widen_interval` implement that division correctly. Asymmetric boxes need not enlarge the original interval, as the documentation acknowledges.
3. There are `12C` marginal probabilities and `24C` one-sided bounds, each allocated `alpha/(24C)`. Valid marginal binomial laws give simultaneous coverage at least `1-alpha` by the union bound without across-coordinate independence. On that coverage event, valid fixed residual bounds transfer enclosure to all biological contrasts. A common positive finite biological J must then lie in every interval; strict disjointness gives false-rejection probability at most alpha. Touching finite intervals do not reject.
4. For independently varying context residual vectors with each differential residual in `[1/R,R]`, multiplier extrema are `[R^-4,R^4]`. Compatibility is exactly `L <= U R^8`; the real-valued first-compatible frontier is `(L/U)^(1/8)` when initially rejecting. Rejection ensures `0<U<L<infinity` under the accepted interval contract. Separately bounding each branch ratio gives an exponent of 16. A single common residual vector adds a shared bias and preserves cross-context equality.
5. The implementation uses rational powers and comparisons for correction, intersection and frontier certificates. Zero lower bounds and positive-infinite upper bounds are retained as finite-log-contrast limits. The accepted domain excludes intervals whose only possible common value is zero or infinity. One-context results are descriptive.
6. The mismatch construction has uniform latent biological probabilities and legitimate positive recovery probabilities. Its two observable corrected J values are 16 and 1/16 while both biological J values are 1. Its chosen multinomial and control count tables are possible outcomes. Restoration of compatibility at R=2 is an illustrative arithmetic fact, not a frequency or biological estimate.

## Independent validation performed in this review

All probes used Python `-B`, exact Fraction arithmetic and in-memory imports; none changed candidate files.

- 1,000 normalized positive-population transport identities, calculated directly from q, p, actual recovery and control recovery.
- 1,000 positive rational residual boxes, compared with all eight route corners.
- 1,000 asymmetric scalar interval projections, compared with endpoint/corner enumeration.
- 1,260 independent exact binomial-tail sums, covering every k for n=1..12, seven dyadic population probabilities and both tails.
- 210 exact small-sample population coverage checks for n=1..10 at 21 rational probabilities, using per-tail error 1/100.
- A separate subreview checked 18 symmetric frontier certificates, including near-one and large ratios, non-dyadic rational roots, zero/infinite endpoints and exact touching behavior.

All passed. The parent's 44-unit-test and 160-record replay runs are separate evidence and were not repeated here. These finite checks support the implementation; the algebra and confidence-event argument supply the general justification.

## Publication wording and limits

The candidate already states the essential qualifications in METHODS.md lines 45–57 and 76–90, README.md, and the suggested abstract: supplied scalar intervals crossed with residual boxes are projected exactly, but the resulting set is conservative relative to simplex or joint mechanistic constraints; restored interval overlap need not establish a fully feasible biological model; bounds are hypothetical sensitivity inputs; nonrejection is not equivalence; all reused results are synthetic; and novelty and external peer-review claims are excluded.

Preserve those qualifications. In particular, this is not a globally sharp confidence set, an estimate of true mismatch, a biological tipping point, or general power. The new adapter verifies saved projection arithmetic and allocation metadata; it does not reauthenticate all old binomial certificates or sampling laws. If residual bounds are estimated with simultaneous failure probability gamma, total noncoverage can be bounded by alpha+gamma; that uncertainty must be budgeted.

**Optional, nonblocking wording clarification:** METHODS.md line 76 can call `R*` the *real-valued frontier*. An irrational eighth root is enclosed by rational API outputs; over accepted rational radii, compatibility has an infimum rather than an attained minimum. The current analytic formula and bracket claims are correct when R is understood as real.
