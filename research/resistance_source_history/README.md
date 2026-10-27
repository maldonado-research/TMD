# Gifford resistance data: source-history follow-up

Ricardo Maldonado · 27 October 2026 · Original factual assessment with AI assistance

**The 54 source-file disagreements now have a clearer provenance, but no authoritative repair or publication error is established.** This extends the [bounded audit](../resistance_well_audit/README.md) of Gifford et al. (2023), [DOI 10.1371/journal.pgen.1010791](https://doi.org/10.1371/journal.pgen.1010791). It uses static source inspection and original Python diagnostics. No author program was executed, no biological model was fitted, and no malformed record was repaired.

## What the public history establishes

The GitHub API returned 67 commits reachable from the default branch, two branches, and no tags or releases on 27 October 2026. The default `master` head remains [`907311849f5610f114ed3ef99f5de73e51349b67`](https://github.com/dannagifford/multi-resistance/tree/907311849f5610f114ed3ef99f5de73e51349b67), dated 12 September 2022. The `elife` head, [`8bb75249eab85c7c71be8857996cac2e0e5f8292`](https://github.com/dannagifford/multi-resistance/tree/8bb75249eab85c7c71be8857996cac2e0e5f8292), has the same Git blobs for all six assay CSV files and for `munging.R`, `model-fitting.R` and `plots.R`. These returned branches provide no alternative assay representation. This is a bounded public-history observation, not an assertion that no other version exists.

Five assay CSV files are byte-identical between the first upload, [`e043d3bbe15ce50181774890075bb8d002580bb2`](https://github.com/dannagifford/multi-resistance/tree/e043d3bbe15ce50181774890075bb8d002580bb2), dated 20 May 2019, and the pinned head. Only `1ul_individual_single.csv` changed. Its earlier blob is `08354289ff1b6e6d985238984808dc1572c87108`; its current blob is `c1f3db880c17f6322c8c4a53f143b6f052a984d5`.

The [Version 4 commit](https://github.com/dannagifford/multi-resistance/commit/fd7c7922bfb0afa64b442584b7f259c2c355c689), dated 22 August 2022, records three edited lines in that CSV:

| Physical line, including header | Earlier record | Version 4 / pinned record |
|---|---|---|
| 175 | Seven fields; invalid well token `F` | An internal semicolon became a comma, yielding eight fields |
| 179 | Seven fields; trailing semicolon produces an empty token under the strict checker | Trailing semicolon removed; 15 listed wells versus aggregate count 13 |
| 183 | Seven fields; invalid tokens `D` and `K7-B3`, plus repeated tokens | An internal comma and `%%` were introduced; eight fields and invalid tokens remain |

The older snapshot therefore does not supply clean replacement records for the two currently rejected assays. Line numbers and changes are verified against both downloaded bytes and the commit patch; the script does not assume how a particular R/readr version handled them.

## The 54 disagreements

All **33 no-antibiotic disagreements** occur in explicit nonempty well lists. In every such record, the individual list contains exactly one more well than the aggregate value, and the aggregate value equals the number of semicolons. These are all 33 explicit nonempty lists in that treatment; its `ALL` and `0` records agree. This is an exact data identity. It is consistent with counting delimiters, but the inspected files do not establish the process that created the aggregate table.

The **remaining 21 disagreements** span rifampicin (8), nalidixic acid (7), and combination treatment (6). Ten have absolute difference one; eleven have larger differences. Nineteen use explicit lists and two use complements. Examples include rifampicin/day 5/low/MH, 9 listed positives versus 60 aggregate; combination/day 4/intermediate/combination assay, 2 versus 17; and combination/day 6/high/combination assay, 37 versus 40. Their source values remain unresolved. The diagnostic output retains every key, raw-record location and aggregate-cell location.

The [source mapping](https://github.com/dannagifford/multi-resistance/blob/907311849f5610f114ed3ef99f5de73e51349b67/munging.R#L62-L100) ranks measured-frequency headers and joins nominal labels 0/10/25/50 to those ranks. The headers in all three aggregate files are already in ascending numerical order, so the original audit's header-order mapping matches this recipe. A diagnostic enumeration of all 24 fixed mixture-label permutations per treatment finds that the source mapping uniquely minimizes total absolute count difference in each treatment. It does not authenticate culture identity. Minimizing the number of unequal cells alone is misleading: a no-antibiotic permutation lowers that count from 33 to 31 while raising the total absolute difference from 33 to 247. No permutation is adopted as a repair.

## What the inspected code does downstream

In [`munging.R`, lines 63–85](https://github.com/dannagifford/multi-resistance/blob/907311849f5610f114ed3ef99f5de73e51349b67/munging.R#L63-L85), aggregate counts are read and missing counts filtered. At [line 100](https://github.com/dannagifford/multi-resistance/blob/907311849f5610f114ed3ef99f5de73e51349b67/munging.R#L100), the join into the individual-well table selects only volume, treatment, measured frequency, nominal rank and frequency label; it does **not** carry aggregate counts. The individual well lists then determine assay indicators and resistance states, saved as `popns.Rds` at line 143.

[`plots.R`, lines 76–99](https://github.com/dannagifford/multi-resistance/blob/907311849f5610f114ed3ef99f5de73e51349b67/plots.R#L76-L99), reads that object and counts `state.simple` for the experimental-evolution plot. [`model-fitting.R`, lines 40–56](https://github.com/dannagifford/multi-resistance/blob/907311849f5610f114ed3ef99f5de73e51349b67/model-fitting.R#L40-L56), reads it and selects day-six populations. Thus the 54 aggregate disagreements cannot simply be equated with 54 downstream analysis changes. Only two of the 54 disagreements concern MH. In the declared recoding, changing MH alone leaves `state.simple` unchanged, although raw assay patterns and detailed low-density states can change. This invariance does not resolve the other 52 disagreements.

This is a static dependency trace, not a replay of the authors' execution. The acquired evidence does not identify the exact executable environment or publication-generating snapshot. Article prose, including the reported 23.3%–61.7% range, does not explicitly identify the disputed cells or resolve the malformed records. Figure and supplementary-content retrieval did not succeed in this follow-up; their contents were not inferred. The missing founder/exclusion crosswalk and source authority still prevent empirical TMD validation.

## Reproduce the bounded checks

`evidence_receipt.json` contains source URLs, exact SHA-256 identities and available Git blob identities. Keep source bodies outside this note's repository. Populate two external directories using the receipt's `original` and `history` cache labels, then run:

```sh
python verify_history.py external-original-cache external-history-cache --output diagnostics.json
```

The script uses Python's standard library, verifies every receipt hash, checks historical/current blob relationships, and recomputes the strict comparisons and exploratory permutations. It performs no downloads and invokes no author code. Expected results include 54 disagreements, the 33-record delimiter identity, three strict token issues in the 2019 single-treatment CSV, and the unchanged assay blobs across the two returned branches. The 2019 trailing delimiter is flagged under the checker’s explicit strict-token rule; that is not a claim about R's treatment of trailing separators. API response identities reflect the acquisition date and can change on a future retrieval even when source blobs remain unchanged.
