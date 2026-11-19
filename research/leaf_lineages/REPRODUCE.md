# Reproduce the leaf and branch results

From this directory, run the analysis with Python 3.10 or later, Bash and diff. The calculations read the archived tables locally. Each saved JSON result is compared to its recalculation, and the two independent optimization algorithms must agree on the actual added memberships.

```sh
bash replay.sh
```

## Reopen the measurements

- For the 2016 peach leaves, the extractor reads S1 and S2 Data. The archived TSV files were checked against publisher-rendered tables. The original article PDF supplies a separate transcription of all leaf icons at 46 labelled shoot positions. The row and column labels in the figure and the supplements differ. The isomorphism verifier tests every cell after finding a matching set of labels. [S1 and S2 extraction](carrier/CARRIERS.md) · [Figure sources and verification](topology/FIGURE_MATCH.md)
- For the later peach flower, the counts come from five source tables. The extractor accepts the workbooks or the documented renderings for the final two tables. [Input files, identifiers and extraction command](aliquots/ALIQUOTS.md)
- For the tropical trees, download the authors’ original XLSX. The extractor verifies the file digest and converts physical distances to integer centimetres. A second reader verifies the distances directly in the workbook XML. The two commands below assume the file is in the current directory. [Workbook](https://cdn.elifesciences.org/articles/88456/elife-88456-supp1-v1.xlsx) · [Distances and interpretation](tropical/TROPICAL.md)

```sh
python3 -B tropical/quartet.py --extract elife-88456-supp1-v1.xlsx | diff - tropical/tip_distances.json
python3 -B tropical/verify_quartets.py --workbook elife-88456-supp1-v1.xlsx
```

The workbook extractors use openpyxl. To redraw the peach overlap diagram using Matplotlib, run the following command from this directory.

```sh
python3 -B carrier/plot.py --output peach-overlap.png
```
