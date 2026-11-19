"""Independently check candidate membership and tissue counts from the four extracted tables."""
import argparse
import csv
import gzip
from pathlib import Path
import sqlite3


def read(directory, pattern):
    matches = list(directory.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"Expected one member matching {pattern}")
    with gzip.open(matches[0], "rt", newline="") as f:
        yield from csv.DictReader(f, delimiter="\t")


def verify(directory):
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE leaves(tree, chr int, pos int, ref, alt, sample, branch, filter);
        CREATE TABLE direct(chr int, pos int, ref, alt);
        CREATE TABLE fruits(tree, chr int, pos int, ref, alt, tissue, flag int, fraction real);
    """)
    for tree, prefix in [("D", "angela"), ("S", "sixto")]:
        db.executemany("INSERT INTO leaves VALUES (?,?,?,?,?,?,?,?)", (
            (tree, r["CHROM"].split("_")[-1], r["POS"], r["REF"], r["ALT"], r["tumor"],
             r["branch"], r["Filter"]) for r in read(directory, prefix + ".leaf_mutations_spectra.tsv.gz")))
    db.executemany("INSERT INTO direct VALUES (?,?,?,?)", (
        (r["CHROM"].split("_")[-1], r["POS"], r["REF"], r["ALT"])
        for r in read(directory, "angela.fruits_candidate_mutations.tsv.gz")))
    db.executemany("INSERT INTO fruits VALUES (?,?,?,?,?,?,?,?)", (
        (r["species"][0], r["scaffold"], r["position"], r["normal"], r["mutation"],
         r["tissue"], r["heterozygous_call_gatk"], r["allelic_fraction"])
        for r in read(directory, "fruit_mutations.tsv.gz")))
    db.executescript("""
        CREATE VIEW eligible AS
        SELECT tree,chr,pos,ref,alt FROM leaves WHERE filter='evs' AND
          ((tree='D' AND branch IN ('A','B','C','D')) OR
           (tree='S' AND substr(branch,1,1) IN ('F','C','B','E')))
        GROUP BY tree,chr,pos,ref,alt HAVING COUNT(DISTINCT sample)>=3;
        CREATE VIEW ledger AS SELECT DISTINCT tree,chr,pos,ref,alt FROM fruits;
        CREATE VIEW signal AS SELECT DISTINCT tree,chr,pos,ref,alt,tissue
          FROM fruits WHERE flag=1 AND fraction>0;
    """)
    def rows(query):
        return list(db.execute(query))
    assert rows("SELECT tree,count(*) FROM eligible GROUP BY tree") == [("D", 124), ("S", 36)]
    assert rows("SELECT * FROM direct EXCEPT SELECT chr,pos,ref,alt FROM eligible WHERE tree='D'") == []
    assert rows("SELECT chr,pos,ref,alt FROM eligible WHERE tree='D' EXCEPT SELECT * FROM direct") == []
    assert rows("SELECT * FROM ledger EXCEPT SELECT * FROM eligible") == []
    assert rows("SELECT * FROM ledger EXCEPT SELECT tree,chr,pos,ref,alt FROM signal") == []
    assert rows("SELECT tree,count(*) FROM ledger GROUP BY tree") == [("D", 23), ("S", 9)]
    assert rows("SELECT tree,tissue,count(*) FROM signal GROUP BY tree,tissue") == [
        ("D","cotyledon",18), ("D","embryo sac",20), ("D","endocarpe",21),
        ("S","embryo sac",8), ("S","fruit base",5), ("S","nucelle",4), ("S","pericarpe",9)]
    assert rows("""
        SELECT tree,chr,pos,ref,alt FROM signal WHERE tissue='cotyledon'
        EXCEPT SELECT tree,chr,pos,ref,alt FROM signal WHERE tissue='embryo sac'
        """) == []
    db.close()
    print("Two reconstructed candidate sets and the named Dicorynia list verified.")
    print("All 32 retained keys match the candidate sets. Seven tissue counts verified.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", type=Path)
    verify(p.parse_args().directory)
