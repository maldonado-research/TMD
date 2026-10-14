# R32: HiDenSeq calibration architecture; supporting information unacquired

The accessible [version-one main text](https://www.biorxiv.org/content/10.64898/2026.08.03.742544v1.full), posted 7 August 2026, clarifies how HiDenSeq converts reads to absolute mutant numbers. In the canUVanine comparison, the authors fit the non-UV population to the canonical Luria–Delbrück distribution to set that conversion, then apply it to the UV populations. This is a fitted calibration transported between experimental arms. It is not evidence of an independently calibrated native Wsp/Aws/Mws supply or a confirmed TMD fit.

Husain, Flagg, Pincus and Murugan's preprint, DOI [10.64898/2026.08.03.742544](https://doi.org/10.64898/2026.08.03.742544), remains a yeast canavanine-resistance method lead. The inspected version has not been certified by peer review. This report refines the [R31 assessment](../barcoded_assay_lead/REPORT.md); it does not revise its reported measurements or admit new biological inputs.

## What the main text resolves

The general analysis begins with a colony-count estimate of total mutants and refines that scale during fitting. The canUVanine paragraph in Results II.D states more specifically that the read-to-mutant calibration is fixed by fitting the non-UV population, before comparison with the two UV-exposed populations. The authors then fit spontaneous-only and spontaneous-plus-induced model families. Their reported agreement between inferred induced rates and independent mutant colony counts before and after UV is a relevant corroborating observation. The underlying counting, uncertainty and analysis details are referred to supporting information, which was not acquired here. We retain the corroboration as an author report, without independently verifying its measurements or importing it into TMD.

Discussion III proposes known-abundance barcoded spike-ins for future implementations. The proposal is not a record that those standards were used in the reported experiment. Fitting itself does not disqualify a calibration: what matters for a prospective TMD test is the experiment used to estimate it, identifiability, joint uncertainty, transport to the evaluation context and the freeze before evaluation.

| Calibration path | TMD implication; no path is admitted here |
| --- | --- |
| A separate calibration experiment estimates scale and rates jointly | Potentially assessable with an identifiable model, honest joint uncertainty, an independently justified count law, complete native route/context records and a freeze before evaluation. |
| A non-UV reference sets scale for UV populations | The source reports this architecture. The applicability and uncertainty of that transport need the underlying records; the architecture alone does not establish independent native calibration. |
| A held-out evaluation endpoint estimates its own supply scale | That fitted scale cannot also be called an independently frozen supply predictor for that same endpoint. |
| Known-abundance spike-ins | A concrete future calibration suggestion in this source; no implemented spike-in record was acquired. |

The authors explicitly leave general mechanism identifiability open. Their discussion notes that mutant fitness and phenotypic switching can both affect distribution tails, with their distinguishability unresolved. Successful comparisons between specified model families therefore do not identify every molecular mechanism uniquely. Orthogonal event genotype, parental ancestry and inherited-negative observations remain necessary for the claim-specific TMD gates.

## What remains unresolved

The main text describes pooled barcoded growth, approximately ten founder cells per barcode, and computational merging into virtual lineages. It does not supply an acquired barcode-to-group allocation sufficient to establish disjoint groups, overlap across analyses, physical-pool dependence or an independent trial/count law. The addition property invoked for the fitted model does not authenticate those empirical conditions. Barcode and read totals remain lineage measurements, not a count of independently verified mutation births.

Postselection non-detection and stable detected barcode frequencies address different questions. Stability is an observation about the surviving detected population in this yeast selection context. Neither observation alone bounds births followed by extinction, poor recovery, phenotypic delay or insufficient sequencing; neither establishes ancestral absence of resistance. The authors' stated fitness/competition confound and need for additional calibration in other selective environments still apply. Yeast results do not establish transport to frequency-dependent SBW25 WS competition, establishment or recovery.

## Acquisition and scope

The named [supporting-information landing page](https://www.biorxiv.org/content/10.64898/2026.08.03.742544v1.supplementary-material) returned a Cloudflare HTTP 429 page. Its scientific content and actual supplementary file link were not obtained. Three distinct indexed searches and one separately indexed full-text HTML acquisition did not identify a target supplementary file or actual data/code deposit. The main text retains a future-tense public-repository promise. This is bounded non-identification, not a global absence finding. A broad HiDenSeq name search predominantly retrieved the unrelated bacteriophage HIDEN-SEQ method; those results and its GitHub repository are excluded from the target evidence family.

The HTML acquisition contains the main article, with displayed equation images and links; equations were not reconstructed or reanalysed. It is a provider representation, not original document bytes or a full supplement. Five local acquisitions saved 541,815 UTF-8 JSON bytes, including the rate-limit response and duplicated provider representations. The sixth allocated call was unused. Source wire/provider-internal bytes are unknown.

Two shared root acquisitions, counted separately at 26,719 bytes, identify the same preprint as PMCID [PMC13484652](https://pmc.ncbi.nlm.nih.gov/articles/PMC13484652/) and PMID [42620021](https://pubmed.ncbi.nlm.nih.gov/42620021/). The PMC response contains metadata and an abstract, followed by an explicit statement that full text is not archived there; it supplies no supporting-file link. Its CC BY 4.0 display and explanation attributing nonarchiving to license terms are retained as a metadata/availability discrepancy, without inferring a rights correction. These aliases are not an independent study or peer review.

The verifier checks public integrity and frozen dependencies; source replay is explicitly UNRUN without the appropriate external caches. With caches it checks identities and selected source anchors, including the calibration distinction, corroborating author report, open identifiability question and PMC coverage limit. It does not reproduce an experiment or authenticate original source files. Exact public membership is enumerated in PUBLIC_FILES.json; raw bodies, provider metadata and private paths remain outside Git.

All 26 study fields and 18 planning fields remain NULL. No actual stock, matched panel, event, fit, new theorem, laboratory work or outreach is admitted or commissioned. Frozen R5/R11/R17, theta/eta forecasts, comparators, error allocation, fixed stopping, paused automation and methods 0.6.0 remain unchanged. The next useful acquisition is an actual version-matched supplement or deposit link that can resolve the remaining grouping, scale/uncertainty, ancestry or loss gates. An unchanged broad search is not required.

Original assessment and derived facts: CC BY 4.0. New verification code: MIT. Ricardo Maldonado with AI assistance. Third-party rights remain unchanged.
