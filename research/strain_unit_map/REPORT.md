# R27: Karita strain identities and experimental-unit joins

The supplementary strain table now identifies the actual Wsp, Aws and Mws mutants in this source family. It also exposes differences in marker, deletion, medium and experimental timing that prevent the available measurements from forming one matched route-control panel. Two additional small author workbooks resolve aggregate mat-outcome and reporter-plate units. They supply neither a native mutation denominator nor a molecular crosswalk from endpoint colonies to those three strains. All 26 actual study inputs and 18 native-control planning fields remain NULL.

Karita et al.'s [journal article](https://doi.org/10.1098/rspb.2025.2004), [preprint](https://doi.org/10.1101/2025.04.29.651346), [Zenodo dataset](https://doi.org/10.5281/zenodo.15735347) and [supplementary collection](https://doi.org/10.6084/m9.figshare.c.8229719.v1) remain **one evidence family**. This is a focused continuation of [R26](../bacterial_panel_leads/REPORT.md), not a new independent replication or systematic literature review.

## What the strain table resolves

The official Figshare API identifies [supplement item 30997061, version 1](https://doi.org/10.6084/m9.figshare.30997061.v1), file `rspb20252004_si_001.pdf`, catalogue size 3,549,450 bytes and MD5 `d454a31d796b804ea3a1c40e6e0194fd`. The item explicitly carries CC BY 4.0. Firecrawl returned a text representation covering all 10 declared PDF pages. **The original PDF binary was not acquired or hashed locally.** Catalogue identity and captured text are authenticated at those respective levels; this does not claim a byte-for-byte PDF replay or independent sequence validation.

[The derived registry](STRAIN_MAP.json) records all 14 Table S3 strain entries, their internal IDs and distinct marker/deletion states. The focal strains are:

| Published locus | Internal strain ID | Published allele description |
| --- | --- | --- |
| wspF / PFLU1224 | MPB08384 | Δ150bp (677–826) |
| awsX / PFLU5211 | MPB10583 | Δ32bp (229–261) |
| mwsR / PFLU5329 | MPB10613 | T2183C |

The awsX description is retained literally: inclusive endpoints span 33 positions while the table says 32 bp. A half-open convention would span 32 positions. The coordinate convention remains unresolved; no corrected allele is invented. These locus names refer to characterized SBW25 genetic variants. They are not arbitrary colony colours or morphotypes.

The registry distinguishes chromosomal constitutive fluorescent tags from the plasmid pCdrA–mScarlet reporter (MPB38082), as well as ΔfliA, Δwss and ΔpvdS derivatives. The Figure 6 Methods identify ancestral SM founders by sGFP2 and mScarlet but do not name their internal IDs. Table S3 lists an sGFP2-labelled SM only with ΔpvdS. That permits a candidate crosswalk, not a verified assignment of the Figure 6 founders to this deletion background. No molecular assignment of small, large, wheel-like or dark endpoint colonies follows from this table.

## Which measurements share a unit or context

[The join matrix](UNIT_JOIN_MATRIX.json) distinguishes documented within-assay links from missing links between assays. The main gains are:

- **Early occupation:** Supplementary Figure S1 says the points are three or four different inoculum densities per strain, measured at two hours. They are not independent replicate mutations. The R26 surface workbook supplies genotype/dilution groups and ROI counts, but still lacks the ROI → image → well → plate → independent preculture map. Its mwsR/awsX and wspF/SM date labels differ. Semantic genotype matching now improves, while a contemporaneous matched batch remains unverified. The surface-to-inoculum density ratio is dimensional; converting the stored volume and area units gives a length, consistent with the figure's µm axis. It is not a lineage establishment probability.
- **Imaging:** The supplementary Methods explicitly change to LB and delete pvdS for confocal microcolony imaging and micron-scale SM/WS co-culture images. The latter use fluorescent label swaps. Those observations retain their own medium, deletion, inoculum and timing context; they do not automatically supply matched controls for the default KB assays or all three routes. The supplement's co-culture Methods give an approximate 10³ cells/mL starting scale while Figure S3 states approximately 5 × 10³ per type; preserve the source descriptions without manufacturing an exact shared dose.
- **Rescue experiment:** Main Methods 4e describe 12 initial WS monoculture wells, followed by a plate with three WS monocultures and nine co-cultures. The paper reports 2/9 co-culture mat successes versus 0/15 combined monoculture successes. These are well outcomes across assay stages, not independently counted introduced lineages. The source does not crosswalk those wells to the new workbook, establish matched pre-existing resident scaffolds at native mutation times, or test the full Wsp/Aws/Mws intervention triad.
- **Evolution endpoints:** Main Methods provide day six and two plating dilution levels. They do not decode each workbook suffix or connect reporter-positive colonies to independently verified new molecular acquisitions. Resident scaffold formation precedes reporter visibility in the described evolution experiment; the first fluorescent focus is an observation time, not a directly timed mutation birth.

## New workbook audit answers the denominator questions

Both exact XLSX files match their current official Zenodo sizes and MD5 values. Their combined size is **18,289 bytes**. [The unit audit](WORKBOOK_UNIT_AUDIT.json) is reproducible without executing spreadsheets.

`Pellicle_success.xlsx` contains eleven `pellicle, total` aggregate pairs in four date blocks, with no individual well, plate, independent culture or genotype field. The dates are obtained from numeric cells with Excel date format 14 and the workbook's default 1900 date system. At the same recorded dilution exponent −3.5, the source has:

| Source date | Pellicles / recorded total |
| --- | --- |
| 2024-06-16 | 1 / 3 |
| 2024-06-19 | 0 / 3 |
| 2024-06-26 | 9 / 9 |

The fourth date block is 2023-11-07. The difference at −3.5 shows why date-specific records must remain separate until strain, inoculum calibration and culture/batch links are resolved. Recorded zero-success pairs remain genuine zeros within their stated aggregate denominators. Missing well identities remain missing. The 45 total recorded outcomes do not become 45 independently known mutation or lineage introductions. The paper's Poisson/beta description is recorded as its method; no project count law or inferential error allocation is replaced by it.

`PcdrA-evo-count_2024_10_08.xlsx` explicitly calls six rows plates: `1-6-1/2`, `2-6-1/2` and `3-6-1/2`. Its three paired summaries are 1,067, 1,186 and 1,123 sampled colonies. Nine cached formula cells agree with literal sums, including four shared-formula descendants whose XML contains no formula text. Those descendants are checked using the declared shared anchor and relative row structure; their cached totals are not added as extra observations.

Across the 3,376 sampled colonies, the four recorded category totals are 200 SM-dark, 10 SM-red, 810 WS-dark and 2,356 WS-red. This supports the article's reported fluorescence/morphology discordance. These categories do not constitute independently verified molecular positives and negatives, so their proportions are not admitted as assay sensitivity, specificity, route assignments or native-origin probabilities. Explicit plate labels in this workbook strengthen the plate interpretation for this experiment; they do not independently decode the older colour-workbook suffixes. R26's separate `Dark wheel` count and missing E30 remain unresolved.

## Target-specific admission and stopping decision

Admit the strain identities as published source annotations; the two small workbooks as authenticated descriptive measurements; and the supplementary context differences as control-design constraints. Do not admit a complete matched route panel, native-origin benchmark, calibrated observation matrix or biological TMD fit. The supplementary four-state model also cites Lind 2019 for its forward mutation-rate parameter and assumes an equal reverse phenotype-switch rate despite noting that the latter has not been systematically measured. This is reused model input, not newly independent matched supply evidence.

The next substantive gate is a precise strain/culture/well/plate/image crosswalk with independent molecular acquisition truth and route-specific supply, establishment, loss and recovery controls under the target context. More scalar workbooks alone cannot answer it. No further source acquisition is justified in this branch merely to expand the count totals. Existing forecasts, context/eta, error allocation, count-law and fixed-stopping rules remain unchanged, as do the paused automation and immutable methods 0.6.0 archive. No laboratory protocol is selected and no outreach or new experiment is claimed.

## Provenance and verification

[The source ledger](SOURCES.json) records seven logical acquisition calls, exact arguments, capture times, wrapper and response hashes, source depth, item-specific rights and byte accounting. The eighth allocated call was unused. Article/provider bodies, XLSX files and incidental author metadata remain outside Git. The R26 source cache disappeared after the environment restart, so the earlier public receipt is historical evidence: **R26 source replay was not rerun**.

Run the read-only, standard-library checker:

```sh
python -B research/strain_unit_map/verify_sources.py
python -B research/strain_unit_map/verify_sources.py --source-cache /path/to/r27-strain-map/sources
```

Without the optional cache it explicitly reports source replay UNRUN. [The saved receipt](VERIFICATION_RECEIPT.json) records this round's executed wrapper, binary, arithmetic and public-file checks. The verifier authenticates the captured representations and declared joins; it does not validate causal claims or independent mutation truth. Original commentary and derived ledgers: CC BY 4.0. Verification code: MIT. Source data and supplementary work: Karita and colleagues, cited above. Prepared for Ricardo Maldonado with AI assistance; internal AI-assisted review is distinct from qualified external scientific assessment.
