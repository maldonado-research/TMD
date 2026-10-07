# Independent review of R7's fluctuation contract

The nominal plate geometry and the conditional mathematics are useful method checks. They do not reproduce a biological mutation-rate estimate or resolve any of the 26 missing fields in TMD's actual-study registry.

## What the source supports

The final primary Methods section, `sec016`, describes six individual reporter transformants in each background, each used on two occasions. Figure 4A therefore provides 24 culture occurrences, with colonies and sequenced reads nested within them. Reusing a transformant supports preserving a transformant/occasion hierarchy; it neither authenticates independent construction events nor by itself proves that the later cultures were dependent.

The reported culture volume is 6 mL. The workbook's multiplication by 20 corresponds to a nominal 0.05 mL aliquot. If `I` is the number of selective plates and `J` is the culture dilution fraction, the summed geometric fraction is `I J/120`. The source rows give eight occurrences at `3/40000`, three at `1/6000`, one at `3/4000`, and twelve at `3/40`. This is volume bookkeeping. It does not measure mixing, viable-cell capture, genotype recovery, colony-age effects, post-plating mutations, or the threshold used to recognize a candidate colony.

Every Figure 4A row has at least two confirmed C565T colonies among the selected sequenced colonies. This statement is specific to those 24 rows. The separate S4 destructive time course mentions one occurrence with no target confirmation among the first selected colonies, followed by additional sequencing. Neither an unconfirmed candidate nor a missing read is a validated absence of a mutation event.

The primary Methods report candidate counts multiplied by a sampled confirmation fraction and MSS maximum likelihood analysis through FALCOR. The released material does not authenticate the actual submitted per-culture inputs, density-versus-whole-culture conversion, rounding of fractional corrected counts, software version/settings, partial-plating option, population-denominator recipe, or reported confidence-interval calculation. The previous R6 sampling-frame and read gaps remain unresolved. Reconstructing the workbook's arithmetic does not establish the candidate sampling frame or a binomial/hypergeometric confirmation law.

The source's S2 caption reports a small fitness cost for the mutant reporter in both backgrounds. Absence of a measured growth advantage does not establish equal growth. The source's phase-dependent transcription and S4 terminal frequencies also do not independently establish a constant mutation probability per division. Birth, death, preexisting mutants, clone growth, and recovery must be separated before choosing a biological fluctuation likelihood. The PsrA deletion is an intervention on the reporter background, but these observations alone do not identify transcription as its sole causal mediator or transfer the result quantitatively to native nlpD.

## Conditional model and bounds

Under a stated Poisson number of mutation births with mean `m`, independent clone sizes `K`, and independent descendant capture with probability `p`, the observed-count PGF is

`G(z) = exp{m[g(1-p+pz)-1]}`.

For the classical asymptotic equal-growth law `P(K=k)=1/[k(k+1)]`,

`g(t)=1+(1-t)log(1-t)/t` and `P0=exp[-m A(p)]`, where `A(p)=p log(1/p)/(1-p)` with continuous endpoint values `A(0)=0`, `A(1)=1`.

This clone law has unbounded support and infinite mean. It is an ideal limiting model, not an exact finite-population model of the released cultures. A colony-size gate can make recovery depend on clone age or genotype, violating the single independent capture probability. A fixed-volume aliquot alone does not authenticate an independent Bernoulli capture law.

Zero probabilities identify only the product `m A(p)` when both quantities are unknown. This is a statement about the zero statistic, not indistinguishability of the whole count distribution. In fact,

`P1/P0 = m p[-log(p)-1+p]/(1-p)^2`

for `0<p<1`; it changes along a fixed-`m A(p)` curve. The separately checked finite-clone examples have equal `P0=exp(-1)` yet `P1/P0=2/3` versus `8/255`. These are synthetic counterexamples, not biological observations.

For `t=1-p`, let `S_K=sum_{k=1}^K t^k/[k(k+1)]` and `b_K=t^(K+1)/(K+1)`. Since the remaining weights sum to `1/(K+1)`,

`S_K <= g(t) <= S_K+b_K`.

Consequently `1-S_K-b_K <= A(p) <= 1-S_K`, and for `m>=0`,

`exp[-m(1-S_K)] <= P0 <= exp[-m(1-S_K-b_K)]`.

The clone-sum endpoints can be rational and exact for rational `p`. Decimal evaluations of their exponentials are not outward-certified numerical intervals. These bounds are not statistical confidence intervals. The correction `m_actual=m_observed/A(p)` for the zero method is established theory: Foster (2006), Equation 5, explicitly discusses partial plating. Neither this identity, the finite tail bound, nor the compound-Poisson recurrence is claimed as new mathematics.

## Reviewer recommendation

Accept the R7 package as a source-grounded measurement contract and a bounded conditional model benchmark. The finite-law input-validation correction now passes the reviewed checks. Keep its mathematics separate from TMD's certified score engine and retain all prior fixtures, error budgets, R6 receipts, and 26 unresolved actual-study fields.

A biological continuation needs the original likelihood inputs/settings, an authenticated confirmation frame, calibrated recovery controls, founder and growth/death histories, and paired native/reporter measurements in the same genotype and environmental context. Capture-calibrated full count distributions can be more informative than zeros alone, but practical identifiability and uncertainty still require a validated model and enough independent cultures. Fractional corrected terminal counts should not be silently substituted for observed mutation births.

For the TMD contrast, an assay-specific mutation-supply effect is a competing explanation that must be measured rather than relabelled natural dominance. The discriminating comparison remains a prespecified cross-context or perturbation test of supply-adjusted route outcomes, with independent constraints on establishment, fitness, recovery, and allele origin. A single C565T reporter cannot identify a W/A/M triad, a universal residual curvature, or a finite native/reporter transport bound.

## Sources actually read

- Farr et al., *PLOS Genetics*, DOI [10.1371/journal.pgen.1011572](https://doi.org/10.1371/journal.pgen.1011572): final primary sections `sec007`, `sec015`, `sec016` and embedded S2–S4 captions reread for this review; main article, data provenance and measurement arithmetic were previously assessed in R6. XML SHA256 `937c7eded441b32eea42777d703647965e6090ccb5850017f2b5b6cbd4ea53c2`.
- The released Figure 4A workbook in [10.5281/zenodo.14335473](https://doi.org/10.5281/zenodo.14335473): all 24 geometry rows replayed from the pinned ZIP. ZIP SHA256 `9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6`.
- Foster (2006), *Methods for determining spontaneous mutation rates*, DOI [10.1016/S0076-6879(05)09012-9](https://doi.org/10.1016/S0076-6879(05)09012-9), PMCID PMC2041832: full methods chapter read in R6; Equation 5 and the partial-plating, phenotype-lag and post-plating passages reread in this round. Cached full HTML SHA256 `dd5641f959156f086b93b2309f55bcfd92276382494e697c33721d9e36ab53b4`.

No new source was acquired for this R7 review. Author-response DOCX bodies were not read, FALCOR was not executed, and publisher/software errors are not inferred from missing provenance. All prose and oracle code here are original; no raw article, workbook, sequencing read, private archive file, local machine path, or credential is included.
