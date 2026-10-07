# Normalization and zero handling before biological inference

Mutation by Natural Dominance · R000014 · 7 October 2026, America/Los_Angeles

This follow-up authenticates a declared supplement filename and reassesses the
normalization, low-count handling and introduced-unit/lineage limits of the two
primary sources already inspected in R12. Four new, bounded retrieval requests
did **not** acquire an authenticated DOCX. Original exact arithmetic shows why
the reporting scale matters without replacing the papers' published numbers.
No clinical table was read, no biological mutation rate was fitted, and none of
the 26 actual study inputs is resolved.

## What was authenticated and what remains unavailable

De La Motte et al., [DOI 10.1128/spectrum.03910-25](https://doi.org/10.1128/spectrum.03910-25),
PMC13228076, declares **Data set S1**, filename
`spectrum.03910-25-s0001.docx`, supplemental DOI
`10.1128/spectrum.03910-25.SuF1`. Its caption identifies paired urine cytometry
and culture data. The exact cached main XML authenticates this declaration;
it does not authenticate the supplement's contents or normalization.

Four new attempts saved 71,716 response bytes in total:

| Authoritative route | Actual result | Content assessment |
|---|---|---|
| Direct PMC attachment | HTTP 404; 48,716 bytes | HTML error response |
| DOI-specific publisher supplement | Proxy CONNECT 403; no body | No file acquired |
| Article-specific NCBI OA-package lookup | HTTP 404; 1,588 bytes | HTML error response, no package metadata |
| Alternate PMC instance attachment | HTTP 200; 21,412 bytes | reCAPTCHA HTML, not a ZIP or DOCX |

These were distinct URLs, without automatic redirects, within a six-request,
5 MiB producer limit. No unchanged URL was retried and no challenge was
bypassed. HTTP 200 alone is not file authentication. These scoped access
outcomes do not establish that the supplement is absent elsewhere. Exact
request/status/content-type/size/hash diagnostics are recorded in
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json). Response bodies remain external.

The second reused source,
[DOI 10.1007/s00203-026-04995-3](https://doi.org/10.1007/s00203-026-04995-3),
PMC13272224, provides PA14 persistence, cytometry and regrowth methods.
Reassessment of either paper is not an independent biological replication.
The [measurement ledger](MEASUREMENT_LEDGER.json) has 16 main-text reassessment
rows, one acquisition-diagnostic row and three original conditional-arithmetic
rows. The two cached main texts declare CC BY 4.0; their bodies and any clinical
raw records are excluded from this public package.

## Why the published median of 10 needs a reporting map

The DTT main text reports 10 mL input resuspended in 1 mL, 1 µL plated,
12-hour readout, and a negative threshold below 10 CFU/mL. One counted colony
in 1 µL nominally represents 1,000 CFU/mL of suspension, or 100 CFU per original
mL **if** the tenfold volume conversion is applicable. That is a volume map,
not measured biological recovery.

Under one integer colony count per specimen, a common fixed plate/volume map,
no censoring or averaging, and an ordinary untransformed midpoint median of an
even-sized sample, median values lie on half the single-colony density grid.
The reported untreated median 10 does not lie on either nominal 500- or
50-CFU/mL median grid. Those conditions have not all been authenticated.
This is a reporting question, not proof that the paper is wrong.

The statistics paragraph also declares log10 analysis and a value of 1 CFU
added for culture-zero handling. A **synthetic** example demonstrates a useful
alternative: take 36 zero values and 36 values of 100. Its ordinary raw-scale
midpoint median is 50. If only the zero values are replaced by 1, the two
central adjusted values are 1 and 100. A midpoint median on the log scale
back-transforms to their geometric midpoint, exactly **10**.

This example is not the clinical dataset or an authenticated reconstruction.
It requires a particular concentration scale, zero-only replacement and
back-transformed reporting convention. Applying +1 to every value instead
would give the radical sqrt(101), rather than exactly 10. The actual source
summary convention, pseudocount unit/application, censoring, rounding,
technical averaging and treated/control volume maps remain **UNKNOWN**.
Neither published median, 10 or 5,500 CFU/mL, is changed.

## Marginal summaries cannot recover the paired effect

The published 5,500/10 ratio remains **550: a ratio of reported marginal
medians**. It is not an authenticated median paired fold change, recovery
probability, mutation-rate ratio or new lineage count.

Three original synthetic pairs illustrate the distinction. Untreated values
100/200/10,000 and corresponding treated values 110,000/100/120,000 have a
marginal-median ratio of 550, but paired ratios 1,100/0.5/12 and a median paired
fold change of 12. These invented values are not clinical records.

A common scaling of both groups preserves their marginal-median ratio;
asymmetric scaling can change it. For example, if the reported numbers were
suspension densities and only the treated group were tenfold concentrated,
the hypothetical original-density ratio would be 55. The actual frame is
unverified, so this calculation **does not correct the published result**.
The exact arithmetic and its assumptions are in
[NORMALIZATION_ARITHMETIC.json](NORMALIZATION_ARITHMETIC.json) and
[NORMALIZATION_CONTRACT.json](NORMALIZATION_CONTRACT.json).

## Introduced units and ancestry still need independent evidence

The DTT study's bead normalization and staining controls support its
instrument/classification workflow. They do not authenticate known introduced
native cells or CFU packets, an independently founded mutation population,
loss-free centrifugation or tracked mutation origins. Its 72 specimen pairs
differ from its 69/71 eligible cross-method comparisons and from unique patient
or founder denominators. Operational membrane integrity is not independent
proof of culturability or VBNC.

The PA14 paper's approximate OD-to-CFU mapping, 1,000–50,000 technical events,
gate/initial-inoculum normalization and 24-hour post-antibiotic regrowth likewise
do not supply known individual-unit introductions or original lineage birth
counts. Similar MICs do not exclude every possible mutation. Species/genotype,
physiological state, native/reporter transfer, clumping, growth, selection,
survival, drift and invisible terminal marks remain separate requirements.
Neither source supplies numerical SBW25 recovery or a matched Wsp/Aws/Mws panel.

## Offline reproduction

Write all outputs outside the checkout. The standard library is sufficient:

```sh
python -B verify_normalization.py --arithmetic-only \
  --output /tmp/tmd-r14-arithmetic.json --check-against NORMALIZATION_ARITHMETIC.json
python -B verify_normalization.py --source-dir /path/to/r12-source-cache \
  --response-dir /path/to/r14-response-cache --output /tmp/tmd-r14-full-replay.json \
  --check-against VERIFICATION_RECEIPT.json
sha256sum -c SHA256SUMS.txt
```

The exact primary and response files are named and pinned in
`SOURCE_MANIFEST.json`. Missing primary files mean source replay **UNRUN**.
If primary files exist but failure-response caches do not, omit `--response-dir`
and `--check-against`; the result explicitly records failure-response replay
UNRUN. Hashes alone do not restore sources. Arithmetic-only mode does not read
or authenticate sources. All verification entry points refuse Python -O/-OO.
The verifier never downloads, sends messages, fits clinical observations or
publishes anything.

Next progress requires an authoritative supplement acquisition and an explicit
count/volume/censoring/reporting map, plus suitable introduced-unit and lineage
controls in a matched biological frame. No author request was sent. The source
definition of natural dominance, prospective forecasts, actual registry,
confirmatory count laws, error budgets and stopping rules are unchanged. There
is no new theorem, biological TMD validation or cancer-prevention claim.

Prepared by Ricardo Maldonado with AI assistance. Original code is MIT;
original notes, ledger and synthetic summaries are CC BY 4.0. No private archive
content, personal records or raw clinical table is included.
