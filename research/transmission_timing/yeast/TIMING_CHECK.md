# A single omitted visit reverses a retrospective persistence call

Johnson et al. sequenced 90 focal populations of budding yeast at six visits. This check uses the 18 initially haploid focal populations in the YPD 30°C environment. It reads the original roster directly from workbook XML and the population tables from the original ZIP. We restricted the analysis to the authors’ five small-variant classes on the 16 nuclear chromosomes, excluded flagged telomeric sites, required at least five alternate reads summed over the well and required either of the authors’ two cross-time discovery filters. The resulting panel contains 5,759 records grouped into 5,543 author-defined events. A group of nearby calls is a putative mutation event. Co-detected groups can occur in the same cells. [Primary study and Methods](https://doi.org/10.7554/eLife.63910) · [Well roster](https://cdn.elifesciences.org/articles/63910/elife-63910-supp1-v2.xlsx) · [Processed observations](https://cdn.elifesciences.org/articles/63910/elife-63910-supp2-v2.zip)

At a local visit a call qualifies when the total read depth is at least five and the alternate fraction reaches the stated threshold. The source’s fixed call in initially haploid wells requires at least 90% at a qualifying visit and no later adequately measured fall below 90%. Subsequent low-depth visits can retain that call. For group-level reporting we take the earliest qualifying record within each group, then retain every group tying for first within its well.

The paper describes a local 10% rule for presence. The pinned code defines a function for this rule but calls its fixation function with a 10% threshold when populating the published presence field. That field requires at least 10% at the current adequate visit with no adequately measured later decline below 10%, or an already active 90% fixation call at the preceding visit. Reconstructing the two published flag fields from the underlying reference and alternate counts reproduced **all 34,554 site–visit pairs for each field**. Compared with a strictly local 10% measure, 1,372 observations passed locally but lacked the source presence flag and 447 were flagged despite failing the local rule. These counts share records and wells. They describe two definitions applied to the same measurements. [Archived implementation](https://github.com/mjohnson11/VLTE_PIPELINES/blob/588043a94abb34b13a6dd7a1b25277c25ae8deaf/WGS/process_files_and_run_go.py#L436-L445) · [Functions that implement the two rules](https://github.com/mjohnson11/VLTE_PIPELINES/blob/588043a94abb34b13a6dd7a1b25277c25ae8deaf/WGS/process_files_and_run_go.py#L223-L261)

| First observed endpoint in each well | Generation 70 | Generation 1,410 | Wells with tied event groups | Wells with tied event classes |
|---|---:|---:|---:|---:|
| Local ≥10% | 17 | 1 | 16 | 16 |
| Source presence flag | 17 | 1 | 14 | 13 |
| Local ≥90% | 15 | 3 | 12 | 11 |
| Source fixation flag | 14 | 4 | 10 | 9 |

For the two 10% definitions, the first visit was identical in every well while the membership of the group tie changed in 14 wells. The set of functional classes changed in nine. Removing P1B03, which the authors report underwent autodiploidization, leaves 17 initial haploid wells with 5,326 records in 5,115 groups. The source presence and local 10% rules still differ in 1,604 of 31,956 site–visit entries. Their earliest group sets differ in 13 of the 17 wells. [Independent calculation](verify_visits.py) · [Per-well results and sensitivity](verify_result.json)

## What the read counts show in P1E11

| Source event group and class | Generation 70 | 1,410 | 2,640 | 5,150 | 7,530 | 10,150 |
|---|---:|---:|---:|---:|---:|---:|
| 145, missense | 33/36 | 20/20 | 22/22 | 5/6 | 26/26 | 17/17 |
| 55, synonymous | 0/36 | 12/13 | 31/32 | 9/9 | 19/20 | 10/10 |

Entries are alternate reads over total reads. The first local 90% event in this well is group 145 at generation 70. Its 5/6 reading at generation 5,150 falls below 90%. The first event satisfying the retrospective persistence rule becomes group 55 at generation 1,410. If the generation 5,150 visit is omitted from the entire well, group 145 at generation 70 wins that same persistence comparison. Its identity and time both change. Reading support at that visit consists of only six observations. No cell lineage abundance or sequence error probability has been estimated from the six reads.

Removing each of the four interior visits one at a time gives 72 overlapping comparisons across 18 wells. With the same full-data catalogue and event groups, the first persistent 90% visit is unchanged in 67 comparisons, later in four, and earlier in one. The P1E11 instance is the only earlier time and the only case where the full-grid and reduced-grid earliest persistent group sets have no common member. This is a sensitivity to observing fewer visits conditional on the discovered panel. It does not reproduce the discovery process that a genuinely sparser study would have had.

## Limits on first crossing

A readout passing an abundance threshold at a sampled time gives an exact visit for that readout. The first visit is generation 70, so some markers already qualify when observation begins. With exact latent fractions and a continuous path, a subthreshold level followed by an above-threshold level implies an upward crossing between the two observations. Earlier unobserved excursions can make it a subsequent crossing. A mutation birth, its establishment and its first appearance in an assay have separate meanings. Rising markers can hitchhike, different classes can tie, and the selected sites and persistence criterion use later observations. The records do not identify a first successful causal mutation route.

An explicit bound illustrates what additional calibration could buy. Suppose a latent fraction is known to change at most L per generation and its exact values a and b at two sampled endpoints are below a threshold q. Over an interval of length Δ, a hidden crossing is feasible precisely when LΔ ≥ 2q − a − b, assuming the endpoint values themselves satisfy the speed bound. Necessity follows from the distances q − a and q − b that a crossing must traverse. A piecewise-linear rise to q followed by a fall to b attains the bound. This is a sensitivity result derived from a triangle inequality. The source provides no verified speed limit or exact latent fractions, so it yields no empirical exclusion of earlier crossings here. The TMD project’s pre-existing first-arrival diagnostic likewise requires a justified time origin and recorded first arrivals. [Earlier TMD formulation](https://github.com/maldonado-research/TMD/blob/f14d1a086dac09f1f884a40743a75b40295f3df3/research/FORMULATION_AND_NEXT_EMPIRICAL_TEST.md)

## Reproduce the original-file check

Use Python 3.10 or later with the two native source files. The verifier uses the standard library and checks both source file hashes.

```sh
python3 -B verify_visits.py elife-63910-supp1-v2.xlsx elife-63910-supp2-v2.zip | diff - verify_result.json
```
