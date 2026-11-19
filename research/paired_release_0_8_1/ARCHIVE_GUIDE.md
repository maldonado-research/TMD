# Paired endpoint evidence and archived route rankings

TMD report and methods supplement 0.8.1 · Ricardo Maldonado · 18 November 2026 Pacific (19 November UTC)

The new report examines what paired, retrospectively selected observations identify in the Howells and Ji studies. The accompanying archive also includes the earlier comparison of recorded route rankings and the sensitivity of those rankings to school and school-year weights. Start with the two reports for study-specific denominators, results, and limits. [Paired evidence](research/paired_evidence/README.md) · [Archived ranking sensitivity](research/archived_rank_robustness/README.md)

## Reproduce the aggregate calculations

Extract the ZIP, open a shell in the directory containing this guide, and run the following commands with Python 3.10 or later. The packaged counts suffice for these checks.

```sh
paired=research/paired_evidence
archive=research/archived_rank_robustness
python3 -B "$paired/verify_paired.py" "$archive/howells_receipt.json" "$paired/paired_result.json"
python3 -B "$paired/verify_attribution.py"
python3 -B "$paired/verify_peach.py"
python3 -B "$archive/verify_weights.py"
python3 -B -m research.archived_rank_robustness.complete_howells | diff - "$archive/howells_completion.json"
python3 -B research/archived_route_ranks/audit.py | diff - research/archived_route_ranks/rank_result.json
```

To regenerate the earlier ranking figure in the extracted archive, install Matplotlib and run `python3 -B research/archived_rank_robustness/rank_margins.py`. The rendering uses the packaged aggregate JSON files. The paired evidence report gives the instructions for its own source replays and figures.

## Published source spreadsheets

The ZIP contains aggregate receipts and original analysis code. The original spreadsheets are available separately from the studies.

| Study | Published materials |
|---|---|
| Howells et al., paired endpoint records | [Article](https://doi.org/10.1111/1462-2920.70061) · [Figshare workbook, version 1](https://doi.org/10.6084/m9.figshare.28340420.v1) · [Publisher workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC11847636.1/EMI-27-e70061-s001.xlsx) |
| Matela et al., historical population archive | [Article](https://doi.org/10.1128/aem.02499-25) · [Table S1 workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC13101516.1/aem.02499-25-s0002.xlsx) |
| Ji et al., peach records | [Article](https://doi.org/10.1371/journal.pgen.1011829) · [Table S2 (file s016)](https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s016.xlsx) · [Table S5 (file s019)](https://pmc-oa-opendata.s3.amazonaws.com/PMC12370204.1/pgen.1011829.s019.xlsx) |

## Archive identity

The SHA-256 sidecar verifies the downloaded ZIP. `MANIFEST.json` identifies the exact Git commit, source path, byte count, and SHA-256 for every packaged source file. The accompanying formulation and earlier ranking report supply the historical context. References to the wider project can be resolved at the manifest commit. [Model formulation and proposed empirical test](research/FORMULATION_AND_NEXT_EMPIRICAL_TEST.md) · [Earlier ranking report](research/archived_route_ranks/README.md) For a byte-identical rebuild, check out the manifest commit and run the following command in its repository root, using an existing output directory.

```sh
python3 -B research/paired_release_0_8_1/build_archive.py --commit HEAD --output-dir .
```

Credit Ricardo Maldonado and cite the version-specific Zenodo record when referring to this supplement. The report series keeps the earlier published ZIPs and their checksums. Original code is MIT-licensed and original documentation is CC BY 4.0. Each third-party source retains its published terms. [Report and methods series](https://doi.org/10.5281/zenodo.23068055) · [Prior report 0.8.0](https://doi.org/10.5281/zenodo.24356344) · [TMD repository](https://github.com/maldonado-research/TMD) · [Software license](LICENSE) · [Licensing and attribution](LICENSING.md)
