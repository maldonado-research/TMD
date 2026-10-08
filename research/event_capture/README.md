# Event capture after inheritance

Mutation by Natural Dominance · R000020 · 7 October 2026, America/Los_Angeles

One mutation birth can be inherited by several descendants. A count of detected copies is therefore a different quantity from the number of distinct births detected. This finite conditional package analyzes that event-level observation problem, including correlated recovery, known lost events and uncertain joint capture. It supplies exact synthetic identities and classical sampling calculations. No biological estimator, mutation rate, confidence interval or clinical result is fitted.

## The observation contract

Fix a finite catalogue E of distinct true events and a finite set of eligible terminal descendants. For event e, S_e is its **known** carrier set, supplied from external ancestry/genotype information. A descendant capture mask M records eligible, validated true genotype calls. In this model, a marked descendant supplies a correct call for every target event it carries. The event is included once when

    I_e(M)=1{M intersects S_e},  pi_e=Pr(I_e=1).

Thus several called descendants carrying the same event still contribute only one detected birth. Different true events can have the same carrier set and remain different catalogue elements.

This shared-mask model is an explicit all-target genotype-observability assumption. Cell isolation, cell survival and sequence-library production alone do not meet it. Real locus-specific false negatives, false positives or multi-subclone support requirements need a justified event-call observation law, often richer than one common descendant mask. A caller that requires two sequenced subclones is not automatically an “any successful descendant” OR rule. The supplied `ancestry_known=True` flag is an assumption, not authentication.

## Marginal recovery does not determine event inclusion

With only the validated-call marginals p_j for j in S_e, the sharp bounds are

    max_j p_j <= pi_e <= min(1,sum_j p_j).

For an empty known carrier set, both endpoints are zero. The familiar formula

    pi_e=1-product_j(1-p_j)

requires joint independence of eligible descendant calls. It cannot be inferred from stage percentages, similar growth times or equal marginal recovery.

For one event carried by two descendants, let both marginals be1/2:

| Synthetic joint capture | Positive mask probabilities | Event inclusion |
| --- | --- | ---: |
|Common success/failure|neither1/2, both1/2|1/2|
|Mutually exclusive calls|first1/2, second1/2|1|
|Independent calls|each of four masks1/4|3/4|

All three have the same expected number of observed inherited copies,1. Their distinct-event inclusion probabilities differ. With three descendants always called, one true event yields three observed copies but one detected birth. No rule turning arbitrary repeated variant calls into new births is justified.

## A fixed-event total and its uncertainty

When every pi_e is known and strictly positive, the classical Horvitz–Thompson quantity

    T(M)=sum_e I_e(M)/pi_e

has design expectation |E|. Let pi_ef=Pr(I_e=I_f=1), including pi_ee=pi_e. Its exact design variance is

    Var(T)=sum_e,f (pi_ef-pi_e*pi_f)/(pi_e*pi_f).

Joint inclusion matters. For two distinct singleton-carrier events with descendant marginals1/2, the common, mutually exclusive and independent capture laws above give total variances4,0 and2, respectively. Two distinct events carried by the same single descendant also have variance4 at capture1/2. Independence of descendant calls does not make events with shared carriers independent.

These are fixed-catalogue/design expectations, conditional on known carrier membership and a justified sampling law. The catalogue is supplied in these synthetic examples. The calculation does not identify an unobserved biological catalogue, reconstruct lost genotypes, infer a mutation process or establish a Poisson/binomial count law. No empirical variance estimator, confidence interval or precision guarantee is provided. A known event with zero inclusion can be analyzed for ascertainment, but the complete-catalogue HT total is refused. Restricting to observable events would change the target.

## Route-dependent event ascertainment

In a synthetic catalogue with one true event in each generic route, let the carrier-set sizes be1,2,1 and every descendant have independent validated-call probability1/2. Event inclusions are then1/2,3/4,1/2. Normalizing the expected detected-event counts gives shares2/7,3/7,2/7 and raw curvature9/4 despite equal fixed true event totals. This is an observation effect after inheritance; mutation generation has not changed. The result concerns normalized expected detected-event counts, not a complete route sampling law or a causal biological effect.

## Reproduction and limits

`event_capture.py` uses Python standard-library Fractions. The public domain is0..8 descendants and0..8 distinct event IDs; each carrier set is explicit, with no duplicates or unknown members. Capture laws have nonnegative normalized rational weights over integer masks0..2^n-1. Each external int/Fraction input is capped at32bits; booleans, floats, unknown ancestry, invalid laws and zero-pi total estimation are refused. Missing mask entries mean probability zero in the supplied **complete population/design law**. Empirical unseen masks are not automatically zero-probability outcomes.

Intermediate exact arithmetic is unrestricted. Constructed independent/extremal laws can exceed a separately called function's external32bit parser cap; arbitrary helper composition is not promised. The stored grid stays in the accepted domain. Ordered pair keys in JSON are encoded arrays; library keys are Python tuples. Empty catalogues have expectation/variance zero, while a known empty-carrier event has pi=0 and blocks a complete-catalogue HT total. Only declared positive-probability masks can be used for `ht_value`.

The verifier checks exact extremal laws, marginal identities, event complements, pair bounds and HT moments against complete finite mask enumeration. Benchmark library and CLI refuse Python -O/-OO; engine validation does not depend on assertions.

```sh
cd research/event_capture
PYTHONDONTWRITEBYTECODE=1 python3 verify_benchmarks.py --output /tmp/tmd_event_capture_replay.json --check-against BENCHMARKS.json
sha256sum -c SHA256SUMS.txt
```

[CONDITIONAL_DERIVATION.md](CONDITIONAL_DERIVATION.md) gives the elementary proofs and retained biological boundaries. All fixtures are synthetic. No source cache or new network request is needed.

For TMD, a useful measurement contract must separately justify ancestry, terminal retention, call eligibility and the joint event-inclusion law. Sequenced/available cell fractions do not fill these quantities. Existing route forecasts, actual26-field registry, count-law admission, error allocations and stopping rules remain unchanged. No cancer-prevention, new theorem, external biological validation or priority claim is made. Prepared by Ricardo Maldonado with AI assistance; original code MIT, original notes and synthetic summaries CC BY4.0.
