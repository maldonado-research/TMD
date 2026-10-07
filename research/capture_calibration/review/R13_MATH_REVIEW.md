# R13 independent conditional recovery review

**Accepted:** the eight producer payload files pinned in
`R13_REVIEW_RECEIPT.json`. The original ten-file producer freeze (including its
two manifests) is separately recorded. Root may add accepted review files and
regenerate final manifests without changing the eight reviewed payloads.

The independent derivation and 960-case rational oracle were prepared before
the producer implementation was read or imported. The independent forward
matrix is built by enumerating assignments on labelled Bernoulli-retained units;
the inverse uses general Gauss-Jordan elimination. The producer uses binomial
coefficients and triangular back-substitution. Both agree exactly over the
tested declared domain.

Independent internal invariants passed 10,747 checks; the frozen producer
comparison passed 20,154 checks. All 960 sweep cases were accepted by the
external parsers for forward, inverse and point-bound inputs. Two additional
extreme valid capture fractions test unrestricted derived rational arithmetic;
the resulting over-cap fractions are correctly refused as inputs to a separate
helper. These are synthetic algebraic checks, not biological trials. Assignment
state counts are explicitly separate from check totals.

The producer's 1,624 checks replayed byte-for-byte. Six launcher/library checks
confirm that producer CLI, producer benchmark library and independent oracle
CLI all reject -O/-OO. Input and compatibility checks in the mathematical
engine do not depend on Python assertions. The original whitelist and nine
checksum entries passed.

The principal result is conditional population-law identification. For known
homogeneous independent capture c>0 and justified finite terminal mark size
B, a complete compatible population positive jump vector identifies its
positive terminal intensities. With no zero terminal marks, their sum identifies
m; at m=0 the mark law is undefined. B does not bound the aggregate
compound-Poisson count. A finite histogram does not provide the exact population
jump vector, and this package supplies no estimator, sample-size calculation,
goodness-of-fit procedure or confidence interval.

The complete-law unknown-c singleton ambiguity and known-c zero-terminal-mark
ambiguity are correct and remain separate. Additional zero-terminal intensity
cannot be recovered even with perfect terminal capture. Inversion sensitivity,
calibration uncertainty, packets versus cells, and native/control transport
prevent a biological identification from following from the algebra alone.

The void-exponent point bounds and deterministic rectangle envelope are correct
and their attainable endpoints are verified. The rectangle is an externally
justified admissible parameter set, not an empirical confidence region. Output
endpoints are intentionally untruncated even when they exceed the wrappers'
20-intensity computational cap; this cap is not a biological prior.

Nothing in these results identifies molecular mutation births, division
exposure, ancestry or inherited origin. Growth, extinction, selection,
establishment, drift, imported alleles, observation loss and assay eligibility
remain meaningful competing explanations. No registry field, confirmatory
count law, forecast, error budget, stopping rule, causal mechanism or biological
validation is supplied or modified. The formulas are established Poisson
marking and binomial inversion, with no theorem-priority or cancer-prevention
claim.

Reproduce the independent comparison offline, writing its result outside Git:

```sh
python -B independent_recovery_oracle.py \
  --implementation /path/to/capture_calibration.py \
  --expected-sha256 d0d28eb36def27d9f01dd5f8b0b31568411ad9aa4a63f74c44ce321c42ba9444 \
  --output /tmp/tmd-r13-independent-comparison.json
```

No network requests, private sources, observed clinical data, publication
requests or external messages were made by this reviewer.
