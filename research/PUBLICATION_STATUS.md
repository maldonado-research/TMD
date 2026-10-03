# TMD publication status

Checked 2 October 2026 (America/Los_Angeles).

The canonical report/methods concept DOI is **10.5281/zenodo.23068055**. The latest verified published version remains **0.5.0**, [record 23075312](https://zenodo.org/records/23075312), DOI 10.5281/zenodo.23075312. Historical software v2.6.5, [record 22398093](https://zenodo.org/records/22398093), belongs to a separate publication family.

## Reviewed 0.6.0 package and existing draft

[Methods 0.6.0](../TMD_METHODS_0_6_0.md) is a reviewed, public-safe publication candidate, not a published Zenodo version. Its ZIP is 1,277,802 bytes; SHA-256 `72173d93fad40ce6d5b3a9e5db9b18e5804a0509c18866f56cfc3c66baa1de76`. The archive preserves the 1 October methods snapshot and excludes the later R1/R2/R3 continuation rounds.

Authentication and ownership succeeded using the existing configured credential. The latest published record's New version action created **draft 23113326 in the same concept family**. Reuse [that existing draft](https://zenodo.org/uploads/23113326); this editor is accessible to its owner. DOI 10.5281/zenodo.23113326 is reserved and **not published**. No standalone duplicate record or GitHub release was created.

Both standard-library and Requests JSON metadata updates returned HTTP 500. Readback did not match the required title, version, description, date or creators. A separate binary upload returned HTTP 400 despite a locally constructed 1,277,802-byte request with Content-Length. The draft still contains six inherited files, no verified new upload, and no saved version label. These observations establish an API staging failure; the exact server/proxy cause is unresolved. Successful authenticated reads and version creation do not make failed metadata/file staging safe to publish. Publication was not attempted.

The [redacted diagnostics](publication_diagnostics/) record methods, content types, byte counts, statuses and readback results without credential values. [Machine-readable status](PUBLICATION_STATUS.json) distinguishes the published record, current draft and proposed version.

## Existing-draft browser fallback

Use the owner account's editor at https://zenodo.org/uploads/23113326. Upload the [reviewed ZIP](../TMD_methods_0_6_0_2026-10-02.zip) and [checksum file](../TMD_methods_0_6_0_2026-10-02_SHA256SUMS.txt); use the fields in [prepared metadata](ZENODO_0_6_0_METADATA_FINAL.json). Read saved metadata back and verify uploaded filenames, sizes and checksums against these files before publication. The six inherited files were preserved; do not publish them alone as 0.6.0. This fallback has been prepared, not executed here.

The authorized publishing repair handoff confirms automatic GitHub archiving is OFF for all eight public repositories, superseding the earlier ON state. Preserve it. Intentional versions in this established family are distinct from duplicate standalone publications. Do not delete records/drafts based on similar titles, re-enable integration or make a test release.
