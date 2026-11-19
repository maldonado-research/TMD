# Which peach mutations can be ordered from the leaves that carry them?

Wang et al. sampled 75 leaves from the four main branches of one young peach tree (DHQ1) in 2016. The paper’s Results and Figure 4 give different collection dates within that year. Their S1 Data lists all 75 samples. Their S2 Data lists the leaf identifiers at each of 48 detected mutation sites. The two supplements expose 148 recorded site–leaf memberships. All 75 names in the mutation table occur in the sequencing roster. The four branches contributed 29, 33, 6 and 7 leaves. The original paper used the physical branch history to distinguish earlier and later growth. The set comparison here asks which orderings are possible from the listed leaves themselves. [Study and Figure 4](https://doi.org/10.1371/journal.pbio.3000191) · [S1 sample roster](https://doi.org/10.1371/journal.pbio.3000191.s018) · [S2 mutation calls](https://doi.org/10.1371/journal.pbio.3000191.s019)

For the strongest interpretation, suppose every leaf represents one terminal cell lineage, the ancestral state lacks each mutation, each mutation arose once and was retained, and the leaf calls give complete and accurate states. The descendants carrying one mutation then form a clade. Two such clades can be identical, nested or disjoint. If the two carrier sets overlap and each has leaves absent from the other, they cannot both be clades of the same rooted tree under those assumptions.

| Recorded relation between the two carrier sets | Unordered site pairs | Meaning under the assumptions |
|---|---:|---|
| Disjoint | 1,055 | Separate clades have no relative calendar order specified by the leaves. |
| Strict containment | 54 | The mutation carried by the larger set must precede the mutation carried by its proper nonempty subset on their common lineage. |
| Equal | 9 | The two mutations have identical sampled descendants. Their order along the shared path is unresolved. |
| Crossing | 10 | Some leaves carry both mutations, some only the first, and some only the second. A single irreversible clonal tree cannot fit this pair of displayed sets. |

The table covers all 1,128 unordered pairs. There are 41 distinct carrier sets across the 48 markers. Every marker is restricted to one main branch, so 833 pairs on different branches are automatically disjoint. The ten crossing pairs are split among three branches. Five fall on B1, one on B2 and four on B3. The absence of a single tree accommodating all pairs also limits interpretation of the 54 containments. Each gives a conditional pairwise ordering. Taken together, the records do not establish a dated tree of these mutations. [Computed counts and complete crossing-pair list](carrier_result.json)

## The two historical markers in the flower study

The Pp01:2130859 site corresponds to M71 and Pp04:21561355 to M101 in the later flower study. One leaf (B1-1-L2) appears in both original sets. A second leaf (B1-1-L1) appears only at M71. Thirteen appear only at M101, and 60 are listed at neither site. Thus the two historical markers do not support an M71-before-M101 or M101-before-M71 ordering under the simple model. The later split-lysate read counts at these sites concern a different tissue sampled in 2019. [Earlier marker attribution and flower measurements](https://github.com/maldonado-research/TMD/blob/2c3cc0c4bcefff8e5401a6bde21abac13f83262c/research/split_selection/historical/HISTORICAL.md)

The sets record bulk-leaf calls. A leaf can contain distinct cell populations. For example, one leaf could contain cells carrying only M71 and other cells carrying only M101, producing a double-positive bulk specimen without a cell carrying both. Limited sensitivity could also omit a true carrier. The S1 coverage column reports that 91.7–93.1% of the genome reached five reads across individual leaf samples. That whole-genome measure supplies no locus-specific guarantee. These alternatives suffice to prevent attributing a crossing to recurrent mutation or loss on the evidence here. Investigators also discovered these sites by screening the same tree, so pair counts describe the retained variants and are dependent through shared sites and leaves.

## Reproduce the source comparison

The two supplied TSVs retain the original DHQ1 row order, locus labels and sample identifiers, and include three S1 fields and four S2 fields. Their SHA-256 digests are `fcd0d1139a85c5b6c6b2dee206394569727041bf4b310cc2ae0739e2f6c33be7` for `sample_roster.tsv` and `7f5c8a082cbc5dbbef3282e6b9e8d2c679117b5e93b029a115a22ce2ab1946dc` for `carriers.tsv`. These digests identify the transcriptions. The publisher's spreadsheet renderings were used in this analysis. Native XLSX bytes were unavailable for a separate binary check. Reference calls and missing calls at individual unlisted combinations cannot be distinguished from the S2 list.

Run the following from this folder with Python 3.10 or later. The extractor also accepts a native XLSX file whose worksheet retains the source column labels. For that input it requires openpyxl. The checked extraction used the rendered tables.

```sh
python3 -B carrier_sets.py | diff - carrier_result.json
python3 -B extract_dhq1.py s1 /path/to/s1-rendered.md | diff - sample_roster.tsv
python3 -B extract_dhq1.py s2 /path/to/s2-rendered.md | diff - carriers.tsv
```
