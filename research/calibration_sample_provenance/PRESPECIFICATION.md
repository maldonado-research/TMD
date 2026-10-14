# R35 accession-provenance rule

Declared 2026-10-14 before inspecting SRA experiment records or computing accession joins.

The target is the 22 `srr_accession` rows in the authenticated Zenodo `data/figure2D.tsv`, already fixed by R34. The question is whether new authoritative archive metadata identifies sample, extraction, library or replicate ancestry, exact introduced standard quantities, or named excluded V4 300-mg accessions. No new figure, regression, source calibration or TMD biological fit is selected.

Join by exact SRA run accession only. Each target requires exactly one matching run record with project PRJNA1100950. Preserve unmatched, multiply matched and contradictory records as errors or unresolved cases; never repair a join by similar counts, position or accession order. Check any explicit primer and amount labels against the frozen Figure 2D fields. Record SRA experiment, SRA sample, BioSample and library identifiers separately. A shared archive identifier establishes a shared submission label; different identifiers alone do not establish independent biological samples, independent extractions or independent libraries.

The project metadata may be screened for a named V4 300-mg candidate only when the record explicitly identifies the condition. A record absent from the retained table is not automatically an excluded run. Report an exclusion as confirmed only with a source link between that accession and the stated exclusion criterion. Absence from the archive does not reconstruct the full attempted-sample denominator.

Exact per-accession dose and uncertainty require explicit quantity, units and scope. An approximate paper-level dose remains an author claim. SRA sequencing totals are not post-denoising standard counts and do not verify the fewer-than-ten-standard-read criterion.

The bounded external evidence is public project/experiment/BioSample metadata, with exact captures outside Git. No raw sequence, new author-code acquisition/execution, outreach or laboratory work. Reuse the complete R34 archive inventory and R33 primary article. Any unresolved field remains null; no accession label promotes a row to a native TMD unit or changes the 44 frozen null fields.
