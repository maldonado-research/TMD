# TMD literature and independent-data opportunities

Later original reviews are indexed in the [current research notes](research/README.md), including the [2 October primary-source watch](research/source_watch/2026-10-02/README.md). The historical search and inspection limits below are preserved.

**Research date: 30 September 2026.** This is a targeted primary-source search for mutation-route prediction, mutation supply, WS Wsp/Aws/Mws, Bacillus subtilis rpoB, and context-dependent establishment. It does not claim to cover the entire web. The current TMD handoff's first 400 lines supplied the model context; user sources were not edited. Several publisher/PMC pages returned access challenges, so the inspection depth is stated where it matters. A paper's support for mutation-biased adaptation is not independent confirmation of TMD's added restrictions.

## Main finding

The highest-value immediate work is to improve and independently challenge the mutation baseline. Recent work makes **local sequence context** and **DNA repair background** measurable alternatives to a context-independent correction. A TMD residual fitted against an incomplete baseline can absorb ordinary mutation hotspots, genotype effects, selection during recovery, or missing routes. Treat those possibilities as competing explanations before interpreting a residual as a new biological law.

There are also authentic public data that can be audited now. The multi-taxon dataset in item 3 is the most immediately usable, licensed candidate. It can test baseline construction and sensitivity to mutation spectrum/codon composition. Its pooled adaptive substitutions do **not** supply independent first-successful-arrival races, so it cannot validate TMD's arrival-time assumptions or the WS manifold.

## Ten useful primary studies

### 1. Genetic dissection of DNA damage tolerance in Bacillus subtilis: RecA and recombination functions regulate translesion synthesis

**Rubén Torres and Juan C. Alonso, 2026.** Published journal article, *Nucleic Acids Research* 54(13), gkag673; publication date 3 July 2026. [DOI](https://doi.org/10.1093/nar/gkag673), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC13335488/), [bibliographic record](https://pubmed.ncbi.nlm.nih.gov/42406627/).

The authors examine mutagenesis, survival and rpoB resistance spectra across DNA-damage-tolerance/repair backgrounds, with and without MMS exposure. H482 substitutions remain prominent, while some routes differ with treatment. The article identifies mutation spectra in Supplementary Table S6 and numerical assay data in Tables S2–S5. Its data statement says the main text/supplements contain the conclusion-supporting data; raw material is available on request. A 14.8-MB supplementary ZIP named `gkag673_supplemental_files.zip` is listed, but its direct download was not resolved here.

**TMD opportunity:** an external repair-by-environment rpoB panel, after checking isolate independence, denominators, strain definitions and recovery protocol. Separate mutation frequency from surviving-isolate composition. **Challenge:** predominant resistant isolates do not alone identify higher fitness or a unique μ/A/F factor. Full article downloads were access-limited; indexed primary text and metadata were inspected.

### 2. G_nT Motifs Can Increase T:A→G:C Mutation Rates Over 1000-fold in Bacteria

**James S. Horton, Joshua L. Cherry, Gretel Waugh and Tiffany B. Taylor, 2025.** Published journal article, *Molecular Biology and Evolution* 42(8), msaf183; publisher online date 4 August 2025. [DOI](https://doi.org/10.1093/molbev/msaf183), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12344412/), [data and custom R script](https://doi.org/10.17605/OSF.IO/HSYFX). Article license: CC BY 4.0; repository asset licenses still need inspection.

The experiments and comparative analysis establish strongly context-dependent hotspot potency. The paper specifically connects previously observed WS-associated **awsR A79C** and **wspF T812G** with G_nT motifs. Its experimental phenotype is motility restoration in an engineered P. fluorescens background, not WS forecasting. The largest rate increases are motif/context-specific; they are not universal per-gene multipliers.

**TMD opportunity:** annotate the exact ancestral sequence, strand and local motif around each observed WS mutation before aggregating route supply. Compare mutation-only baselines with and without these independently supported hotspots. **Challenge:** a shared Aws correction might partly reflect a misspecified q. A motility result cannot itself establish the WS curve. Full primary text and data statement were inspected; OSF assets were not downloaded.

### 3. Molecular adaptation reflects taxon-specific mutational biases

**Bryan L. Gitschlag, Arlin Stoltzfus and David M. McCandlish, 2025.** bioRxiv preprint, version posted 5 September 2025; **not verified as a peer-reviewed journal publication** in this search. [DOI](https://doi.org/10.1101/2025.09.03.674101), [author-institution PDF](https://repository.cshl.edu/id/eprint/42179/1/10.1101.2025.09.03.674101.pdf), [code/data repository](https://github.com/bgitschlag/mbamta), [source-data archive](https://github.com/bgitschlag/mbamta/blob/main/Gitschlag_et_al_2025_SOURCE_DATA.zip). Manuscript CC BY 4.0; repository identifies CC0-1.0.

The authors pair independently obtained mutation spectra with 5,488 adaptive missense events across 14 species and account for species-specific codon use. Their observed correlations support mutation-spectrum information as an adaptive-outcome predictor in the sampled settings.

**TMD opportunity:** audit codon-weighted q, mutation-spectrum uncertainty and sensitivity to event concentration. **Challenge:** these are aggregated substitutions from heterogeneous studies, not exchangeable route winners with waiting times. Some mutation spectra use neutral variation rather than direct mutation accumulation. Preserve taxon and source strata; do not manufacture independent replicate races. The institutional PDF and repository README were inspected.

### 4. Fluidity and Predictability of Epistasis on an Intragenic Fitness Landscape

**Sarvesh Baheti, Namratha Raj and Supreet Saini, 2025.** eLife **Reviewed Preprint**, v2 dated 30 October 2025, DOI [10.7554/eLife.104848.2](https://doi.org/10.7554/eLife.104848.2); first reviewed version dated 3 February 2025. [Primary reviewed-preprint page](https://elifesciences.org/reviewed-preprints/104848). No separate data/code download was verified here.

The work reanalyzes an approximately 260,000-variant E. coli folA landscape. Pairwise epistasis changes across backgrounds, and strong global patterns are concentrated in a subset of mutations. This is a secondary analysis of primary experimental measurements, not a new TMD experiment. The current version's publication category is retained instead of treating reviewed-preprint status as a conventional version of record.

**TMD opportunity:** compare a shared route tilt with explicitly background-dependent fitness terms before portability claims. **Challenge:** a low-dimensional fit need not imply a background-invariant mechanistic factor. Indexed primary abstract, introduction and version information were inspected; the publisher page/PDF returned an access challenge.

### 5. Additive effects of environmental and demographic variation shape the repeatability of evolution across replicated experiments

**Karen Bisschop, Meike T. Wortel and colleagues, 2026.** Published journal article, *Evolution Letters* 10(4):382–395; online article date 21 May 2026. [DOI](https://doi.org/10.1093/evlett/qrag017), [primary article](https://academic.oup.com/evlett/article/10/4/382/8690031), [data and R code](https://doi.org/10.5281/zenodo.17497646), [genetic data BioProject](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1252273/).

Five institutes replicated C. elegans experimental evolution under new rearing conditions. The work is useful for assessing repeatability and variation across implementations, rather than assuming replication across contexts has a single source of variability.

**TMD opportunity:** use the published design as a template for lab/batch/environment covariates and a test that leaves an entire laboratory or context out. **Challenge:** a shared coefficient can hide protocol or demographic effects. These nematode results are not a bacterial first-arrival route assay. Bibliographic metadata, primary abstract and data/code availability statement were inspected; deposited files and their licenses were not downloaded.

### 6. Distribution of mutation rates challenges evolutionary predictability

**T. Anthony Sun and Peter A. Lind, 2023.** Published research article, *Microbiology* 169:001323. [DOI](https://doi.org/10.1099/mic.0.001323), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10268835/), [author-institution full text](https://www.diva-portal.org/smash/get/diva2%3A1761543/FULLTEXT01.pdf). No code repository download was verified here.

The paper uses numerical simulations to examine heterogeneity in mutation rates and the difficulty of observing rare WS pathways. Its model deliberately excludes fitness variation and does not establish a universal log-normal rate distribution. It shows that repeated recovery of common routes need not imply the absence of rare alternatives; inference also depends on route aggregation.

**TMD opportunity:** test missing-route mass, target-size uncertainty and hotspot heterogeneity in q; report both molecular and pathway resolution. **Challenge:** treating Wsp/Aws/Mws as exhaustive and fixed supply as certain can overstate predictability. Primary indexed full-text sections and institutional manuscript were inspected.

### 7. Predicting mutational routes to new adaptive phenotypes

**Peter A. Lind, Eric Libby, Jenny Herzog and Paul B. Rainey, 2019.** Published journal article, *eLife* 8:e38822, 8 January 2019. [DOI](https://doi.org/10.7554/eLife.38822), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6324874/), [equations and source code supplement](https://doi.org/10.7554/eLife.38822.022).

This decisive WS study connects pathway architecture, mutation supply and selected outcomes. Unanticipated hotspots caused departures from initial predictions; the spectra measured with and without selection differed, including lower-fitness WS-causing mutations found without selection. The article provides source data for Figures 6 and 9 in its supporting files.

**TMD opportunity:** build mechanistic q from independently measured unselected supply and test selected route outcomes separately. **Challenge:** it already supplies a concrete mutation-plus-selection explanation, so TMD must demonstrate useful additional predictive restrictions rather than rebrand the general idea. Indexed primary article, metadata and supplementary availability were inspected; individual figure-data downloads were not performed.

### 8. The Spectrum of Spontaneous Rifampin Resistance Mutations in the Bacillus subtilis rpoB Gene Depends on the Growth Environment

**Joss D. Leehan and Wayne L. Nicholson, 2021.** Published journal article, *Applied and Environmental Microbiology* 87(22):e01237-21. [DOI](https://doi.org/10.1128/AEM.01237-21), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC8552901/). Main-text mutation tables and competition measurements are the directly identified data objects; no separate raw-data repository was verified here.

The study compares 60 independent cultures per growth medium (LB and SMMAsn) and tests competitive fitness of prominent rpoB mutations. This is the existing biological source for TMD's two-medium branch; reanalysis is not independent new validation. Its sampling rule must remain tied to recovering Rif-resistant isolates rather than being renamed first successful adaptation.

**TMD opportunity:** reconcile exact route/count extraction with the study's independent cultures and compare measured competition effects with route enrichment. **Challenge:** culture-specific growth and selection can affect the recovered spectrum; counts alone do not separate μ, accessibility and establishment. Primary indexed article sections were inspected.

### 9. Mutations in rpoB That Confer Rifampicin Resistance Can Alter Levels of Peptidoglycan Precursors and Affect β-Lactam Susceptibility

**Yesha Patel, Vijay Soni, Kyu Y. Rhee and John D. Helmann, 2023.** Published journal article, *mBio* 14(2):e03168-22. [DOI](https://doi.org/10.1128/mbio.03168-22), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10128067/), [bibliographic record](https://pubmed.ncbi.nlm.nih.gov/36779708/). Tables/figures and article supplements are identified; no independent code archive was verified.

Under the studied rifampicin/cefuroxime conditions, S487L differs strongly from H482Y and Q469R in β-lactam susceptibility and cellular precursor physiology. Those findings are specific to the tested strains and exposures, not a universal ranking of rpoB routes.

**TMD opportunity:** use allele-specific physiological outcomes as measurable F-side candidates and test whether the route ranking changes across exposure contexts. **Challenge:** the results do not directly explain S487 enrichment in SMMAsn and do not establish an Asn-transport mechanism. Primary indexed abstract/results and bibliographic record were inspected; full-text open returned an access challenge.

### 10. A mutation in RNA polymerase imparts resistance to β-lactams by preventing dysregulation of amino acid and nucleotide metabolism

**Yesha Patel and John D. Helmann, 2025.** Published journal article, *Cell Reports* 44(2):115268; online 4 February 2025. [DOI](https://doi.org/10.1016/j.celrep.2025.115268), [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11975431/), [bibliographic record](https://pubmed.ncbi.nlm.nih.gov/39908144/). Article figures, STAR Methods and supplements provide identified assay resources; a distinct data/code repository and reuse license were not verified here.

The authors compare B. subtilis rpoC G1122D with rpoB H482Y and connect altered β-lactam responses with amino-acid and pyrimidine metabolism. It supplies measured physiological alternatives to an unspecified establishment factor.

**TMD opportunity:** prioritize defined metabolic/fitness readouts when evaluating rpoB routes, and retain genetic background as a model variable. **Challenge:** the rpoC phenotype cannot be transferred to H482R/S487L or to Asn-limited culture without new evidence. Primary indexed abstract and detailed methods were inspected; full-text open returned an access challenge.

## Ready data opportunity: the mbamta source archive

The directly observed repository archive link is [Gitschlag_et_al_2025_SOURCE_DATA.zip](https://github.com/bgitschlag/mbamta/blob/main/Gitschlag_et_al_2025_SOURCE_DATA.zip). The [README](https://github.com/bgitschlag/mbamta) identifies the data structure below. It also displays a CC0-1.0 repository license. Public availability and license identification were verified; the binary archive was not downloaded by this literature subtask. Cache-miss responses from the web reader are not evidence that the data are unavailable to a normal download.

| Input | Role in a conservative audit |
| --- | --- |
| `SOURCE_DATA/species_list_and_mutation_counts.csv` | Taxon list and source mutation-measurement sample sizes |
| `SOURCE_DATA/mutation_spectra.csv` | Independently sourced mutation spectrum, described as GC-weighted and normalized |
| `SOURCE_DATA/codon_use/{species}.csv` | Species-specific opportunity weights |
| `SOURCE_DATA/adaptive_changes/adaptive_csv/{species}_adaptive_changes.csv` | Adaptive substitutions and raw counts |

An audit should pin the repository commit or archive checksum; retain original data; distinguish event counts from distinct mutation paths; inspect aggregation and species-source citations; and preserve the authors' derivation of GC and codon weighting. Do not double-correct the mutation spectrum. Compare equal-type, mutation-spectrum-only, codon-weighted, and estimated mutation-bias-exponent baselines with sensitivity to small taxa and concentrated event counts. This is a computational robustness exercise using external data, not evidence of a TMD-specific biological breakthrough.

For public redistribution, keep attribution and provenance even under CC0, inspect third-party inputs' original terms, and present the underlying paper as a preprint. Publication of an audit should contain its own script and conclusions rather than claiming ownership of source experiments. The manuscript and repository license categories differ and must not be interchanged.

## Concrete TMD model improvements motivated by these papers

The following are proposed TMD analyses, not claims made by the cited authors.

1. **Use a baseline hierarchy.** Lock a uniform comparator, mutation-class/codon comparator, local-sequence comparator, and independently measured route-rate comparator. A claimed residual should survive plausible supply models. The independent hotspot literature motivates the local-sequence level; it does not supply every route rate.
2. **Make q uncertainty visible.** Estimate route supply with uncertainty rather than attaching exact numbers to a small unselected panel. Propagate that uncertainty through the shared-tilt and WS tests. A fixed-axis curve tested with fitted q from the same selected outcomes risks circularity.
3. **Separate count meanings.** Label a row as a first-arrival route, selected isolate, dominant endpoint, or adaptive substitution. Tie each to its actual likelihood/sampling rule. Establishment inference needs independent competition/recovery data or explicit assumptions.
4. **Audit the WS triad conditionally.** Add an `Other` category and report its count/unknown status. For contexts with the same q, the shared-K curve is restrictive. If independently measured q differs, test the baseline-adjusted contrast rather than forcing a raw common K:

   \[
   D_c=\log\!\frac{p_{c,A}^2}{p_{c,W}p_{c,M}}-\log\!\frac{q_{c,A}^2}{q_{c,W}q_{c,M}}=2\theta_1.
   \]

   This is an algebraic restatement of the supplied TMD model for positive triad probabilities, not newly discovered mathematics. Invariance of D across future contexts remains an empirical hypothesis; zero counts require likelihood treatment rather than infinite plug-in logs. Conditioning on the triad does not establish that the triad is exhaustive.
5. **Challenge constant establishment.** Analyze background-by-route and environment-by-route terms, and evaluate an entire held-out context. The epistasis and physiology papers make clear why a shared coefficient can fail. Endpoint counts cannot determine absolute successful-arrival rates.
6. **Run the new rpoB data through an admissibility gate.** Before Table S6 enters the main panel, recover assay details, route denominators and independence. A repair/MMS panel can be an external context challenge after these checks. It is not directly an LB/SMMAsn replication.

## Evidence boundary and priority

The strongest near-term priority is **one reproducible baseline audit plus a prespecified external test**, with explicit negative outcomes allowed. A strengthened mutation baseline may reduce TMD's reported residual. That would be useful progress: it identifies what remains to explain and avoids claiming novelty for already measured supply effects. The most valuable possible TMD contribution is prospectively predicting held-out route distributions with a narrowly defined, falsifiable correction and calibrated uncertainty. None of the reviewed papers proves that correction, supplies a quantum mechanism for it, or connects TMD to a unified theory of physics.

## Source/data update — 7 October 2026

The [authenticated SBW25 figure-data audit](research/sbw25_data_audit/README.md) reproduces published source arithmetic while retaining sampling, sequencing and native/reporter transfer gaps. Its [methods assessment](research/sbw25_data_audit/METHODS_RECOMMENDATION.md) reads Foster 2006 in full and Hall 2009 at abstract/metadata depth only; HTTP200 browser-check HTML is not full-text access. A separate [bounded new-index watch](research/source_watch/2026-10-07/README.md) reads two October 2026 abstracts, with exact indexing/publication distinctions. Neither is a systematic review, an independent new cohort or TMD validation.

## 7 October follow-up: observation models and allele origin

The [R7 methods package](research/fluctuation_contract/README.md) rereads Farr et al.'s final fluctuation Methods and the supplied culture records. It derives nominal partial-plating geometry and checks established clone/thinning mathematics against Foster (2006), DOI 10.1016/S0076-6879(05)09012-9, Equation 5. Final article statements, review-history text and unread author-response attachments stay distinct. This is a targeted source/method assessment, not an original fluctuation experiment or author-rate replication.

The [R8 primary assessment](research/recombination_scope/README.md) reads Payne et al., *Herd immunity underlies homologous recombination in stationary phase bacteria*, DOI 10.1093/molbev/msag238, electronically published 3 October 2026. The engineered E. coli MG1655/P1vir system distinguishes recombinant and mutant CFUs with resistant fluorescent marker cassettes. Source interventions support assay-specific transfer; clone growth, recovery, maintenance antibiotics, genetic backgrounds and repeated-culture measurements bound the interpretation. The reported approximately 380-fold 24-hour contrast is an abundance contrast, not independently enumerated molecular event rates. Supplements, author models and raw data are unacquired; no numerical parameter is transferred to native SBW25. The primary text is CC BY-NC 4.0 and remains external; public notes are original attributed commentary.

The [R9 input audit](research/source_input_authentication/README.md) reuses the same article/archive and distinguishes its final software declaration from the historical submission. Four new bounded software/metadata paths returned CONNECT403 or HTTP404; no software artifact, new author-response body or historical input report was acquired. This scoped access result is not a claim that those materials do not exist. The [R10 paired-sampling package](research/paired_aliquot/README.md) derives classical PGF/marking consequences from explicitly stated observation laws; it adds no independent biological cohort, literature discovery or new theorem.

## Absolute recovery and sampling units — 7 October 2026

The [R12 source assessment](research/recovery_calibration_sources/README.md) uses one targeted PubMed query:45 matches, eight newest metadata/abstract candidates, two selected primary main-text methods/results and one newest abstract-only lead. Four public GETs acquired506,673 bytes. This is a bounded source screen, not a systematic review or another occurrence of the already completed daily watch.

[DOI10.1128/spectrum.03910-25](https://doi.org/10.1128/spectrum.03910-25), PMC13228076, compares72 clinical specimens in paired processing conditions. Bead-normalized membrane-integrity events and recovered colonies are different units. The reported marginal CFU median ratio550 is not a paired fold-change estimate, recovery probability or mutation-rate ratio. Below-quantification exclusions leave different cross-method denominators69/71; the volume/concentration/low-count mapping remains unresolved without the declared, unacquired DOCX Data set S1. P=.470 is not evidence of equivalence, and an operational cytometry gate does not confirm VBNC.

[DOI10.1007/s00203-026-04995-3](https://doi.org/10.1007/s00203-026-04995-3), PMC13272224, provides PA14 persistence, redox/membrane gates and post-antibiotic regrowth comparisons. Approximate OD/CFU inocula, variable technical event acquisition and outgrown descendants do not establish independently introduced single cells or mutation-origin lineages. Neither primary cohort is a common-background Wsp/Aws/Mws panel.

[NanoSpacer DOI10.1039/d6lc00655h](https://doi.org/10.1039/d6lc00655h), PMID42831674, electronic date5 October2026, remains abstract-only. Relative fluorescent-mixture agreement across microscopy, flow and CFUs does not establish absolute capture. Full text, raw observations and biological replicate denominators remain unacquired. The two inspected PMC sources declare CC BY4.0; original ledgers and source pins are public, while source bodies and clinical raw files remain external.

The [R13 calibration mathematics](research/capture_calibration/README.md) uses standard binomial inversion and Poisson marking. It specifies the positive-mark, known-capture, full-population-law conditions under which one ambiguity disappears, and preserves unknown-capture and invisible-lineage alternatives. It adds no independent biological cohort, new theorem or fitted mutation rate.

## Cancer-domain source assessment and normalization — 7 October 2026

[R15](research/cancer_translation/README.md) uses one targeted, relevance-ranked PubMed query:160hits,12metadata/abstract candidates and two foundational primary main texts. These are2018/2021 sources, not newly discovered2026 cancer breakthroughs or a systematic review. Martincorena et al., DOI10.1126/science.aau3879, maps844normal-esophagus samples in9donors; detailed MethodsS1–S7 and raw/supplementary data remain unacquired. Colom et al., DOI10.1038/s41586-021-03965-7, supplies mouse competition observations and perturbations, with nested animal units, separate simulations and analogous human micro-tumor elimination explicitly unknown. XML licenses allow text mining, not CC redistribution; source bodies remain external. Cancer-associated clone prevalence is not a malignancy or prevention endpoint. Neither validates TMD.

[R14](research/normalization_audit/README.md) reuses the two R12 clinical/PA14 primary texts. Four new supplement/package URLs return404HTML, CONNECT403,404HTML and200reCAPTCHA; no raw DOCX or clinical table is read. Exact original arithmetic demonstrates conditional reporting alternatives, not the source's authenticated calculation. Reassessment is not a new cohort. Source/clinical failure responses stay external; public notes and provenance hashes are original attributed commentary.

## Observed epithelial pedigrees — 7 October 2026

[R16](research/epithelial_lineage/README.md) assesses Brody et al.2018, DOI10.1101/gr.238543.118, PMC6280753. A newest-first targeted PubMed query returned18hits;12metadata/abstract records were screened and6were not. The older selected experiment directly observes divisions and reports isolation/outgrowth/sequencing losses. All80main paragraphs were inspected by the producer, with20cached anchors and independent source/stage review. This is a bounded source assessment, not a systematic review or new2026biological discovery.

HT115 and RPE1 differ in tissue, genome, ploidy and medium. Source mutation calls, correlated lesions, related descendants and divisions have different denominators. Consensus-conditioned caller sensitivity is not known-input recovery. The public software commitbcfe5a6c1a1407306b1c8b82e423de124e7a9f9e and six-file tree/README were identified without running Python2.7 notebooks or downloading mutationZIPs/reads. ArticleCCBY4.0 does not establish software/archive licensing. No matched cancer panel or TMD confirmation follows.

[R18](research/curvature_bounds/README.md) derives standard interval/continuity consequences for a hypothetical expected-mass factorization. It performs no new source search, biological fit or mathematical-priority assessment.

## Recent ancestry method and pedigree contract — 7 October 2026

[R19](research/pedigree_contract/README.md) retains the observed Brody 2018 pedigree architecture and adds a qualified-review packet. A narrow 2024–2026 PubMed query returned two metadata/abstract records. Yu et al. (2025), MitoTracer, DOI10.1371/journal.pcbi.1013090/PMC12184895, was selected for a recent lineage-method assessment. Root read 50 body paragraphs; another agent independently read and checked 12 anchors. Retrospective mitochondrial marker reconstruction, selected clone benchmarks, planted simulation data and exploratory drug-resistance associations remain distinct. No source software, display-equation or raw-data calculation was replayed. A 2024 mutation-rate-evolution review was assessed at abstract depth only.

[The source receipt](research/pedigree_contract/RECENT_METHODS_REVIEW.json) records the narrow scope, licenses, identities, source reporting ambiguities and paragraph numbering. Four new source requests retrieved 220,395 bytes, including Crossref metadata for the established Horvitz–Thompson 1952 reference. That historical primary text was not read. No broader literature or novelty claim follows.

## Native origin controls and caller support — 7 October 2026

The bounded R21 search made eight requests totaling 925,380 response bytes and screened 14 returned abstracts. Three cached primary articles were assessed: all 56 main-body paragraphs each for PTA and NNK, and 25 selected PTATO paragraphs plus a short lead scan. [Source review and hashes](research/native_origin_controls/SOURCE_REVIEW.json) preserve those depths; raw article/abstract bodies, source code, supplements and patient reads are excluded. These searches are not a claim of literature completeness.

- *Accurate genomic variant detection in single cells with primary template-directed amplification* (2021), DOI [10.1073/pnas.2024176118](https://doi.org/10.1073/pnas.2024176118): >90% bulk-conditioned sensitivity and 99.9% germline precision do not measure de novo-origin inclusion. Kindred cells were expanded for five days; viable/recovered genomes do not enumerate all births. The mutagenicity caller's unique-single-cell/bulk-absence rule differs from a multiple-support branch caller.
- *Comprehensive single-cell genome analysis at nucleotide resolution using the PTA Analysis Toolbox* (2023), DOI [10.1016/j.xgen.2023.100389](https://doi.org/10.1016/j.xgen.2023.100389): 45–69% recovery of shared substitutions differs from 86.8% sensitivity conditional on detectable true variants in callable loci. Some artifact truth is signature-refit estimated; reused ENU data are not an independent experiment. Reference, recurrence, quality and sample-adaptive rules require a frozen, validated complete algorithm.
- *Differential Mutagenic Response of Rat Liver and Lung to Nicotine-Derived Nitrosamine Ketone (NNK)* (2026), DOI [10.1021/acs.chemrestox.6c00154](https://doi.org/10.1021/acs.chemrestox.6c00154): six animals were dosed and the first five assayed per group, with the sixth reserved. The two methods use the same animals/DNA and a 20-target, 48-kb panel (13 intergenic/7 genic regions). Concordance does not establish independent truth. Reported dose-grid NOGEL is not proof of zero biological hazard or a medical-prevention threshold. Exposure, adduct and repair/metabolic explanations remain unmeasured in this study; the paragraph-34 dose wording discrepancy is preserved.

[Independent inspection receipts](research/native_origin_controls/review/README.md) retain narrower reviewer depths separately. No source supplies actual matched TMD catalogs, mutation-origin/control transport, independent episode trials or an admitted inference law.

## PTATO official-artifact inspection — 8 October 2026

[R23](research/artifact_admission/README.md) reuses the same PTATO 2023 primary source and inspects its official tool v.1.2.4 and figure-analysis v1.0.1 release pointers. The acquired figure-code ZIP and selected tool blobs expose concrete conditional-label, denominator and missingness checks. EGA/Mendeley biological manifests and authentic Table S2 remain unacquired; CAPTCHA HTML is not a workbook. This is a bounded source/software assessment, not a new cohort, complete pipeline replay or admitted variant/origin benchmark. No parameter is transported into the actual TMD registry.

## R24 current-source note — 8 October 2026

Park and Krug's [*Mutation-biased adaptation: The Yampolsky–Stoltzfus model revisited*](https://doi.org/10.64898/2026.10.05.756661), version posted 7 October 2026, is an unreviewed analytical preprint. [The original assessment](research/source_watch/2026-10-08/README.md) inspects a provider-parsed 14-page representation while excluding graph-derived tables and unverified formula replay. Continuing mutation and clonal interference separate first establishment from eventual fixation. Its extension to more than two alternatives supplies the least-fit marginal, not a general complete Wsp/Aws/Mws vector. This strengthens a concrete conventional-comparator question without filling native parameters or validating TMD.

The bounded search reidentifies Barber and Couce's 2026 study already assessed in R4; no additional cohort is counted. The [PTATO processed-metadata audit](research/processed_metadata/README.md) independently authenticates the author-recorded training and clone/day input structure in two exact files; caller-derived variant truth remains separate from independent acquisition-episode truth. These original notes add no copied full text, source figures, clinical table or new biological experiment.

## PTATO scoped source and denominator audit — R25, 8 October 2026

The [scoped input audit](research/processed_input_audit/README.md) reuses the same 2023 PTATO evidence family and authenticates new official folder/file metadata and three small source summaries. It adds no cohort, variant/locus replay or independent origin truth. The [code-denominator contract](research/genotype_denominators/README.md) develops the earlier global-membership caution into standard set/mean identities and constructed checks, with exact source anchors and unknown actual numerical effects. The R24 recent preprint assessment remains separate; no new paper search or uninspected physics mechanism is counted as evidence.

## R26 targeted bacterial source assessment — 8 October 2026

Karita et al.'s [Context-dependent adaptation in structured environments](https://doi.org/10.1098/rspb.2025.2004) provides observed pre-endpoint ecology and named wspF/awsX/mwsR colonization measurements. Its preprint and [2025 dataset](https://doi.org/10.5281/zenodo.15735347) are the same source family, with explicit dataset CC BY 4.0. Two exact small workbooks are authenticated; their colony categories and surface units do not fill independent route supply, acquisition-episode truth, lost-lineage or phase-specific control requirements. The [original assessment](research/bacterial_panel_leads/REPORT.md) preserves selected primary anchors and source arithmetic, without a new model fit.

Matela et al. [10.1128/aem.02499-25](https://doi.org/10.1128/aem.02499-25) reports 69 selected clones from 54 historical populations, with phenotype ascertainment, relatedness and differing ancestors. Those observations cannot be joined to the Karita collection as a matched experiment. The article's reuse terms and the separate supplement-rights notice are retained. This two-search/two-primary assessment is bounded; other hits remain metadata/excerpt leads. The [PTATO truth decision](research/benchmark_decision/README.md) reuses cached2023source material with zero new acquisitions, and parks numerical accuracy/origin benchmarking.
