# Which recorded variants crossed between two sequenced mouse litters?

Among 173 distinct validated events documented in at least one pup in the first sequenced litter, **10 were also documented in a different pup in the later sequenced litter**. This comparison uses five earlier and five later whole-genome-sequenced (WGS) offspring per family. The later panel was litter 8 in CBGP8 and litter 9 in GPCB2. Other litters and targeted-only siblings fall outside this comparison. [Analysis design](../DESIGN.md) · [Lindsay et al., 2019](https://doi.org/10.1038/s41467-019-12023-w)

| Pedigree | Events in 10 WGS pups | Documented among five early pups | Documented among five late pups | Both litters | Later documentation among early-positive events |
| --- | ---: | ---: | ---: | ---: | ---: |
| CBGP8 | 172 | 76 | 100 | 4 | 4/76 (5.3%) |
| GPCB2 | 216 | 97 | 125 | 6 | 6/97 (6.2%) |
| Combined | 388 | 173 | 225 | 10 | 10/173 (5.8%) |

Each event enters the observed early group if its explicit carrier list contains an early WGS pup. Its later outcome is documentation in at least one late WGS pup. The 215 events documented only in late WGS pups had no early WGS carrier record and were ineligible for the observed follow-up fraction. Absence from a positive list can reflect an unobserved genotype. Per-locus negative calls for every pup would be needed to turn that fraction into an estimate of actual carrier recurrence. Both WGS panels contributed to the original discovery process. Their observable overlap is a retrospective endpoint.

## A timing comparison conditional on the discovery roster

There were 23 events documented in at least two WGS pups. Their overlap across the two actual litters depends on which pups carried them. Under a reference model, assign each pedigree's ten fixed pup profiles to two artificial groups of five, with all 252 assignments equally likely. Keep every marker and every tissue-collapsed carrier identity within a pup together. This holds fixed the full catalog, each event's WGS carrier count, its original eligibility as a WGS-observed event and co-carriage among markers. Under each allocation, count events documented in both groups across the whole catalog. A group-specific early risk set changes when pups change groups. Restricting all permutations to the 173 events that happened to appear early in the real chronology would condition on the observed outcome of the allocation. [Previous WGS carrier-count audit](https://github.com/maldonado-research/TMD/blob/246d02bd66389ab50637f423dd62220aa852c754/research/pedigree_timing/mouse/README.md)

For example, an event with $K\ge1$ recorded carriers among ten pups has probability $1-2\binom{5}{K}/\binom{10}{K}$ of appearing on both sides under the balanced null. The convention is $\binom{5}{K}=0$ for $K>5$. Summing those probabilities gives the expected number of shared events by linearity. Correlated markers can share all their carriers, so that sum gives no independent-marker sampling distribution. The calculation below enumerates the allocations of entire pup profiles and combines the two families under independent allocations. Equality counts in both tails. The two-sided tail includes every count at least as far from its own reference mean as the observed count.

| Allocation model | Joint allocations | Expected events spanning groups | Observed | Lower tail | Upper tail | Two-sided |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Five of ten per family | 63,504 | 15.397 | 10 | 0.0370 | 0.9836 | **0.0542** |
| Preserve early female count per family | 15,120 | 15.217 | 10 | 0.0430 | 0.9804 | **0.0602** |

The family differences matter. CBGP8 had 4 events in both litters against a balanced reference expectation of 8.73. GPCB2 had 6 against 6.67. The two-sided per-family tails were 0.0159 and 0.8254. Only two actual litter pairs contributed, and they differed biologically as well as in birth time. Randomization here describes a hypothetical exchangeability of ten full profiles in each family. Experimental random assignment of birth order did not occur. An excess of within-litter co-carriage could reflect the composition of a parental lineage, litter-level biology, detection differences or the selection of validated loci. The data do not identify a causal timing effect.

The average of the authors' per-pup WGS depths was 25.0× early versus 23.6× late in CBGP8 and 33.8× versus 25.0× in GPCB2. An exploratory allocation restriction preserves both the early sex count and the sum of reported early depths in each family. Only 9 and 3 assignments remain, giving 27 joint assignments, a reference mean of 16.33 and a two-sided tail of 1/27. The small allocation space, rounded per-pup depth measurements and absence of a per-locus callability adjustment limit this comparison. [Supplementary Table 1](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM1_ESM.pdf) · [Full distributions and integer tail counts](split_results.json)

The original article described inferred primary embryonic lineages as distributed randomly with respect to litter timing. This two-litter comparison instead counts recorded mutation events that occur in both sampled groups. [Lindsay et al., lineage reconstruction](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731245/)

## A prospective carriage endpoint

For a new pedigree, freeze an early landmark and the candidate list using only observations available by that date. Record eligibility for every early-positive event, a forecast for each eligible marker, and a predefined later follow-up roster. A recorded later positive resolves a positive outcome. To resolve a later negative for the fixed roster, require interpretable assays in every scheduled later pup. If $R$ eligible events have a later positive, $Z$ have a fully observed negative, and $U$ remain unresolved, a later-positive fraction compatible with those observations ranges from $R/(R+Z+U)$ to $(R+U)/(R+Z+U)$ under accurate recorded calls. Report losses over that same uncertainty set if forecasting. Related markers and pups call for replication across founder families. This endpoint addresses future carriage. Population establishment would require measurements of lineage survival or expansion against a defined comparator.

## Reproduction

The included JSON assigns one bit per sequenced pup and gives the multiplicity of each recorded carrier pattern. A one means documented in the source's carrier list. A zero means absent from that list. Repeated tissues from one pup contribute one bit. The pinned 0.13.0 grouping code counts each source-defined two-base mutation once. Both source files are by Lindsay et al., distributed under CC BY 4.0. [Original event workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC6731245.1/41467_2019_12023_MOESM5_ESM.xlsx) · [Source license](https://creativecommons.org/licenses/by/4.0/) · [Anonymous profiles and covariates](profiles.json)

With Python 3.9 or later, run these commands in this directory. The verifier enumerates every pair of allocation masks directly and checks the joint histograms against the convolution. Regenerating profiles also needs Poppler's pdftotext, both original files, and the project's prior pedigree reader.

```sh
python3 -B split_test.py | diff - split_results.json
python3 -B verify_split.py
python3 -B extract_profiles.py path/to/41467_2019_12023_MOESM1_ESM.pdf path/to/41467_2019_12023_MOESM5_ESM.xlsx ../../pedigree_timing/mouse | diff - profiles.json
```
