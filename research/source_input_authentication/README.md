# R000009: authenticate the source inputs before reproducing a mutation-rate fit

The final Farr et al. article identifies FALCOR and an MSS maximum-likelihood method, but the released materials inspected here do not identify the actual historical submission, server build, estimator settings or output report. This audit makes the available units and missing provenance explicit. It does not reproduce the reported mutation rates or confirm Mutation by Natural Dominance.

The original offline script verifies the previously acquired public dataset ZIP and primary article XML by SHA-256, inspects six OOXML workbooks and five RTF readme files for literal software keywords, checks the Figure 4A formula masters, and reproduces 144 cached arithmetic values. Two legacy binary XLS files are inventoried and hash-pinned; semantic parsing of those two files is **UNRUN**. Neither source files nor operator relationship targets are included in this package.

The Figure 4A workbook contains several different quantities that must remain distinct:

| Quantity | Unit and interpretation | Historical FALCOR input authenticated? |
| --- | --- | --- |
| H | Integer size-qualified candidate colonies pooled across I selective plates | No |
| L, M | Confirmed C565T colonies and sequencing denominator | No |
| H·L/M | Confirmation-corrected candidate-pool estimate | No |
| K = 20H/(I·J) | Candidate CFU-density estimate per mL; J is the dilution fraction | No |
| O = K·L/M | C565T-corrected CFU-density estimate per mL | No |
| G = 20·10⁶·E | Terminal total CFU-density estimate per mL | No |
| 6G | Nominal whole-culture CFU estimate using the reported 6 mL culture volume | No |

H·L/M is fractional for **9 of 12 WT culture occurrences**, and integral for all 12 ΔpsrA occurrences. This is a property of the correction formula, not evidence that fractional values were submitted to FALCOR, rounded, or treated as mutation births. The script publishes aggregate ranges and hashes of ordered source-derived quantity vectors to prepare a later comparison with an authenticated run export. These hashes use the documented exact-rational reconstruction and JSON serialization, rather than Excel's cached decimal bytes. Rounding and input conventions must still be reconciled. The hashes do not authenticate or disprove a historical FALCOR submission.

H is pooled across multiple plates. Pooled H and L/M do not recover labelled per-plate genotype counts, aliquot pairings or a disjoint capture law. Plates and sequenced colonies remain technical sampling within the 24 culture occurrences. Six individual transformants per background were used on two occasions; this is not 24 independently constructed transformants. All 24 released Figure 4A confirmation counts are positive. The separate destructive S4 time course contains an initial negative confirmation followed by additional sequencing; it must not be folded into a Figure 4A zero-count fit.

Four bounded public GET attempts returned no readable software or new author-response artifact: the current official FALCOR URL and the HTTPS variant of the legacy URL declared in Hall et al.'s 2009 abstract both failed with a proxy `CONNECT 403`; two distinct OA-metadata endpoint paths returned HTTP 404. All used scoped network escalation, the existing proxy and TLS verification. The receipt records 50,304 response bytes. These failures describe this environment's access, not the historical server's existence or the absence of an underlying public file. The 2009 abstract describes a Java applet and three calculation methods; it does not authenticate the 2024 Farr run. Its full software paper and executable source remain unread/unacquired here.

The current official domain can be proposed as a future environment allowlist addition, preserving other destinations. This round made no environment configuration change and did not test a newly published environment. No authentication token was needed or accessed.

`INPUT_AUTHENTICATION_CONTRACT.json` maps source facts, units, reported outputs and run-provenance gaps. Its ten-field status map corresponds to the earlier prepared source request; no request was sent. The seven peer-review-history subarticles are kept separate from final article methods, and linked author-response DOCX bodies remain unread. None of the 26 actual TMD study-input fields is resolved by these external reporter data.

Run with the separately acquired source cache:

```sh
python -B audit_source_inputs.py --zip /path/to/source_data.zip \
  --article-xml /path/to/nlpd_hotspot_2025.xml \
  --output /tmp/source-input-audit.json --check-against SOURCE_INPUT_AUDIT.json
```

Without those exact source files, the raw-source replay is **UNRUN**; package checksums and review documentation remain inspectable. The script is offline and uses Python's standard library. It performs no Excel, Java, FALCOR, model fitting, interval estimation, new biological simulation or source-file extraction.

Sources: Farr et al. (2025), DOI [10.1371/journal.pgen.1011572](https://doi.org/10.1371/journal.pgen.1011572), final main-article sections 6, 7 and 16; released data DOI [10.5281/zenodo.14335473](https://doi.org/10.5281/zenodo.14335473), CC BY 4.0; Hall et al. (2009), DOI [10.1093/bioinformatics/btp253](https://doi.org/10.1093/bioinformatics/btp253), abstract only. Existing R6 and R7 audits retain the deeper confirmation, fitness, geometry and conditional-model limitations. This is an original input-provenance audit, not a new biological finding.
