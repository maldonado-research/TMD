# Absolute capture: what a calibrated count law can identify

Mutation by Natural Dominance · R000013 · 7 October 2026, America/Los_Angeles

This conditional methods package follows the [paired-aliquot observation check](../paired_aliquot/README.md). It states what **absolute capture calibration** could add, and what it cannot add. The calculations use original finite synthetic examples and established binomial marking and compound-Poisson identities. No biological observations, calibration measurements or mutation rates were fitted. No actual-study registry field is resolved.

## The useful boundary

Let precursor events have Poisson intensity m in a defined sampling frame. Each event contributes an independent terminal mark J with law pi. J counts eligible terminal observation units, not necessarily cells or mutation births. Each such unit is independently captured with the same known probability c, with 0<c<=1. Under a declared finite bound 1<=J<=B, the positive detected jump intensities are

    nu_l = sum_{j=l}^B w_j binom(j,l)c^l(1-c)^(j-l),  w_j=m*pi_j.

Knowing c, B and the **complete population positive jump-intensity vector** gives a triangular inverse:

    w_B = nu_B/c^B,
    w_j = nu_j/c^j - sum_{k=j+1}^B binom(k,j)(1-c)^(k-j)w_k.

For a compatible nonnegative vector, m=sum_j w_j. The positive mark law is pi_j=w_j/m when m>0. At m=0 all weights are zero and pi is undefined. B limits one event's terminal mark size; total observed compound-Poisson counts remain unbounded when m>0.

This is an ideal conditional identification result, **not an estimator from a finite culture histogram**. A known population count law uniquely determines its positive compound-Poisson jump intensities within this finite family, but finite observations do not directly provide those exact coefficients. No procedure here estimates them, assesses goodness of fit, obtains statistical intervals or determines a sample size. An exact negative inverse coefficient rules out the declared exact population family at that c and B. A negative coefficient estimated from noisy observations alone does not biologically disprove a mechanism.

## Two complete-law ambiguities

- **Unknown capture:** singleton marks with (m,c)=(1,1/2) and (2,1/4) both give nu_1=1/2, hence the same complete observed Poisson law. A conditional split-ratio check cannot supply the missing common absolute capture probability.
- **Invisible zero terminal marks:** at known c=1/3, J=2,m=1 and J in {0,2} with equal weights,m=2 have exactly the same complete positive jump vector. The inverse identifies positive terminal intensity m*(1-pi_0)=1; it cannot recover the additional zero-mark events. Lost or extinct lineages need measurements outside this terminal-count frame.

Calling the units cells does not authenticate them. A CFU can originate from a packet or clump of cells. The same formulas can apply to independently captured packets, but then J and c describe packets. Native/reporter transport, growth, ancestry, allele import, establishment, retention and molecular mutation exposure require separate evidence. Even a correctly identified positive terminal intensity is not automatically a per-division mutation rate.

## What a zero probability alone can bound

Write b=-log Pr(X=0)=sum_l nu_l. It is the intensity of detected nonempty event marks, **not** the mean observed count sum_l l*nu_l. For synthetic J=2,m=1,c=1/2, b=3/4 while the observed mean is1.

If 1<=J<=B and c is known, standard monotonicity gives the sharp bounds

    b/[1-(1-c)^B] <= m <= b/c.

Without a justified finite upper B, the valid generic bound is b<=m<=b/c. When c<1 and b>0, the generic lower endpoint need not be attained by a finite positive mark; increasingly large marks approach it. For finite B the displayed endpoints are attained by J=B and J=1. Intermediate values follow from mixtures of those endpoint laws. At c=1, m=b for every positive terminal mark law, though the zero probability alone does not determine pi. At b=0 and positive c, the positive-event intensity is zero.

Externally justified deterministic ranges b in [b_L,b_U] and c in [c_L,c_U], with c_L>0, give

    b_L/[1-(1-c_U)^B] <= m <= b_U/c_L.

The synthetic rectangle b in [1/2,3/4], c in [1/4,1/2], B=2 gives [2/3,3]. These are deterministic bounds, not observed confidence intervals. No logarithms of data, numerical exponentials, certified transcendental arithmetic or new error allocation are supplied. Unknown c with no strictly positive lower bound can leave m without a finite upper bound outside the implementation's chosen numerical cap.

## Exact reproduction and limits

The Python standard-library implementation accepts int or Fraction inputs, rejects floats and booleans, and declares J in0..8, B in1..8, m in0..20 and c in(0,1]. Each external rational has numerator/denominator at most32bits. Every inverse vector must explicitly include all keys1..B, including zero intensities. The positive inverse assumes pi_0=0, rejects negative reconstructed weights and rejects a recovered positive intensity above20. Internal exact arithmetic is unrestricted. Derived forward outputs can exceed the separate inverse's external32bit cap; arbitrary forward-to-inverse helper compositions are **not** promised. The benchmark grid stays within the accepted parser domain.

The point and rectangle bound functions return exact algebraic endpoints without clipping them to20; these endpoints can exceed the forward/inverse wrappers' declared intensity cap. Those numerical caps are computational limits, not biological priors. Inversion can be sensitive: the diagonal scale is c^(-B), and the closed-form inverse alternates signs. For c=1/4,B=8, the highest coefficient is multiplied by65,536. Exact arithmetic checks an identity; it does not remove calibration uncertainty, sampling error or statistical instability.

Write reproduction outputs outside the checkout:

```sh
cd research/capture_calibration
PYTHONDONTWRITEBYTECODE=1 python3 verify_benchmarks.py --output /tmp/tmd_capture_calibration_replay.json --check-against BENCHMARKS.json
sha256sum -c SHA256SUMS.txt
```

The producer checks include direct enumeration of all Bernoulli unit assignments, forward/inverse round trips, exact PGF-exponent identities, sharp bound endpoints, complete-law witnesses and invalid-input guards. All verification entry points refuse Python -O/-OO. Engine input and compatibility guards do not depend on assertions. Independent internal review is distinct from external peer review.

## What changes for TMD

Absolute recovery and the identity of sampled units deserve separate measurements before a biological interpretation of counts. Known capture can remove one algebraic ambiguity under a compatible positive-mark model. It cannot identify invisible events, supply native-route transfer controls, or turn nominal plating geometry or a passing technical split check into calibrated molecular capture. This package changes no shared-curvature forecast, trial denominator, confirmatory count law, confidence budget, study registry or stopping rule.

Read [DERIVATION_AND_LIMITATIONS.md](DERIVATION_AND_LIMITATIONS.md) for the conditional proof and retained competing explanations. Prepared by Ricardo Maldonado with AI assistance. Original code: MIT; original notes and synthetic summaries: CC BY4.0. No third-party raw files or private archive content are included. No new theorem, priority claim, new causal force or biological confirmation is proposed.
