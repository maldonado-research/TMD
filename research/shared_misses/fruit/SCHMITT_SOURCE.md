# Which fruit observations support the reported tropical-tree counts?

Schmitt et al. studied one parent tree per species. They selected candidate sites that had already appeared in multiple leaves on fruit-bearing branches and searched for them in fruit material. Their Results give 23 of 160 for *Dicorynia guianensis* and 9 of 36 for *Sextonia rubra*. Their Methods describe **160 selected sites across both trees**, partitioned as 124 and 36. The archive supports the Methods partition and the two retained site counts. [Results and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC10927512/) · [Author data, version 2](https://doi.org/10.5281/zenodo.10089692)

| Stage | *D. guianensis* | *S. rubra* |
|---|---:|---:|
| Initial candidate sites, reconstructed from the archived leaf tables | 124 | 36 |
| Targets in the final panel reported in Supplementary Note S9 | 117 | 36 |
| Candidate sites present in the filtered fruit table | 23 | 9 |
| Candidate sites with an accepted call in at least one listed fruit tissue | 23 | 9 |
| Candidate sites with an accepted call in tissue labelled “embryo sac” | 20 | 8 |

The authors’ R notebooks specify the candidate subsets for the two trees. Reapplying those rules to the two archived leaf-summary tables gives 124 and 36 distinct locus-and-allele identities. The submitted *Dicorynia* candidate-list member independently contains exactly the same 124 identities. All 32 distinct identities in the filtered fruit table join their respective initial candidate sets. Supplementary Note S9 reports the final assay panel. The filtered fruit table does not supply a per-target crosswalk for the seven *Dicorynia* candidates omitted from that panel. [Dicorynia notebook](https://github.com/sylvainschmitt/treemutation/blob/fc6a2eeef7b2bb1d178ebfbf3a79652ca13fb9df/11-MutationsAngela.Rmd) · [Sextonia notebook](https://github.com/sylvainschmitt/treemutation/blob/fc6a2eeef7b2bb1d178ebfbf3a79652ca13fb9df/12-MutationsSixto.Rmd) · [Supplementary Note S9](https://pmc.ncbi.nlm.nih.gov/articles/instance/10927512/bin/pnas.2313312121.sapp.pdf)

The deposited figure code retains positive-fraction, heterozygous-flag records across fruit tissues for its transmitted category. We deduplicated retained rows by species, scaffold, position, reference and alternate state, then counted the union across literal tissue labels. All 23 *Dicorynia* and 9 *Sextonia* sites appear under this rule. In *Dicorynia*, 18 sites appear in cotyledon and all 18 also appear under the embryo-sac label. Three sites have accepted calls exclusively in records labelled “endocarpe.” One *Sextonia* site has accepted calls exclusively in records labelled “pericarpe.” Thus the two published numerators are reproduced by considering all recorded fruit tissues; restricting the calculation to the embryo-sac label gives 20 and 8. The authors also describe uncertainty about maternal versus embryonic tissue origin during development and possible mixing of small tissues during dissection. A sample label alone therefore cannot establish the cellular origin of an accepted call. [Supplementary Note S9, limitations before Figure S36](https://pmc.ncbi.nlm.nih.gov/articles/instance/10927512/bin/pnas.2313312121.sapp.pdf) [Archived figure calculation](https://github.com/sylvainschmitt/treemutation/blob/fc6a2eeef7b2bb1d178ebfbf3a79652ca13fb9df/40-Figures.Rmd#L200-L215)

The any-tissue yield among initially selected candidates is 23/124 (18.55%) and 9/36 (25%). Of those initial candidates, 101 and 27 have no row in the filtered fruit table. Their absence supplies no evidence that each site and tissue was callable or that every missing event was biologically absent. The discovered-candidate denominator, final target-panel denominator, tissue-restricted numerator and per-offspring transmission probability each require different information. Each retained site counts once across sampled fruits. Estimating a per-offspring transmission probability would require an offspring denominator at each locus, with documented coverage and independently interpretable offspring genotypes. These two tree records provide no population-wide transmission estimate or calibration for the separate peach-flower study. A targeted literature check found no linked correction in the inspected Crossref metadata on 19 November 2026. [Primary study](https://doi.org/10.1073/pnas.2313312121) · [Crossref metadata](https://api.crossref.org/works/10.1073/pnas.2313312121)

## Replay the source

The original version-2 ZIP is 4,239,118,097 bytes. A standard-library helper retrieves only the four compressed table members used for this calculation, using fixed byte ranges for this published archive version. Each decompressed ZIP member remains a gzip file whose SHA-256 is checked against the receipt. To use an already downloaded complete ZIP, pass its path directly to the replay. [Original ZIP](https://zenodo.org/records/10089692/files/treemutation_save.zip?download=1)

```sh
python3 -B fetch_schmitt_members.py /tmp/schmitt-tables
python3 -B replay_schmitt.py --members /tmp/schmitt-tables | diff - schmitt_receipt.json
python3 -B verify_schmitt.py /tmp/schmitt-tables
# Alternative using the authors' full ZIP
python3 -B replay_schmitt.py --zip /path/to/treemutation_save.zip | diff - schmitt_receipt.json
```

The range download transferred 868,450 bytes of ZIP payload; the four extracted gzip members have a combined size of 872,005 bytes. The four member digests and full paths are in the receipt. Independently reading the entries through the ZIP directory also validated their ZIP CRCs. A second calculation using SQL groups checks both candidate sets and all seven species-by-tissue counts.
