# R29: Reference sequences narrow two allele annotation questions

Two small, exact NCBI reference slices strengthen the source assessment. The reported awsX interval 229–261 encodes the eleven-residue peptide reported for historical WST and spans 33 nucleotides. The mwsR protein label depends on the CDS coordinate origin: a historical-workbook-based projection supports V728A, while the current reference annotation numbers the same genomic change V694A. **These are reference and annotation joins; no historical or MPB stock sequence is authenticated, and no matched biological panel is admitted.**

Six targeted scientific calls acquired three search representations, one publisher page representation and two exact GenBank slices. Search results remain excerpts; the eLife page representation did not expose the V728A figure label found in the search excerpt. Neither is promoted to a verified author correction. R27/R28 source captures and the exact Lind Figure 6 workbook were reused after fingerprint verification. Source bodies remain outside Git. [Provenance](SOURCE_PROVENANCE.json) records exact request arguments, UTC capture times, representations, rights and saved-byte accounting.

## awsX: agreement at the reference interval, with stock identity unresolved

[McDonald et al. (2009)](https://doi.org/10.1534/genetics.109.107110), Table 1 and Results, reports WST as awsX Δ229–261, explicitly a 33-nucleotide in-frame deletion, with peptide ΔYTDDLIKGTTQ. [Lind et al. (2019), Figure 6 source data](https://doi.org/10.7554/eLife.38822.015), Aws row 22, reports 33 bp, gene interval 229–261, genome interval 5707405–5707437, and Y77–Q87. Reuse of this workbook adds no independent cultures to the current study.

The acquired [NC_012660.1 reference region](https://www.ncbi.nlm.nih.gov/nuccore/NC_012660.1?from=5706900&to=5707800) explicitly maps old locus PFLU5211 to PFLU_RS25580, protein WP_015885882.1, reverse-strand CDS 5707093–5707665. Extracting one-based inclusive CDS positions 229–261 gives 33 nucleotides and translates to YTDDLIKGTTQ. Repeat ACCCAG occurs at CDS positions 223 and 256 around this interval, consistent with the historical repeat description; its other occurrence at position 395 is retained in the audit. This validates the local reference-coordinate and peptide correspondence, not the molecular history of any stock. The current protein annotation is 190 residues, whereas the 2009 text reports 171; identical locus names alone do not establish identical annotation conventions.

[Karita et al. supplementary Table S3](https://doi.org/10.6084/m9.figshare.30997061.v1) associates MPB10583 with the literal string “Δ32bp (229-261)”. That string is preserved. The reference check supports the historical 33-nucleotide interval, but neither silently corrects the 2025 source nor proves MPB10583 equals WST or a particular reconstruction. The 2009 study reports both original WST and reconstructed alleles, so a shared allele description is insufficient to identify the stock.

## mwsR: a coordinate origin is necessary before assigning a protein consequence

McDonald Table 1 pairs WSR's mwsR T2183C with **V272A**. The distinct mechanistic reference strain MWS carries G3247A/E1083K; it must not be substituted for WSR. Karita Table S3 associates MPB10613 with mwsR (PFLU5329) T2183C, without a WSR alias or genome accession for that stock.

The exact [NC_012660.1 mwsR-region record](https://www.ncbi.nlm.nih.gov/nuccore/NC_012660.1?from=5854300&to=5859000) maps PFLU5329 to PFLU_RS26190, protein WP_224265972.1. Its annotation is dated 21 December 2021; it states sequence identity to AM181176.4 and assembly GCF_000009225.2. The current CDS is 5854765–5858514 on the forward strand, 3750 nt including the stop codon and 1249 annotated residues. The accession version and annotation date are both recorded because a stable sequence accession is not a frozen gene annotation.

Six paired SNP-coordinate rows in the authenticated 2019 workbook give the same implied mwsR coordinate origin of 5854663 (four distinct coordinate pairs; repeated rows are preserved). This is **102 nucleotides (34 codons) earlier** than the current CDS start. The paired fields document the workbook's coordinate convention; they do not supply a sequenced WSR or MPB10613 genome.

Under the explicit condition that the historical T2183C label uses that workbook origin, its genomic position is 5856845. The exact reference has codon GTC there; T→C yields GCC. This gives **V728A under the workbook origin**, and **V694A at current CDS position 2081**. By contrast, literal position 2183 of the current CDS has base **A**, in codon GAT. Therefore it cannot be normalized as current-CDS T2183C without resolving the reference convention. V272A does not follow from the stated historical origin. This conditional calculation narrows the discrepancy; it is not an author-issued correction and does not prove which coordinates were used for either physical stock.

The targeted search also found a later primary-study excerpt pairing lowercase t2183c with V728A, and an eLife 2015 PDF excerpt containing V728A. Full source context for those particular labels was not acquired; they are leads only. The reference/workbook derivation above is the reproducible evidence used here.

## WSX and admission remain unresolved

The targeted WSX/stock search returned the historical unresolved-sequencing account and the Karita source family. It supplied no authenticated molecular mutation for WSX and no stock-to-sequence crosswalk. This bounded search cannot establish that such evidence does not exist elsewhere.

The same 2007/2009 collection remains 26 separate-microcosm samples, one randomly chosen WS isolate at day five: 16 molecular Wsp, 6 Aws, 3 Mws and one unresolved WSX. A functional-dependency classifier gives 17 Wsp-associated samples and is kept distinct. Neither annotation projection changes that count, adds cultures, establishes a first mutation/first arrival, supplies a complete eligibility ledger, or creates a prospective holdout.

[Join decisions](JOIN_DECISIONS.json) distinguish a supported reference-coordinate relationship from unverified stock identity. The useful next evidence is a named stock/alias/reference-version crosswalk and a sequence-backed interpretation of the precise allele labels. No stock is selected, no outreach or laboratory protocol is commissioned, and no later correction is presumed. Matched route supply, acquisition episodes, independent origin truth, pre-existing/inherited negatives, invisible-loss limits, establishment and separately calibrated recovery/classification remain missing for current admission.

All 26 actual study fields and 18 planning fields stay NULL. R5/R11/R17, theta/eta and comparators, count-law and error-allocation rules, fixed stopping, paused runner and methods 0.6.0 remain unchanged. No biological fit, causal confirmation, new force, held-out success or external peer review is claimed.

Run `python -B research/source_join_resolution/verify_sources.py`, optionally adding `--source-cache /path/to/sources`. Without captures the verifier explicitly reports source replay UNRUN. With captures it verifies exact fingerprints, locus annotations, coordinate arithmetic, short codon translations, original source labels and NULL registries. It does not validate stock biology.

Original assessment and derived facts: Ricardo Maldonado with AI assistance, CC BY 4.0. Verification code: MIT. Source facts are attributed to McDonald, Bantinaki, Lind, Karita and NCBI/RefSeq contributors. Genetics copyright and third-party rights remain unchanged; no blanket license is inferred for source records or workbooks. Raw reference records, article bodies and workbooks are excluded from publication.
