# Cross-feeding study: primary-source feasibility gate

Ricardo Maldonado · 27 October 2026 · Assessment with AI assistance. No biological data analysis or native TMD validation performed.

## Versions and access

The journal record is Al-Tameemi, Rosazza and Rodríguez-Verdugo, *Unilateral cross-feeding constrains adaptive evolution, even in the producer without direct fitness effects*, DOI [10.1093/molbev/msag263](https://doi.org/10.1093/molbev/msag263). [Crossref metadata](https://api.crossref.org/works/10.1093/molbev/msag263) verifies online publication on 21 October 2026. [PubMed XML](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42904594&retmode=xml) records revision on 30 September 2026; its current linked-record response did not identify a PMC copy.

[bioRxiv metadata](https://api.biorxiv.org/details/biorxiv/10.64898/2026.03.31.715640) independently identifies same-title preprint v1, 1 April 2026, DOI [10.64898/2026.03.31.715640](https://doi.org/10.64898/2026.03.31.715640). The API's `published: NA` does not establish a version crosswalk. Journal and preprint full texts were unavailable through the attempted retrievals. The following methods evidence is from the author's publicly accessible **dissertation chapter 2**, not verified journal methods. No identity between versions is assumed.

## Verified dissertation evidence

- Six lines started per culture treatment; P. putida monoculture PP5 became extinct after 50 generations. [PDF pages 35, 51](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=35)
- Evolution used daily 1:100 transfers for approximately 800 generations. P. putida monocultures received 0.06 mM benzoate to match producer output. [Page 51](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=51)
- Population sequencing sampled nominal generations 0/200/400/600/800 after 24-hour revival; eight P. putida clones were sampled per population/timepoint. Target coverage was 100×; the methods say that this enabled confident population calls above 5% frequency. This does not establish a hard cutoff for every call. [Pages 53–54](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=53)
- The endpoint statistic defines site π=p (derived-allele frequency), explicitly distinguishing it from 2p(1−p); treatments pool replicates. [Pages 54–55](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=54)
- Clone-only mutations were excluded from lineage tracking. The methods describe summing constituent mutation frequencies for a lineage; actual inputs, implementation and normalization are needed to assess whether any co-occurring variants affect the reported lineage frequency. No error is established. [Page 56](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=56)
- Partner-removal assays use Co1–Co3 at generations 6/400/800 with three temporal replicates. [Page 58](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=58)
- Data availability identifies PRJNA1339041 for the A. johnsonii genome and directs other underlying data to article/supplements. [Page 59](https://escholarship.org/content/qt0d8146x1/qt0d8146x1.pdf#page=59)

Inference: these are selected, recovered populations. First detection cannot identify mutation birth; missing lineages can reflect early loss, thresholding or recovery. Replicate lines, clones and temporal assay replicates must remain distinct units. The statistic does not estimate mutation rate.

## Independently checked public sequence record

An [NCBI SRA search for PRJNA1339041](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=PRJNA1339041&retmode=json&retmax=200) returned one experiment on the assessment date. Its [SRA XML record](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=46446018&retmode=xml) identifies experiment **SRX34992594**, run **SRR40386432**, BioSample **SAMN52625548**, PacBio Revio WGS of A. johnsonii C6, publicly released 27 August 2026. This is a reference-genome sequencing record, not an authenticated longitudinal Illumina sample manifest. No raw reads were downloaded. This scoped query cannot establish that evolved-sample reads are unavailable elsewhere.

## Actionable next gate

Before choosing this as an empirical test, obtain a version-matched supplement and immutable manifest linking every biological line, species, nominal generation, revival batch, clone, sequencing accession, exclusion and variant table. Verify actual retained sample counts from that manifest rather than multiplying the nominal design. Reproduce the endpoint statistic from its exact calculation, including genomic opportunities/normalization, and keep population counts separate from clone counts.

For any mutation-origin claim, require separately justified cell-division exposure, context-specific mutation opportunities, early-loss/establishment information and capture/recovery calibration. Otherwise restrict the estimand to conditional detected-genotype or trajectory summaries. A useful next computation would audit observation thresholds and replicate-level endpoint distributions only after the accession crosswalk is authenticated; it would not transfer evidence to native SBW25 or resolve the existing R43 identities.

The existing [qualified-review packet](../qualified_review_packet/REPORT.md) distinguishes an observed-prediction claim from a biological origin claim: the latter's planning fields need not all be filled for the former. The [unchanged operational forecast](../prospective_design/README.md) still requires independent baseline, recovery and earlier establishment inputs, along with matching evaluation data. This source has not supplied those native inputs.

Retrieval limitations: Firecrawl search/scrape reported exhausted credits; bioRxiv source/XML/PDF requests returned HTTP 429; the web connector could not retrieve the journal article body. Allowed Crossref/NCBI/bioRxiv API metadata and indexed dissertation text were used. No network restriction was bypassed.
