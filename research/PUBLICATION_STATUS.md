# TMD publication status

Checked 2 October 2026 (America/Los_Angeles).

The canonical report/methods concept DOI is **10.5281/zenodo.23068055**. The latest published family record is now [23113326](https://zenodo.org/records/23113326), DOI 10.5281/zenodo.23113326. It has **no version label** and contains the same six filenames, sizes and checksums as published **0.5.0**, [record 23075312](https://zenodo.org/records/23075312). The reviewed **0.6.0 package is absent**. Cite record 23075312 when using the labelled 0.5.0 methods release. Historical software v2.6.5, [record 22398093](https://zenodo.org/records/22398093), belongs to a separate publication family.

## Reviewed 0.6.0 package and changed publication state

[Methods 0.6.0](../TMD_METHODS_0_6_0.md) is a reviewed, public-safe publication candidate, not a published Zenodo version. Its ZIP is 1,277,802 bytes; SHA-256 `72173d93fad40ce6d5b3a9e5db9b18e5804a0509c18866f56cfc3c66baa1de76`. The archive preserves the 1 October methods snapshot and excludes the later R1/R2/R3 continuation rounds.

Earlier authentication and ownership checks succeeded using the existing configured credential, and the New version action created draft 23113326 in this same family. At that checkpoint it was unpublished. A fresh read-only check at **8:42 p.m. Pacific on 2 October 2026** followed the latest-version redirect and confirmed that **23113326 is now published**. The API reports a public creation/modification time near 8:32 p.m. Pacific. The actor is unknown; this research task made no publish request. There is no longer a verified active draft in the inspected linked metadata. Do not upload to the now-published record or describe its DOI as merely reserved.

Before this state change, standard-library and Requests JSON metadata updates returned HTTP 500, and readback failed to match the approved metadata. A separate binary upload returned HTTP 400. Those historical staging failures remain unresolved. Official Zenodo documentation is now accessible and describes a separate multipart upload route; a proposed use of that route stopped at the pre-upload guard because 23113326 had already become published. **No multipart upload, metadata edit, new draft, deletion or publication was performed in this round.**

The [redacted diagnostics](publication_diagnostics/) record methods, content types, byte counts, statuses and readback results without credential values. [Machine-readable status](PUBLICATION_STATUS.json) distinguishes the published record, current draft and proposed version.

## Coordinated staging and browser fallback

Coordinate with the separate publishing task before further writes. Recheck the latest published record, ownership and any linked unpublished draft. Reuse such a draft when present; otherwise a coordinated new version must start from **latest published record 23113326**, preserving the existing family. Do not create a standalone record, delete the inherited-file publication or guess which task published it.

The [reviewed ZIP](../TMD_methods_0_6_0_2026-10-02.zip), [checksum file](../TMD_methods_0_6_0_2026-10-02_SHA256SUMS.txt) and [prepared metadata](ZENODO_0_6_0_METADATA_FINAL.json) remain available for that verified unpublished draft's owner editor. Verify saved metadata and uploaded filenames, byte sizes and checksums before publication. Publishing inherited 0.5.0 files alone cannot archive 0.6.0. The later GitHub source-watch and certified-score work is also outside this immutable 0.6.0 package.

The authorized publishing repair handoff confirms automatic GitHub archiving is OFF for all eight public repositories, superseding the earlier ON state. Preserve it. Intentional versions in this established family are distinct from duplicate standalone publications. Do not delete records/drafts based on similar titles, re-enable integration or make a test release.
