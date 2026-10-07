# Paired aliquots: a falsifiable observation check

Mutation by Natural Dominance · R000010 · 7 October 2026, America/Los_Angeles

This package checks how two samples from the **same culture** differ from independent cultures or two observations capable of counting the same cell twice. It provides a prospective measurement-quality check and exact finite synthetic examples. No paired biological observations were acquired or fitted. It does not resolve the 26 actual-study fields, measure mutation supply, prove a clone-growth law, or confirm TMD.

## Observation and competing explanations

Let R be a culture's terminal number of true qualifying descendants, with probability-generating function H. Each descendant is independently assigned to sample1, sample2 or neither with probabilities p1,p2,1-p1-p2. The samples are physically disjoint, p1+p2≤1, and the probabilities include the justified observation process rather than nominal volumes alone. Then

    G(z1,z2) = H(1-p1-p2+p1 z1+p2 z2).

Put P=p1+p2 and S=X1+X2. For P>0 and any sum s with positive probability,

    S has PGF H(1-P+Pz),
    X1 | S=s ~ Binomial(s, p1/P).

These standard marking identities hold for **any** terminal history H. Clone histories, standing variation, imported alleles, growth and common unmeasured loss can all pass the conditional split check. Passing therefore cannot authenticate mutation origin, Poisson events, total capture, equal growth, native/reporter transfer or a new mechanism. In particular p1=c f1,p2=c f2 leaves p1/P=f1/(f1+f2) unchanged for unknown common recovery c. Calibration of the allocation ratio alone does not identify c.

A meaningful test fixes the eligible sampling units, disjoint frame and allocation ratio independently of the selected outcomes, retains every sampled culture and its full outcome ledger, and investigates a failure rather than assigning a causal explanation. Two agar plates can share a culture even when cell assignments to them are disjoint. Correlated descendants, technical plates and genotype confirmations are not additional independently founded cultures. Uniform assignment of CFU packets might pass the same split check while one CFU still contains several cells.

## Three frames with identical marginals

For a conditional compound-Poisson history, write R as the sum of B iid finite clone sizes K, with B~Poisson(m). The precursor events and clone marks are independent under this model. m is an event-intensity parameter for the defined observation frame, not an authenticated per-division mutation rate. Here g is the clone PGF and

    H(u) = exp[m(g(u)-1)].

The disjoint joint law is exp[m(g(1-p1-p2+p1z1+p2z2)-1)]. If both arms instead independently recapture the same descendants, the argument becomes (1-p1+p1z1)(1-p2+p2z2). For separate independently founded cultures with independently controlled histories, the two marginal PGFs multiply. Merely placing cultures in separate vessels does not establish independence when founders, occasions or latent parameters are shared.

With synthetic K=2,m=1,p1=p2=1/4, all three frames have marginal means1/2, variances5/8 and negative-log marginal zero probabilities7/16. Their paired quantities differ:

| Sampling frame | -log Pr(X1=X2=0) | Cov(X1,X2) |
| --- | ---: | ---: |
| Disjoint aliquots, same history | 3/4 | 1/8 |
| Independent overlapping recapture, same history | 175/256 | 1/4 |
| Independent culture histories | 7/8 | 0 |

Thus marginal agreement cannot authenticate the joint sampling frame. For synthetic singleton clones K=1,m=1 with p1=p2=1/4, the disjoint law has Pr(X1=1|S=2)=1/2. The overlapping model instead gives25/34. This is a concrete observation-law discriminator in the stated toy model, not a mutation-mechanism discriminator.

## Conditioning changes covariance

When R has finite first and second moments,

    Cov(X1,X2) = p1 p2 [Var(R)-E(R)].

Conditioning on fixed R=N gives -N p1p2. Under the compound-Poisson law, the unconditional covariance is m p1p2 E[K(K-1)]≥0. At K=1, independent Poisson splitting gives zero unconditional covariance even though fixed-N sampling has negative covariance. Do not mix these conditioning frames or use covariance formulas for the ideal infinite-mean Luria–Delbrück clone law. Its first and second moments diverge; finite-moment covariance formulas are undefined. Valid PGFs or void probabilities are the relevant conditional tools instead.

Positive covariance is not evidence uniquely identifying clonal mutation. For example, R|Λ~Poisson(Λ), with Λ=0 with probability1/3 and Λ=3 with probability2/3, has E(R)=2 and Var(R)=4. It produces the same first two paired moments as fixed-intensity K=2,m=1. Culture-to-culture intensity heterogeneity is a meaningful competing explanation. Their full distributions can differ.

Likewise K=2,m=1 and K∈{1,3} with weights3/4,1/4,m=4/3 share means, variances and covariance, while joint negative-log zero probabilities are3/4 and19/24. Moments alone do not identify the latent event intensity.

Allowing zero terminal clones gives a stronger boundary. K=2,m=1 and K∈{0,2} with equal weights,m=2 have exactly the same **complete** observable PGF at every capture probability, because all positive jump intensities agree. Additional extinct/unrecovered zero marks are invisible. This explicit zero-mark ambiguity does not claim full-distribution ambiguity for every strictly positive clone family. Measurements outside the descendant-count frame are needed to count those lost precursor events.

## Implementation and reproduction

`paired_aliquot.py` constructs exact multinomial or overlapping-binomial clone marks and computes bivariate compound-Poisson coefficients relative to Pr(0,0) by an Euler-derivative recurrence. A separate finite exponential-series convolution checks that recurrence. Diagonal sums are checked against union thinning, and individual coefficients against the conditional-binomial split identity. These coefficients are exact rational values for finite synthetic laws; negative-log zero probabilities remain exact rational intensities. No numerical exponential, outward certificate, p-value, biological confidence interval or achieved-power claim is supplied.

The public `paired_model` domain is explicit: integer clone support0..8, normalized nonnegative exact weights, intensity0..20, exact capture probabilities0..1, total coefficient degree0..8. Integers and Fractions are accepted; floats and booleans are rejected. Each external rational has numerator/denominator at most32bits. Within `paired_model`, derived joint weights and coefficient intermediates retain exact arbitrary-precision arithmetic without reapplying that input-size cap. Separately calling the public `pgf` helper with an externally composed argument can exceed its32bit input cap; arbitrary helper compositions are not guaranteed to execute. The returned triangular coefficient table is **truncated by total degree** and must not be normalized or described as a complete probability distribution. A marginal cannot be recovered by summing an incomplete triangle. Absolute probabilities multiply the listed ratios by exp(-the appropriate joint zero intensity).

Run with Python3.12 and the standard library, writing outside the checkout:

The verification entry points refuse optimized Python (`-O`/`-OO`), which would disable assertion-based checks. Ordinary reproduction and the stored exact results remain unchanged.

```sh
cd research/paired_aliquot
PYTHONDONTWRITEBYTECODE=1 python3 verify_benchmarks.py --output /tmp/tmd_paired_aliquot_replay.json --check-against BENCHMARKS.json
sha256sum -c SHA256SUMS.txt
```

The producer benchmark counts are60 normalization checks,360 exact clone-PGF identities,5040 recurrence/convolution coefficient comparisons,630 union-thinning comparisons,2100 conditional-split comparisons and18 invalid-input guards. Source/methods review and a separately implemented mathematical oracle are recorded in `review/`. These are computational checks, not biological replications or external peer review.

## What this changes for TMD

Before evaluating a held-out Wsp/Aws/Mws forecast, a justified aliquot law can provide a measurement-quality gate and prevent plate counts from being promoted into independent founders. A passing technical allocation gate does not supply any missing biological study input. Selection, clone fitness, correlated recovery, classification errors, cell clumping, post-plating events and ancestry or transfer remain distinct explanations. The shared-curvature forecast, actual registry, original error allocations, stopping rules and immutable archives remain unchanged.

The SBW25 source audit reconstructs nominal geometry but does not authenticate the effective p values or random confirmation frame. Its 24 source rows are not paired observations for this new benchmark. The prepared author-input request remains unsent; no new rate fit is justified. Read the separate R9 source-input audit and R7 fluctuation contract before interpreting these formulas biologically.

This is original conditional methods work derived using established PGF, multinomial marking and compound-Poisson identities, with the classical fluctuation framework discussed in the existing R7/Foster2006 assessment. No new theorem, priority claim or new biological force is proposed. Original notes and derived synthetic summaries: CC BY4.0; original code: MIT; prepared by Ricardo Maldonado with AI assistance. Private archive and raw third-party files are excluded.
