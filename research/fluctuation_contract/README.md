# A partial-plating contract and conditional fluctuation benchmark

Ricardo Maldonado · Mutation by Natural Dominance · R000007 · 7 October 2026 (America/Los_Angeles)

This round resolves one concrete part of the released SBW25 assay geometry and implements an offline benchmark for the classical clone-and-sampling model. **The geometry is nominal, the numerical model is conditional and synthetic, and no biological mutation-rate fit is performed.** The actual TMD study still has 26 unresolved inputs and zero admitted matched Wsp/Aws/Mws panels.

Source: Farr, Vasileiou, Lind and Rainey (2025), [10.1371/journal.pgen.1011572](https://doi.org/10.1371/journal.pgen.1011572), and its CC BY 4.0 figure-data record [10.5281/zenodo.14335473](https://doi.org/10.5281/zenodo.14335473). This is a follow-up to the [R6 source audit](../sbw25_data_audit/README.md); its acquired raw files and original outputs are preserved. Source workbooks, reads and article text remain outside this package.

## What is now resolved

The final article reports 6 mL fluctuation cultures, with 22 hours of assay growth after a 24-hour pregrowth step. Workbook scaling implies 50 µL per selective plate. For `I` selective plates and a culture dilution fraction `J`, the summed nominal fraction of a 6 mL culture represented on those plates is

\[
p_{\rm nominal}=\frac{I(0.05\,\mathrm{mL})J}{6\,\mathrm{mL}}=\frac{IJ}{120}.
\]

| Background | Nominal sampling fraction | Culture occurrences |
|---|---:|---:|
| SBW25 reporter | 3/40,000 | 8 |
| SBW25 reporter | 1/6,000 | 3 |
| SBW25 reporter | 3/4,000 | 1 |
| SBW25 ΔpsrA reporter | 3/40 | 12 |

The [machine-readable contract](MEASUREMENT_CONTRACT.json) preserves all 24 row mappings and initial CFU estimates. Six individual transformants per background were used across two occasions. Initial density is a dilution-plating CFU estimate; multiplying it by 6 mL does not create a known number of independent single-cell founders. Actual culture volume at plating, mixing, viability, clumping, selective recovery, colony-size detection, delayed mutation and genotype confirmation can change observation probability. **Nominal aliquot geometry is not a calibrated total detection probability.**

The released Figure 4A rows all have at least two confirmed C565T colonies. This statement applies to that 24-culture table. The separate S4 time-course methods describe an initially negative confirmation sample followed by 24 additional sequenced colonies; outcome-dependent sampling remains explicit. No complete culture-absence observation frame is admitted for a zero-class fit. The R6 7-counted/8-sequenced pool discrepancy and 94-read/95-confirmation provenance gap remain unresolved.

## Final article and review history are separate source states

The pinned XML contains seven review-history subarticles. Reviewer comments question stationary-phase timing, constant mutation probability, reporter fitness, selection and the comparison with mutation-accumulation averages. These are dated peer-review assessments of earlier manuscript states, not new experiments or final methods. The final article adds time-course frequency discussion but does not thereby establish every clone-growth or mutation-process assumption.

Author-response bodies are linked DOCX supplements, rather than embedded in the cached XML. Two official PLOS GETs were attempted with scoped escalated network access and returned `URLError`; the inner cause was not captured, so DNS, proxy, TLS and server failures cannot be distinguished. Two NCBI mirror GETs returned HTTP 200 with non-DOCX responses. **No author-response DOCX body was acquired or read**, and permanent unavailability is not asserted. The [acquisition receipt](ACQUISITION_RECEIPT.json) records four attempts and 42,794 response bytes. No additional retry or credential was used. Editor contact details and raw review text are excluded.

## The existing model and its observation law

Declare an ideal model: the number of mutation events is Poisson with mean `m`; each event independently leaves a terminal mutant clone with the asymptotic equal-growth Luria–Delbrück law

\[
\Pr(K=k)=\frac1{k(k+1)},\quad k\ge1,\qquad
g(z)=\sum_{k\ge1}\frac{z^k}{k(k+1)}
=1+\frac{1-z}{z}\log(1-z).
\]

The continuous endpoint values are `g(0)=0` and `g(1)=1`. This is a normalized heavy-tailed idealization with unbounded clone size and infinite mean clone size, not an exact finite-population distribution for these cultures. Selection, changing growth, death, mutation timing and finite population constraints can change the clone law.

For independent capture of each terminal descendant with known probability `p`, probability-generating functions compose:

\[
G_{\rm obs}(z)=\exp\{m[g(1-p+pz)-1]\},
\]

\[
P_0=\exp[-mA(p)],\qquad
A(p)=\frac{p\log(1/p)}{1-p},\quad A(0)=0,\ A(1)=1.
\]

This is established fluctuation-analysis theory. Foster (2006), [10.1016/S0076-6879(05)09012-9](https://doi.org/10.1016/S0076-6879(05)09012-9), gives the zero-class partial-sampling correction in Equation 5. The chapter was acquired and read in the preceding methods review. Hall et al. (2009), [10.1093/bioinformatics/btp253](https://doi.org/10.1093/bioinformatics/btp253), was inspected at abstract/metadata depth only; no full-text or FALCOR execution is claimed. No new theorem, priority or mutation mechanism is claimed here.

For the four source nominal fractions, the ideal model's `A(p)/p` is approximately **9.4987, 8.7010, 7.2008 and 2.8003**, respectively. These are synthetic-model factors evaluated at released assay geometry, not estimated recovery, actual mutation rates or a recalculation of the author's MSS results. Clone bursts make a zero-class correction differ from treating descendants as independent mutation births. A mutation-event parameter `m` becomes a per-division rate only under a documented division/population and software convention; terminal CFUs alone do not supply it.

## What zero observations could and could not identify

Under the stated model, zero-class observations identify the scalar `λ=mA(p)`; unknown `m` and `p` can give the same zero probability. The benchmark constructs three models with identical synthetic `λ=0.7` and different `p`, showing identical `P0` but different `Gobs(1/2)`. **Zero-only confounding does not establish nonidentifiability of the full count distribution under a specified model.** Counts beyond zero can distinguish these examples; an admissible likelihood still needs the sampling and clone-law contract.

More generally, if each mutation event leaves `Y` terminal descendants,

\[
-\log P_0=m\,\mathbb E[1-(1-p)^Y].
\]

For `p>0`, if every event leaves at least one terminal descendant, the visibility factor lies between `p` and `1`, giving the conditional bound

\[
-\log P_0\le m\le\frac{-\log P_0}{p}.
\]

Allowing extinct or unrecovered clones with `Y=0` removes the positive visibility lower bound and the finite upper bound on `m`. Different mutation-time/clone-size histories can also yield the same zero intensity. The benchmark illustrates fixed terminal clone sizes 1, 2 and 8 with different synthetic event intensities and identical `P0`. None of these conditions or quantities is fitted to Farr's cultures. Nominal physical fractions cannot be substituted for validated capture probabilities in these bounds.

An unknown confirmation fraction, false-positive resistance, incomplete candidate sampling or age-dependent size gates further change the observation map. Multiplying candidate CFUs by `L/M` produces a fractional corrected descendant estimate, not an observed integer birth count and not automatically an admissible count for an MSS likelihood. A pgf for independent descendant thinning does not justify a binomial confidence law for the source's nested colony confirmations.

## Exact finite checks and numerical scope

The original code includes a separate **finite capped-clone synthetic model**, with exact rational weights, for testing thinning and compound-Poisson coefficient calculations. It is distinct from the infinite asymptotic clone law. Two algorithms compare `P_n/P0`: a pgf-derived recurrence and direct finite polynomial/exponential-series convolution. Their results agree exactly across **324 coefficient identities**. Another **48 exact thinning identities** check pgf composition. Shared PMF validators reject nonnormalized, negative, oversized, floating, Boolean and unsupported laws; **27 malformed-law guards pass**.

The helpers have explicit support/count and 128-bit rational-input caps. A law returned by thinning can have a larger denominator and be rejected by a later coefficient helper, even when the original law and sampling fraction were accepted. Passing the fixed benchmarks does not guarantee that every permitted input composition can execute. No global Decimal error certificate is claimed; cap violations stop evaluation rather than justify changing an assay input.

For the infinite law, define `S_K=Σ_(k≤K)(1−p)^k/[k(k+1)]`. Its omitted tail obeys

\[
S_K\le g(1-p)\le S_K+\frac{(1-p)^{K+1}}{K+1}.
\]

Exact rational sums and tail expressions support **21 numerical checks** of the analytic form. Exponentiating gives the corresponding symbolic zero-probability bounds. Decimal logarithms and exponentials use 80 digits; rounded numerical outputs are **not outward certificates or statistical confidence intervals**. The source-specific exact-geometry and long-series internal review is separate evidence about this implementation.

The model is a tool for auditing assumptions and designing comparisons. It does not fit biological rates, turn simulation into observation, fill the TMD registry or identify a natural-dominance force. The author's reported 58.33 mutation-rate ratio remains a reported estimator output; the R6 118.97 terminal-frequency ratio remains a distinct descriptive estimand.

## Reproduce or request the remaining contract

Python 3.12 and the standard library suffice:

```sh
python3 run_benchmarks.py --output /tmp/tmd_r7_synthetic.json \
  --check-against SYNTHETIC_BENCHMARKS.json
python3 reproduce_measurement_contract.py \
  --zip /path/to/source_data.zip --article /path/to/nlpd_hotspot_2025.xml \
  --output /tmp/tmd_r7_contract.json --check-against MEASUREMENT_CONTRACT.json
```

If raw source caches are absent in a restored cloud task, synthetic benchmarks and public hashes can still run; the source-contract replay must be marked **UNRUN**, not passed. The R6 downloader supplies the pinned public ZIP; acquisition of source XML is separate. These commands do not regenerate or overwrite preserved public source outputs.

[The prepared source-fields packet](SOURCE_FIELDS_REQUEST.json) asks for exact FALCOR inputs/options, per-culture counts/volume/rounding, growth/division history and colony/read mapping. It is a concrete request draft and **has not been sent**. [The verification receipt](VERIFICATION_RECEIPT.json) records actual execution and unresolved limits. This original exploratory audit and internal AI-assisted review are not external peer review or a registered study. Code is MIT; original notes and attributed derived summaries are CC BY 4.0. Private archive material and credentials were neither used nor published.
