# Independent internal review of conditional design diagnostics

5 November 2026 · AI-assisted internal mathematical and computational review

This review independently derived the integer support movements, fiber dimension,
conditional information interpretation, and full-model allocation formula. The
reviewer read the existing conditional-curvature and prospective-design methods
before assessing the companion calculation. These are standard multinomial and
exponential-family arguments; this work supplies no new-theorem, biological,
external-peer-review, or study-registration claim.

The independent oracle reconstructs matched-baseline conditional probabilities
from local binomial coefficients and raw arm multinomial masses. The producer
instead groups raw null joint-table masses. The oracle imports the producer only
to compare its geometry function; its probability reconstruction does not call
the producer's probability or design routines.

Executed checks cover:

- 3,136 local baseline/selected count-table pairs, with each arm total from zero
  through five, checking the complete local support against the two-unit move.
- 1,554 combinations of the resulting six distinct capacity patterns across one
  through four contexts, comparing fiber size and claimed covariance rank with
  direct integer enumeration and exact rational affine-rank calculation.
- All nine B+N=8 splits in `DESIGN_BUDGET_8.json`, independently matching the
  **matched-baseline** fiber counts and size histograms, expected null conditional
  information, and singleton, rejection-attainable-fiber, and rejection
  probabilities under all three declared laws.
- Exact null symmetry under exchanging the baseline and selected arm sizes.

All checks passed. `ORACLE_RECEIPT.json` records their scope and exact matched-
baseline information and rejection probabilities. The oracle does not separately
replay the known-offset comparator summaries. Those summaries were reviewed
mathematically, and the producer's verifier compares every selected table for
N=0..8 with the unchanged, previously verified known-offset engine. These are
different checks and should not be described as an independent full replay of
that comparator.

The mathematical assessment found no conflict between the support criterion and
the stated model. Nontrivial support, positive information for a contrast,
attainability at a specified alpha, and unconditional power are distinct. The
full-model Fisher allocation is a local planning calculation; sparse finite
fibers can retain much less information. Lower expected conditional information
does not imply lower power for every particular discrete probability-ordering
test. The matched observed-offset and joint independence contracts remain
necessary for inferential interpretation.

To reproduce without changing checkout receipts, copy this directory to a fresh
scratch directory and run its oracle:

```sh
review_dir=$(mktemp -d /tmp/tmd-conditional-review.XXXXXX)
cp research/conditional_design/design_diagnostics.py \
   research/conditional_design/DESIGN_BUDGET_8.json \
   research/conditional_design/independent_design_oracle.py "$review_dir/"
python -B "$review_dir/independent_design_oracle.py"
```

The default package directory is the directory containing the oracle. An optional
`--package PATH` selects producer code and budget data elsewhere. Receipts always
go beside the oracle. Optimized Python modes are refused because the oracle uses
assertions.

`ORACLE_HASHES.json` contains SHA-256 hashes of the executed oracle, producer
`design_diagnostics.py`, input `DESIGN_BUDGET_8.json`, and completed oracle receipt.
The hash manifest is separate to avoid hashing itself recursively. It binds these
bytes, not biological validity or external verification. Changes to those inputs
require another replay and refreshed hashes.

Original review text is CC BY 4.0 and original oracle code MIT under the repository
terms. No third-party code was copied or executed for this review.
