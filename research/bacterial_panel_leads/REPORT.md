# A licensed SBW25 ecological lead, with authenticated endpoint counts

R26 · 8 October 2026, America/Los_Angeles · Original source assessment and exploratory source arithmetic

Acquisition timestamps and search bounds retain their actual 9 October UTC values in the provenance ledger.

**Decision: pursue Karita et al.'s ecological measurements as a practical panel-design lead; no complete matched Wsp/Aws/Mws panel is admitted.** The 2026 paper, [*Context-dependent adaptation in structured environments*](https://doi.org/10.1098/rspb.2025.2004), supplies a concrete reason to measure ancestral facilitation, spatial retention and competition before declaring an endpoint winner. Its [versioned Zenodo dataset](https://doi.org/10.5281/zenodo.15735347) is explicitly CC BY 4.0. We authenticate two small author workbooks: endpoint colony categories and early surface occupancy for named genotypes. These are published observations reused for exploratory assessment, not a new independent experiment or TMD confirmation.

The alternative contemporary primary lead, [Matela et al. (2026)](https://doi.org/10.1128/aem.02499-25), provides actual Wsp/Aws/Mws-related genotypes and a useful warning about colony ascertainment, but has heterogeneous historical collections and a different bead-transfer ecology. Its samples cannot fill the selected lead's missing route/control cells. The two studies should not be joined into a synthetic matched experiment.

## What the selected source measures

Karita et al. use SBW25 in King's B medium at 28 °C, with a representative **wspF** WS strain for the mat/rescue assays. The early surface-occupation comparison also includes **awsX** and **mwsR** mutants; these additional genotypes are explicitly reported in the primary Results and have named sheets in the acquired surface workbook. Their Methods and figures distinguish experiments: low-inoculum mat success at 24 hours, introduced SM/WS imaging, a c-di-GMP reporter experiment followed for six days, and a two-colour ancestral mixture scored for colony morphology after six days. They report five evolution lines with more than 140 scored colonies each in Figure 6. Those colonies are descendants sampled from lines, not five times as many independent mutation origins as colonies.

The source reports 2 successful mats among 9 WS/SM co-cultures versus 0 among 15 WS monocultures in its rescue comparison. These are whole-well mat outcomes at specified cell densities, not known single-lineage W/A/M establishment trials or phase-specific correct-recovery controls. The present assessment does not replay the paper's interval calculation or treat that small comparison as decisive evidence by itself. Figure 3 time-lapse measurements and Methods describe pre-endpoint dynamics; Figure 6 classifies endpoint colour and morphology. Neither is a molecular, time-resolved census of Wsp, Aws and Mws mutation births.

The c-di-GMP reporter indicates a physiological state; colour marks the ancestral tag; colony shape identifies a morphotype. None uniquely names a mutational route or dates a mutation. The authors explicitly note that different genotypes can share morphology and propose deep sequencing/barcoding for further resolution. Detected microcolony collapse is relevant to loss mechanisms, but without pre-loss genotypes and detection calibration it cannot enumerate lost mutant origins. A smooth ancestral phenotype likewise does not establish molecular absence of pre-existing eligible variants.

The paper's four-state conventional model separates SM/WS and bulk/interface populations. It motivates an ecological comparator, but supplies neither every W/A/M outcome probability nor independently measured target-context mutation supply. The approximately 1.1 × 10^-8 rate is cited from prior work; reacquiring it here is not a new matched calibration. No source parameter, eta rule, model fit or new forecast is selected in R26.

## Exact workbook and the unit that can be counted

The official record lists `SM-mixevo_count_2024_10_02.xlsx`, **9,925 bytes**, MD5 `445db9f6f795ea98a256bdb09e370446`. The acquired binary matches both fields; its SHA-256 is `142bf3ea4a873b2f8ae493a0832fce12ea6bb935a1eca8b3c3be4f93a3d38d23`. It has one sheet, **Tabelle1**. The original workbook, parser responses and author workstation metadata remain outside Git; only the attributed derived audit and receipts are published.

The sheet contains 57 literal count cells: 55 positive values and two observed zeros. Eight additional summary cells for line 1 are retained separately and never counted again. All eight equal their corresponding literal sums; only three contain formula text: I3 = C3+C7+C11 = 56, K3 = E3+E7+E11 = 30, and I4 = C4+C8+C12 = 79. The other five are literal constants. No spreadsheet formula or external code was executed.

| Source line group | Sum of standard red/green wheel, large, small and SM cells | Separate Dark wheel count | Sum including that separate category |
| --- | ---: | ---: | ---: |
| 1 | 297 | — | 297 |
| 2 | 155 | — | 155 |
| 3 | 188 | — | 188 |
| 4 | 166 | 21 | 187 |
| 5 | 187 | — | 187 |
| Literal total | 993 | 21 | 1,014 |

These are **arithmetic sums of sampled-colony entries**, with no dilution correction or claim of a complete population denominator. The dash means that no separate Dark wheel entry is recorded, not a measured zero. In line 4, B30 is `Dark wheel` and C30 is 21 in the red count column; the corresponding E30 cell is absent. Its fluorescence/phenotype interpretation needs adjudication before inclusion in any normalized category vector. E30 remains missing, not zero. The note “No FS was observed in these 5 lines.” remains a source statement, without manufacturing numeric FS counts or molecular-negative controls.

Line 1 retains the raw labels `1-7-1,1-7-2`, `1-6-1,` and `1-6-2,`, plus the source summary label `1-7, 1-6`. The paper describes plating at two dilution levels, but the workbook does not independently define the suffixes. Their interpretation as plate/dilution identifiers is not authenticated here; they must not become separate independent lines, fixed-day labels or automatic sample weights. At the line-group arithmetic level, all six standard WS colour/morphology classes have positive counts in every group. That supports the source's descriptive morphotype-coexistence account, without identifying six molecular routes, independent mutation births or fixation.

## Genotype-labelled surface data sharpen the control requirement

`Surface_density_data.xlsx` is **15,773 bytes** and matches official MD5 `6595f2b6bb05e827ec1f434f4b89a6fa`; SHA-256 is `5802bfb537f94b60de3a03d5f83e4fe7b94a2af8a9c32e2deb1b030939f138a0`. Its seven sheets are SM, SM-Dwss, SM-DfliA, mwsR, awsX, wspF and wspF-DfliA. Worksheet relationship mapping is preserved: workbook sheet IDs alone do not determine archive member order.

The [surface audit](SURFACE_DENSITY_AUDIT.json) retains **25 declared dilution groups, 24 populated groups and 200 positive numeric image-count entries**. The mwsR row with dilution factor 100 has no recorded area or counts; it is missing, not zero. All 21 cached arithmetic formulas agree with independently calculated exact rational values. The check uses a restricted arithmetic parser, not spreadsheet execution.

The columns specify saturated density measured by plating in cells/mL, dilution factor, ROI area in µm² and repeated image counts. The nominal inoculum density is the stated saturated density divided by dilution; surface density is count divided by ROI area. Their ratio has units mL/µm² under those stored units. It is a dimensional occupation measure, not a binary establishment or recovery probability. Raw plating counts, independent cell-number calibration and image-to-well/culture links are not supplied by these sheet headings.

The source date labels further matter: mwsR and awsX carry `2024-0326`, wspF carries `2023-0526`, and SM carries `2023-0602`. These are genotype-labelled assay records, not authenticated matched contemporaneous batches. The two-hour measurement time comes from the primary Methods, not an independent time field in the workbook. Repeated count columns cannot be assigned independent culture denominators without the experimental map.

The concrete lesson is that future establishment controls must match **inoculum density, resident ancestral scaffold state and timing**, as well as route and genetic background. An introduced mutant in an empty interface and a mutant emerging within an established ancestral mat may have different opportunities to persist. The source makes this a candidate control-design requirement; it does not select an actual protocol, establish a probability of mutation origin, or supply a new frozen forecast.

## Why the alternate lead does not repair the panel

Matela et al.'s main primary text reports **69 phenotype-selected clones from 54 populations**: 3/1 from Allderdice, 22/10 from SciTech, 40/39 from Winnacunnet and 4/4 from university labs. The source explicitly says the frequencies are skewed toward populations with visibly new morphologies and cautions that some repeated mutations from the same school/year may not be independent. Historical collections include 2015, 2017, 2018 and 2019; publication in 2026 does not make them prospective 2026 outcomes. The article distinguishes shared ancestral reference differences and extra WHS-2015 deletions, alongside different durations, temperatures, agitation and triclosan use. Those distinctions block a pooled common-background W/A/M race.

Its separate longitudinal experiment has four lines per treatment, population sequencing on days 3 and 15, and daily bead transfers. Its introduced competition uses bmo, wspF, fuzY and a marked ancestor, not the full W/A/M triad. Smooth-looking bmo adaptations make it especially unsafe to define genotype absence by ancestral morphology. These findings sharpen alternative ecological and observation explanations. The main article is CC BY 4.0, but its supplemental notice states separate reuse terms; the supplemental workbooks and BioProject PRJNA1284392 were not acquired or granted a blanket article license in this audit.

## The next concrete acquisition and analysis decision

The [admission matrix](ADMISSION_MATRIX.json) records each supplied measurement, missing field and permitted inference. The [acquisition plan](ACQUISITION_PLAN.json) preserves all 14 official Zenodo file entries with exact sizes, MD5 values and URLs, and names the next small artifacts. No whole archive, microscopy collection, movies or raw reads are required to inspect the colony/mat-control tables.

The next bounded step is to authenticate the 8,831-byte `Pellicle_success.xlsx` and 9,458-byte reporter workbook, then obtain the published supplementary strain table/protocol with its own manifest, version and license. First resolve the raw plate/dilution map, `Dark wheel` class, starting genotypes, reporter/marker controls, and which source experiments actually share a sampling frame. Additional arithmetic is warranted only if those records answer a panel-admission question. Data-file identity alone cannot supply unmeasured genetics, independent ancestry, mutation opportunity, losses or recovery.

For a complete test, require one documented ancestral background with all focal routes available, an allele registry including Other/compound/ambiguous categories, context-matched independent supply measurements, and molecularly linked pre-endpoint trajectories. Preserve inherited/pre-existing true variants as origin-negative controls, independently established acquisition episodes, unobserved/lost-lineage limits, and introduced/recovered controls in each route × baseline/selected phase. A birth census, descendant census and successful endpoint census must remain separate. These are acquisition requirements for a qualified biological/statistical assessment, not a newly selected laboratory protocol.

The conventional forecast must predict the complete same observed-category vector from admitted supply, demographic, fitness, spatial/facilitation and observation inputs. Freeze it before independent held-out endpoints, including the chosen treatment of Other/no-outcome and how route aggregation is justified. Report any inability to populate this contract rather than obtaining W/A/M probabilities by renaming colour or morphology. Existing forecast, context/eta, count-law, error allocation and fixed-stopping rules stay unchanged. All 26 actual study inputs and 18 native-control planning fields remain NULL; R5/R11/R17 blockers remain in force.

## Scope and verification

Two bounded searches returned six paper-index records and eight web hits; two passage requests returned no indexed full text. Two primary HTML sources and one official dataset page/API were then inspected. Eleven scientific acquisition attempts are recorded, including the failed default-sandbox binary request and a successful repeat after explicit network permission enabled access to the inherited proxy. No proxy, CA or TLS verification setting was bypassed. This is a focused search and primary-method assessment, not an entire-web or systematic review.

Preprint 10.1101/2025.04.29.651346, the 2025 deposited data and journal article 10.1098/rspb.2025.2004 form one evidence family. Lind 2019 and Sun 2023 remain the previously identified reused source family; no repeat of those old failed workbook endpoints was made. Other search hits remain metadata/excerpt leads. No local D-Blast archive scan was needed or performed in this branch. No outreach, experiment, mathematical priority, cancer-prevention result or biological validation is claimed. This addendum does not alter the immutable methods 0.6.0 archive.

Run the standard-library checker without source downloads or writes:

```sh
python -B research/bacterial_panel_leads/verify_sources.py --source-cache /path/to/r26-bacterial-cache
```

Without a cache it explicitly reports source replay as UNRUN and checks public invariants only. [The saved receipt](VERIFICATION_RECEIPT.json) records the full executed source replay. Checks authenticate acquired representations and literal source arithmetic; they do not authenticate independent mutation truth or scientific causation. Independent internal AI-assisted review remains distinct from qualified external assessment.

Original commentary and attributed derived audit: CC BY 4.0. New verification code: MIT. Source authors retain their rights. Prepared by Ricardo Maldonado with AI assistance.
