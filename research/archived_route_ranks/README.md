# Which route led among the archived representatives?

Two published collections support the same order, **W > A > M**, when each represented parent population contributes one recorded representative and a representative contributes one supported molecular class. Here W, A and M are the project's historical Wsp, Aws and Mws categories. In the more recent archive the A–M difference can be as small as one. Extending that roster to one additional phenotype-positive population permits a tie.

| Sample and unit | Number of units | W minus A | W minus M | A minus M |
|---|---:|---:|---:|---:|
| Bantinaki–McDonald, one selected isolate per population | 26 | 9 to 11 | 12 to 14 | 2 to 4 |
| Matela, one representative from the sequenced records of each represented population | 50 | 28 to 33 | 31 to 39 | 1 to 8 |
| Matela, hypothetical extension giving one further population an unrestricted label | 51 | 27 to 34 | 30 to 40 | 0 to 9 |

Each endpoint is attainable on its own row under the stated rule. These are count differences, measured in populations. No sampling distribution or confidence level is needed for these finite lists. The studies chose records by phenotype and used different settings. Their agreement establishes a descriptive ordering in two collections. It leaves the order of first mutations, mutation rates, establishment probabilities and the ranking among all organisms in their source populations open.

## The 26-isolate collection

The Bantinaki study selected one isolate with the specified phenotype from each of 26 separate populations. McDonald and colleagues characterized the same lettered isolates. Table 1 assigns 16 to W, six to A, three to M, and leaves one molecular assignment unresolved. Allocating the last record to W, A, M or another class gives the four possible count tables. In the closest comparison, giving it to M leaves six A and four M. The source also describes functional dependence for the unresolved isolate. We preserve the molecular classification used in the archived row ledger. Results depend on the 25 assigned labels being correct. For instance, with the last record assigned to M, a single erroneous A assignment corrected to M would tie A and M. [Bantinaki, Methods](https://doi.org/10.1534/genetics.106.069906) · [McDonald, Table 1](https://doi.org/10.1534/genetics.109.107110) · [Historical source audit](https://github.com/maldonado-research/TMD/tree/604390d9bba8471be26487e3737c072a0f5cb9bf/research/matched_source_feasibility)

## The 50 represented populations

Matela et al. reported 69 sequenced clones of several phenotypes from 54 populations. Their workbook lists 57 wrinkly clones. The sample name encodes school, year, population and clone. Grouping the wrinkly rows by the first three fields gives 44 populations with one record, five with two, and one with three. Reading all three molecular annotation columns yields 40 rows marked only W, nine only A, six only M and two marked both W and M. The article discusses three exceptional clones together. At focal-family resolution, one of those three has two changes in the same M family. A family label on a multichange record is an attribution allowed by this audit. Its causal role in isolation would need separate evidence. [Primary study, Results](https://doi.org/10.1128/aem.02499-25) · [Original Table S1](https://pmc-oa-opendata.s3.amazonaws.com/PMC13101516.1/aem.02499-25-s0002.xlsx)

The choice of representative matters only in five populations. Across their archived records, 37 populations allow only W, seven allow only A, one allows only M, three allow W or M, and two allow A or M. Choosing M in all five variable populations attains the joint counts **(37, 7, 6)**. To reach the opposite A–M endpoint, choose W in the three W/M populations and A in the two A/M populations. The counts become **(40, 9, 1)**. The linked population identifiers are what rule out an A–M tie among these 50. The clone totals alone do not fix which records can be dropped together. [Workbook replay](replay_matela.py) · [Input receipt](matela_receipt.json)

The paper observed the phenotype in 51 of its 54 populations. One phenotype-positive population therefore lacks a sequenced wrinkly representative. If its extra slot is assigned to M in the first feasible table, A and M tie at seven each. Its actual label is unknown. Unsequenced members of the 50 represented populations also have unknown composition. Even a perfectly documented choice among the archived clones cannot identify which route arose first or was most abundant within a parent.

## Exact calculation and reproduction

For each parent p, form the set S(p) of focal labels appearing on its eligible archived records. Retaining one representative and attributing one supported label permits any member of S(p). For a contrast i minus j, let s(i)=1, s(j)=−1 and s(other)=0. The smallest count difference is the sum over parents of min s(c) for c in S(p). Replacing min by max gives the largest. Both follow by choosing a minimizing or maximizing label in each parent. For joint orders and ties the program builds all distinct attainable count tables. It starts at the fixed-class counts and adds one permitted unit vector for each ambiguous parent. This is elementary finite enumeration.

An independent verifier instead chooses physical records first, then completes their labels. It checks all 160 such assignments for the 50 represented parents, 640 with the extra unrestricted slot, the historical table and 815 small rosters. A separate extraction from the publisher-rendered copy of Table S1 matched the original workbook's clone and parent totals. [Exact joint results](rank_result.json) · [Independent verifier](verify.py)

From the repository root, Python 3.10 or later runs the analysis from the saved receipts. Direct spreadsheet replays also use openpyxl 3.1.5.

```sh
python3 -B research/archived_route_ranks/audit.py
python3 -B research/archived_route_ranks/verify.py
python3 -B research/archived_route_ranks/replay_history.py research/matched_source_feasibility/DERIVED_SOURCE_AUDIT.json
python3 -B research/archived_route_ranks/replay_matela.py /path/to/aem.02499-25-s0002.xlsx
```

[Historical input receipt](historical_receipt.json) records the upstream ledger URL and digest. [A paired plant observation check](OBSERVATION_CHECK.md) examines how the observed leader can change when detection conditions change. Together the studies motivate a specific empirical question: does the same ordering persist in a separately defined, independently labeled cohort that includes records missed by the original screen? These retrospective collections supply no held-out test of that question. Prepared 19 November 2026 UTC (18 November Pacific) with AI assistance and independent internal computational checks.
