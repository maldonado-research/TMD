# Retrospective route rankings and observation audits

TMD reports and methods, version 0.8.0 · Ricardo Maldonado · 18 November 2026 Pacific (19 November UTC)

Two phenotype-selected bacterial collections support the same ordering of archived route labels, Wsp > Aws > Mws. The historical calculation covers one isolate from each of 26 microcosms. The second calculation retains one archived wrinkly clone from each of 50 represented parent populations and allows every choice consistent with the recorded labels. In the first collection, Aws leads Mws by 2–4 records. In the second, its lead is 1–8. Adding one hypothetical parent with an unrestricted label permits a tie in the second collection. These ranges describe the selected records under the stated assignment rules. Estimating the order for all evolving populations requires evidence about inclusion and observation.

The accompanying finite-roster method bounds route counts when some reference labels are missing. Its examples use constructed rosters. The plant analyses use published observations to examine which mutations were selected for verification, which were detected in another tissue, and how two methods overlap on verified positives. All seven apricot branches belong to one tree.

## Read and run

The [archived route report](research/archived_route_ranks/README.md) explains the route calculations, source replays and aggregate results. The [finite-roster guide](research/finite_roster_audit/README.md) describes the verified-label bounds and both synthetic inputs. The [source assessment](research/finite_roster_audit/SOURCE_ASSESSMENT.md) explains the assay and detection denominators in the apricot and oak data.

Extract the ZIP, open a shell in the directory containing this guide, and use Python 3.10 or later. These commands use the standard library and the packaged records.

```sh
python3 -B research/archived_route_ranks/audit.py
python3 -B research/archived_route_ranks/verify.py
python3 -B research/finite_roster_audit/audit.py research/finite_roster_audit/synthetic_reversal.json
python3 -B research/finite_roster_audit/audit.py research/finite_roster_audit/synthetic_input.json
python3 -B research/finite_roster_audit/verify_audit.py
```

The ranking program reads `historical_receipt.json` and `matela_receipt.json` beside the script. Compare its output with `rank_result.json` in the same directory. The historical receipt stores the four assignment counts, number of isolates, and the full source ledger's identity. The finite-roster directory includes `synthetic_result.json` for the 100-record example and `verification.json` for the enumerative checks.

## Reproduce the counts from their sources

Download the relevant file separately. The three XLSX replays for Matela and Goel use openpyxl 3.1.5. The historical and oak replays use the Python standard library. Substitute each downloaded file's path in the commands below.

| Input | Origin |
| --- | --- |
| Historical R28 aggregate ledger with its isolate records | [Exact repository file](https://raw.githubusercontent.com/maldonado-research/TMD/604390d9bba8471be26487e3737c072a0f5cb9bf/research/matched_source_feasibility/DERIVED_SOURCE_AUDIT.json) · [Bantinaki et al.](https://doi.org/10.1534/genetics.106.069906) · [McDonald et al.](https://doi.org/10.1534/genetics.109.107110) |
| Matela et al., supplemental workbook | [Workbook](https://pmc-oa-opendata.s3.amazonaws.com/PMC13101516.1/aem.02499-25-s0002.xlsx) · [Article](https://doi.org/10.1128/aem.02499-25) |
| Goel et al., apricot Additional file 2 | [Versioned workbook](https://doi.org/10.6084/m9.figshare.26368540.v1) · [Supplementary figures S7 and S8 used for confirmation assignments](https://doi.org/10.6084/m9.figshare.26367951.v1) · [Article](https://doi.org/10.1186/s13059-024-03337-0) |
| Xian et al., oak supplement containing Table S10 | [Journal ZIP](https://pmc-oa-opendata.s3.amazonaws.com/PMC12341919.1/jkaf143_supplementary_data.zip) · [Article](https://doi.org/10.1093/g3journal/jkaf143) |

```sh
python3 -m pip install 'openpyxl==3.1.5'
python3 -B research/archived_route_ranks/replay_history.py /path/to/DERIVED_SOURCE_AUDIT.json
python3 -B research/archived_route_ranks/replay_matela.py /path/to/aem.02499-25-s0002.xlsx
python3 -B research/archived_route_ranks/replay_apricot_layers.py /path/to/13059_2024_3337_MOESM2_ESM.xlsx
python3 -B research/finite_roster_audit/replay_apricot.py /path/to/13059_2024_3337_MOESM2_ESM.xlsx
python3 -B research/finite_roster_audit/replay_oak.py /path/to/jkaf143_supplementary_data.zip
```

`replay_history.py` checks the full R28 ledger against its pinned SHA-256, counts the historical isolate records, and reproduces `historical_receipt.json`. The oak replay accepts the journal ZIP or its original workbook, preserving the cell formatting used to identify detections.

## Archive identity, related work and licensing

The root `MANIFEST.json` gives the source commit, repository URL, builder identity, and Git path, length in bytes and SHA-256 for every packaged source file, including this guide. Use that commit in the repository to resolve links in the original reports that point outside these two analysis directories. From a checkout of the recorded commit, run the following command with an existing output directory. The builder prints the SHA-256 of the complete ZIP.

```sh
python3 -B research/roster_release_0_8_0/build_archive.py --commit HEAD --output TMD_roster_audits_0_8_0_2026-11-18.zip
```

The archive uses sorted entry names, fixed permissions and timestamps, and uncompressed ZIP members. The TMD report and methods series also holds the earlier versioned archives. PR 51 addresses a separate question about transporting observation bounds across conditions. [TMD repository](https://github.com/maldonado-research/TMD) · [Report and methods series](https://doi.org/10.5281/zenodo.23068055) · [Methods 0.7.0](https://doi.org/10.5281/zenodo.23970140) · [PR 51](https://github.com/maldonado-research/TMD/pull/51)

Credit Ricardo Maldonado, the TMD repository, and the release version or source commit when reusing the original work. The software is MIT-licensed and the documentation is CC BY 4.0. The cited source publications and supplements retain their respective terms. [Software license](LICENSE) · [Licensing and attribution](LICENSING.md)
