# Hypothetical control-resource calculations

TMD continuation · 8 October 2026, America/Los_Angeles

These standard planning illustrations recover previously unpublished calculations. They are not new mathematics, native control observations, mutation-rate estimates, a TMD prediction, achieved power, or a selected study size. The illustrative single-metric alpha does not change any project error allocation, threshold or stopping rule. No qualified external scientific review has been obtained.

For a fixed number `n` of independent, homogeneous Bernoulli origin-error trials, zero observed errors gives the one-sided Clopper–Pearson upper confidence bound

    U = 1 - alpha^(1/n).

For the illustration `alpha = 1/20`, `U <= epsilon` exactly when `20*(1-epsilon)^n <= 1`. Integer powers verify the following minima, including failure at `n-1`:

| Hypothetical epsilon | Minimum n, conditional on zero errors |
| --- | ---: |
| 1/100 | 299 |
| 1/1000 | 2,995 |
| 1/10000 | 29,956 |

At a hypothetical `n=500`, the exact strict bracket is

    5973551516/10^12 < U < 5973551517/10^12,

or about `0.59735515%`. A 95% confidence bound concerns coverage over repeated fixed-size sampling under the assumed binomial model. It is not a posterior probability that the error rate lies below the realized bound. These sample counts do not guarantee zero errors or provide a power calculation.

For one defined eligible candidate-origin frame,

    PPV = p*s / [p*s + (1-p)*f].

Hypothetical `p=1/1000` and `s=9/10` give exactly `100/211` (about `47.39336493%`) for `f=1/1000`, and `1000/1111` (about `90.00900090%`) for `f=1/10000`.

The required truth is origin-negative truth: independent ancestry and acquisition-episode evidence, including true inherited or pre-existing variants where relevant. A correct genotype can still be assigned a false new origin. The full caller, eligibility frame, exclusions and evaluation plan must be frozen; an error definition or caller selected after seeing the evaluation outcomes is outside this illustration. Unauthenticated truth may measure disagreement instead of actual origin error.

Here `p` is the positive prevalence in the intended eligible candidate-origin frame; `s` and `f` are sensitivity and false-positive probability for the same complete caller and truth definition in that frame. `p` is neither a mutation rate nor the selected mixture of an enriched control panel. Germline variant precision is not native origin specificity. Transporting any quantities between frames requires evidence. The PPV formula is a probability identity and does not itself assume independent candidates; independence is required for the stated binomial confidence calculation. Cells, descendants, calls and batches are not automatically independent, and pooling contexts does not establish homogeneous or route-specific calibration.

No native `p`, `s`, `f` or event inclusion `pi` was estimated. All actual study and control-planning fields remain unresolved. Internal AI verification does not replace qualified biological/statistical assessment.

Run with only Python's standard library:

```sh
python3 -B verify_control_calculations.py --output /tmp/tmd_control_resource.json
python3 -B verify_control_calculations.py --check-against RESULTS.json
```

The script uses integer powers and exact fractions for every scientific comparison. Its rounded decimal strings are for display. The result is a fresh recovery receipt, not the historical verification receipt. Original code is MIT; original notes and synthetic summaries are CC BY 4.0. Prepared for Ricardo Maldonado with AI assistance.
