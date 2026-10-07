# Cancer relevance: a prospective measurement contract

Mutation by Natural Dominance · R000015 · 7 October 2026, America/Los_Angeles

This round makes cancer relevance more concrete by defining what a qualified future evaluation would have to measure and what could falsify a restricted prediction. It also checks a strong ordinary growth/recovery explanation. It is a **design and methods candidate**: no cancer experiment, clinical intervention, biological fit, registered study or prevention result was produced.

## What the inspected biology teaches

A targeted PubMed search returned160 indexed hits. Twelve relevance-ranked candidate metadata/abstract records were inspected, followed by two foundational primary main texts. This is a bounded assessment, not a systematic review or a search of the entire web. Both selected source XML notices permit text mining consistent with UK copyright law; raw article text is excluded from this public package.

- **Martincorena et al.2018, human normal esophagus**, [10.1126/science.aau3879](https://doi.org/10.1126/science.aau3879):844 spatial samples came from **nine donors**. The article reports8,919 coding mutation calls and6,935 putative events after spatial clone merging. These source quantities are distinct from counted independent mutation births or844 independent humans. dN/dS assesses reaching detectable clone size after mutation-context controls. Cancer-associated clones can be abundant in histologically normal tissue; NOTCH1 mutations can be more prevalent there than in cancers. All28 main-body paragraphs were inspected. Detailed supplementary MethodsS1–S7, tables and raw sequencing data were unacquired.
- **Colom et al.2021, mouse esophageal competition**, [10.1038/s41586-021-03965-7](https://doi.org/10.1038/s41586-021-03965-7):the main narrative and available Methods describe early lesion loss, clone competition and perturbation experiments. Tumors, micro-biopsies and technical sequencing samples are nested in mice. The authors also model these processes; simulated outputs are separate from measured animals. Methods report no experiment randomization or investigator blinding. The authors explicitly state that an analogous micro-tumor elimination mechanism in humans remains unknown. The DN-Maml1 **dominant-negative molecular construct** is unrelated to TMD's operational natural-dominance terminology or a measured Mendelian dominance coefficient. Supplementary model notes, tables, source data, images and videos were not acquired or replayed.

These studies support treating mutation supply, clonal selection, spatial competition, survival and detection as serious established explanations. They do not validate TMD. Normal-tissue clonal expansion, malignant transformation and a reduction in cancer incidence are different outcomes.

## A narrowly defined future question

Could a fixed supply-adjusted three-category restriction predict the fate of newly arising, heritable lineages in a held-out context of a defined mammalian epithelial system? Before this could be evaluated, experts would need to select the model, ancestor/background, three disjoint molecular event catalogs and measurement technology, then independently measure mutation supply, lineage growth/survival and recovery. This package selects none of those actual biological inputs.

Use generic categories R1,R2,R3. No Wsp/Aws/Mws labels are transferred from bacteria, and no cancer routes or gene rankings are declared identified. A mutation signature is not automatically a disjoint mechanistic pathway. Every category needs an explicit molecular mapping and compatible observation unit before its probabilities have meaning. [DESIGN_CONTRACT.md](DESIGN_CONTRACT.md) specifies the contract, falsifier, held-out parameter requirement, rivals and unmet inputs.

## The exact synthetic caution

Hold mutation supply q fixed. Expected endpoint descendant mass can have shares

    p_i = q_i*g_i*r_i / sum_j q_j*g_j*r_j.

With relative terminal-yield multipliers g=(t,2,1/t), recovery r=(1,1,1), the supply-adjusted curvature

    J = p2^2*q1*q3/(p1*p3*q2^2)

equals4 for every positive t. Yield includes growth and retention/loss; a value below1 is a relative expected yield, not a fractional realized cell count or an expansion-only rate. A sufficiently large common multiplier makes every yield at least1 while preserving the normalized mixture; those scaling identities are checked. Alternatively keep yields equal and set recovery probabilities proportional to(t,2,1/t), scaled so each is at most1: the same expected shares result. Mutation generation remains unchanged in both examples. For uniform q:

| Synthetic t | Expected endpoint shares R1,R2,R3 | J |
| --- | --- | --- |
|1/2|1/9,4/9,4/9|4|
|1|1/4,1/2,1/4|4|
|2|4/9,4/9,1/9|4|
|4|16/25,8/25,1/25|4|

This is an exact identity of **normalized expected endpoint masses**. It is not an equality of complete count distributions, independent-founder sampling laws or first-arrival processes, nor a fit to patients. Dividing by the true independently known multipliers restores q and J=1. Estimating those multipliers from the same selected outcomes would remove the intended independent test.

The standard algebra shows why apparent agreement with a common-curvature pattern alone cannot establish a changed mutation-production mechanism. No new theorem or priority is claimed.

## Reproduction and retained boundaries

The Python standard-library implementation checks36 synthetic supply/context/multiplier combinations, exact mimic and correction identities, an unequal-curvature example and invalid inputs. It accepts positive int/Fraction triples, external rational values at most32bits, growth multipliers at most16 and recovery probabilities at most1. Engine guards do not depend on assertions; verification CLI and benchmark library reject -O/-OO. Arbitrary composition of externally capped helpers is not guaranteed. No log/exponential arithmetic, biological confidence interval, power calculation or new error budget is supplied.

```sh
cd research/cancer_translation
PYTHONDONTWRITEBYTECODE=1 python3 verify_translation.py --output /tmp/tmd_cancer_translation_replay.json --check-against SYNTHETIC_BENCHMARKS.json
sha256sum -c SHA256SUMS.txt
```

With authenticated external XML caches, optionally add `--human-xml /path/to/PMC6298579.xml --mouse-xml /path/to/PMC7612642.xml`. Without caches, source replay is explicitly UNRUN. Hash/anchor replay verifies inspected bytes, not a biological causal interpretation. [SOURCE_LEDGER.json](SOURCE_LEDGER.json) records all four new requests,631,752 response bytes, inspection depth, licenses, the twelve-candidate screen and20 normalized paragraph anchors. Raw patient data and private archive files were not acquired.

The existing26-field actual-study registry, Wsp/Aws/Mws estimand, immutable releases, count-law eligibility, forecasts, error allocations and stopping rules remain unchanged. This package supplies a possible translation question and its barriers. It gives no basis for saying TMD prevents cancer or that funding a pilot guarantees a medical benefit. Prepared by Ricardo Maldonado with AI assistance; original code MIT, original notes and synthetic summaries CC BY4.0.
