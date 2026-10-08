# R000019: pedigree exposure and event ascertainment

**7 October 2026 · Original prospective contract and SYNTHETIC ledger**

This work specifies records needed to distinguish observed cell divisions, molecular-origin hypotheses, inherited variant copies, and genotype ascertainment. It uses the cached Brody et al. (2018) primary study and existing public TMD design contracts. No actual system, partner, route catalog, ordered axis, protocol, allocation or error plan is selected. All actual study inputs remain unresolved; no existing bacterial registry field is filled.

## Source-grounded measurement boundary

Brody et al., *Quantification of somatic mutation flow across individual cell division events by lineage sequencing*, DOI [10.1101/gr.238543.118](https://doi.org/10.1101/gr.238543.118), provides independently imaged pedigrees linked to genomes of recovered, expanded descendants. The primary article's recorded division ancestry adds exposure information that sequencing-only reconstruction cannot supply independently. Sixteen cached paragraph anchors, identifiers and the article license were verified; raw XML, movies, supplementary branch tables, reads and source software are excluded and not replayed.

The source's collection/isolation/outgrowth/sequencing counts are 45/37/11/11 for HT115 and 26/22/15/13 for RPE1. These are nested descriptive stage counts, not independent recovery controls. Available cells at collection are not every cell ever born. The 24 primary sequenced descendants belong to two displayed founder pedigrees, one per different cell-line background, rather than 24 independent cultures. HT115/RPE1 differ in genotype, tissue background, media and estimated ploidy.

Source branch variants are supported by related subclones and mapped to lineage segments. Copies inherited by two descendants are not two independently arising mutations. A variant seen in one descendant may have originated near collection, during later subclone expansion, or through technical error. Optical pedigree knowledge does not reveal the genotypes of dead, lost, unrecovered or failed-outgrowth cells.

Internal caller consistency estimates are distinct from independently calibrated cell capture. **Event inclusion** also differs from cell-stage recovery: observing a molecular-origin hypothesis may require multiple relevant surviving genomes, an informative comparison branch, adequate callability, and a valid ancestral state. An at-least-one-call capture rule cannot automatically substitute for the source's branch-caller requirements. The complete native predicate still needs qualification.

The separately acquired recent-method review is retained in **RECENT_METHODS_REVIEW.json**. Yu et al. (2025), MitoTracer, DOI [10.1371/journal.pcbi.1013090](https://doi.org/10.1371/journal.pcbi.1013090), supplies a retrospective mitochondrial marker/ancestry lead, with explicit coverage, filtering and small-clone limits. R19 independently read and checked its 12 anchored paragraphs, both narrow-search abstracts and the classical sampling bibliography metadata; root's full 50-paragraph inspection is attributed separately. MitoTracer markers are not a nuclear mutation-birth census, optical division exposure, native origin-inclusion control or cancer-prevention result. Brody anchors are zero-based; MitoTracer's corrected anchors are one-based and require subtracting one before XML indexing.

## Reviewable materials

- **REQUIREMENT_MATRIX.json** links 13 requirements to verified primary anchors, known source evidence and critical unresolved candidate inputs.
- **OBSERVATION_CONTRACT.md** specifies prospective identity, exposure, event, missingness, control and inference records.
- **EXPERT_REVIEW_PACKET.md** gives concrete questions and evidence requests for a qualified biologist/statistician before any commissioned pilot.
- **LEDGER_SCHEMA.json** is a practical table/field dictionary with cross-table relationships. It is not a general JSON-Schema validator or an admitted statistical contract.
- **SYNTHETIC_LEDGER.json** and **TOY_RULES.json** demonstrate bookkeeping using fictional identifiers, with no molecular coordinates, actual route mapping or biological system.
- **verify_contract.py** checks graph/time consistency, nested stages, explicit missing calls, inherited-carrier bookkeeping and toy origin classification. Passing does not establish experimental truth.
- **verify_recent_sources.py** independently verifies the cached recent-source identities, 12 anchors, two-hit metadata screen and bibliography-only record without reacquisition.

## The synthetic example

The toy contains 13 tracked cells, six observed division events and 20 arbitrary cell-time units. Five cells are collection-available, four isolated, three outgrown and three sequenced; one other terminal cell dies and one is lost from tracking. Four terminal genotypes are unknown.

Two assayed descendants carry TOY_VARIANT_A, while an assayed comparison branch does not. Under the locked **toy-only** rule, this supports one origin hypothesis within a tracked segment. TOY_VARIANT_B is seen in one sequenced descendant; its origin stays leaf-ambiguous. Simulation truth places two origins in the earlier pedigree, but only that explicit synthetic truth reveals the otherwise hidden history. The three alternate descendant observations do not become three mutation origins.

The toy predicate requires at least two carrier descendants, an observed noncarrier outside the assigned segment and a simulated ancestral reference. It illustrates why ascertainment must be explicit; it is neither an implementation of the source's complete caller nor a selected native protocol. Unknown targets require explicit unknown rows and cannot silently become reference calls.

## Reproduce and interpret

~~~sh
python3 -B verify_contract.py --primary-xml /path/to/authorized/cached/PMC6280753.xml --outdir /tmp/tmd_r19_contract_replay
python3 -B verify_recent_sources.py --cache-dir /path/to/authorized/recent/source/cache --output /tmp/tmd_r19_recent_source_replay.json
sha256sum -c SHA256SUMS.txt
~~~

Both commands write replay receipts outside the checkout. Keep these explicit output arguments; do not use a default-output invocation for setup or replay, since it can overwrite the packaged evidence. An omitted/missing primary cache returns **UNRUN** for source replay; it is not evidence of source failure or permission to reacquire data. Only exact nonnegative rational times are accepted. Ordinary Python is required; optimized execution is refused. The checks reconstruct descriptive exposure and stage counts and reject inconsistent ancestry, lost-cell genotypes, double-counted origins, altered locks, promoted leaf evidence and imported scientific claims. No mutation rate, inclusion probability, confidence interval or power is estimated.

Rule hashes detect byte changes; they cannot prove a rule was chosen prospectively or authenticate its author. A study needs independent dated registration/version receipts and a reviewable amendment history. Related cells, genomic reads, paired samples and common batches require explicit dependence records.

The remaining priority is qualified review of actual matched ancestry/backgrounds, molecular catalogs and episode units, source caller inclusion rules, loss-genotype observability, native controls and transfer, independent units, and a prespecified observation/error/stopping design. Ancestry reconstruction alone supplies no new TMD mechanism or cancer-prevention result.

Code is MIT; original notes and synthetic summaries are CC BY 4.0. AI assistance was used under Ricardo Maldonado's direction. No raw third-party source, patient data, private archive material or credentials are included.
