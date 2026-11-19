"""Reconcile original peach catalogues, named leaf counts and measured offspring genotypes."""
import argparse
from collections import Counter
import csv
from decimal import Decimal
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
NATIVE = {
    's1': '7fd6bccbe17753771d0b65ff945bcf80581998af66df596df9aa245598fcf4a9',
    's2': '7a6f6a083a80f9baa7b6fc3ec5dc577b041072e2b5f20ee23d86385dd746aa2a',
    's7': '9a8ffb1020eeeddf9e2c129b91b0f710a41a4ad68b59f9444fabd2b88ce8f5c3',
    's11': '51caef01a89815100928b4f6fbd7c6b41753d99e0192b4c609cbeee61ac4ed30',
    'gz': '485a99260cacccfb7105281edb05b48770e12ad1a418f5f54c0a8b1f24411647',
}
FOCAL = 'DHQ1_B1-1-L1'
NEIGHBOR = 'DHQ1_B1-1-L2'
PREDICTED_M101 = (FOCAL, 'DHQ1_B1-11-L2', 'DHQ1_B1-6-L2', 'DHQ1_B1-8-L2')


def read_sheet(path):
    from openpyxl import load_workbook
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        return list(book.worksheets[0].values)
    finally:
        book.close()


def tsv_digest(header, rows):
    stream = StringIO()
    writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
    writer.writerow(header)
    writer.writerows(rows)
    return sha256(stream.getvalue().encode()).hexdigest()


def extract(paths):
    sources = dict(zip(NATIVE, paths))
    for name, path in sources.items():
        assert sha256(path.read_bytes()).hexdigest() == NATIVE[name], name
    s1, s2, s7, s11 = [read_sheet(sources[k]) for k in ('s1','s2','s7','s11')]
    sample_rows = [r for r in s1 if r[:2] == ('Prunus persica','DHQ1')]
    site_rows = [r for r in s2 if r[:2] == ('Prunus persica','DHQ1')]
    assert len(sample_rows) == 75 and len(site_rows) == 48
    def decimal(n):
        return format(Decimal(str(n)).normalize(), 'f')
    roster_hash = tsv_digest(['sample_id','mapped_depth','genome_pct_depth_at_least_five'],
                             [(r[3],decimal(r[7]),decimal(r[8])) for r in sample_rows])
    carrier_hash = tsv_digest(['chromosome','position','change','listed_leaves'],
                              [(r[2],int(r[3]),r[5],r[4]) for r in site_rows])
    assert roster_hash == 'fcd0d1139a85c5b6c6b2dee206394569727041bf4b310cc2ae0739e2f6c33be7'
    assert carrier_hash == '7f5c8a082cbc5dbbef3282e6b9e8d2c679117b5e93b029a115a22ce2ab1946dc'
    sites = {(r[2],int(r[3])): set(r[4].split(';')) for r in site_rows}
    listed = {'M71':sites['Pp01',2130859], 'M101':sites['Pp04',21561355],
              'M103':sites['Pp05',11214460]}
    roster = {r[3] for r in sample_rows}
    raw = {r[3]:r for r in s7[7:] if r[3] in roster}
    assert set(raw) == roster and all(r[1] == 2016 for r in raw.values())
    columns = {m:s7[6].index(c) for m,c in [('M71','M71_A'),('M101','M101_G'),('M120','M120_C')]}
    leaves = {}
    for leaf,r in sorted(raw.items()):
        counts = {}
        for m,c in columns.items():
            ref,alt,vaf = r[c:c+3]
            assert ref+alt>0 and abs(vaf-100*alt/(ref+alt)) < 1e-8
            counts[m] = [ref,alt]
        leaves[leaf] = {'listed':[m for m in listed if leaf in listed[m]], 'counts':counts}
    progeny = {}
    overlap = {}
    assert [s11[2][i] for i in (4,8,12)] == ['#M101','#M103','#M120']
    for r in s11[4:]:
        leaf = r[3]
        counts = {}
        calls = {}
        for m,c in zip(('M101','M103','M120'),(4,8,12)):
            ref,alt,vaf,call = r[c:c+4]
            assert ref+alt>0 and abs(vaf-100*alt/(ref+alt)) < 1e-8
            counts[m] = [ref,alt]
            if call:
                assert call == ('Absent' if alt==0 else 'HOM' if ref==0 else 'HET')
                calls[m] = call
        if r[1]=='First True Leaf':
            progeny[leaf]={'branch':r[2], 'counts':counts, 'calls':calls}
        else:
            assert r[1]=='Branch Leaf' and leaf in leaves and not calls
            for m in ('M101','M120'):
                assert counts[m]==leaves[leaf]['counts'][m]
            overlap[leaf] = counts
    assert len(overlap)==26 and len(progeny)==7
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(sources['gz']) as archive:
        doc=ElementTree.fromstring(archive.read('word/document.xml'))
    grid = [[ ''.join(t.text or '' for t in c.findall('.//w:t',ns))
              for c in r.findall('w:tc',ns)] for r in doc.findall('.//w:tbl/w:tr',ns)]
    gz = []
    for r in grid:
        if r[0].startswith('TH-'):
            a,b,ni,c,d,nd=map(int,r[1:7])
            assert ni==a+b and nd==c+d
            gz.append([r[0],ni,nd])
    assert len(gz)==9 and grid[-1][-1]=='61/93(66%)'
    return {'native_sha256':NATIVE,'normalized_2019_tsv_sha256':{'roster':roster_hash,'carriers':carrier_hash},
            'counts_order':['REF','ALT'], '2016_leaf_panel':leaves, 'S11_parental_overlap':overlap,
            'seven_progeny':progeny, 'GZ_columns':['sample','inherited','de_novo'], 'GZ':gz}


def analyze(data):
    leaves = data['2016_leaf_panel']
    result = {}
    for marker in ('M71','M101'):
        groups = {}
        for flag in (False,True):
            pairs = [r['counts'][marker] for r in leaves.values() if (marker in r['listed']) == flag]
            groups['listed' if flag else 'unlisted'] = {
                'leaves':len(pairs), 'alt_reads_histogram':dict(sorted(Counter(alt for ref,alt in pairs).items())),
                'ref_alt_totals':[sum(ref for ref,alt in pairs),sum(alt for ref,alt in pairs)]}
        result[marker] = groups
    cutoffs = []
    for k in range(1,9):
        a,b = [{leaf for leaf,r in leaves.items() if r['counts'][marker][1]>=k}
               for marker in ('M71','M101')]
        label = ('M101 empty' if not b else 'M71 strict subset of M101' if a < b else
                 'disjoint' if not a & b else 'crossing')
        cutoffs.append({'min_alt_reads':k,'M71':len(a),'M101':len(b),'both':len(a&b),'relation':label})
    kids = data['seven_progeny']
    positive={m:{k for k,r in kids.items() if r['calls'][m]!='Absent'} for m in ('M101','M103','M120')}
    child_counts = {m:{'calls':dict(sorted(Counter(r['calls'][m] for r in kids.values()).items())),
                      'ref_alt_totals':[sum(r['counts'][m][i] for r in kids.values()) for i in (0,1)]}
                    for m in positive}
    gz = data['GZ']
    return {'2016_leaves':len(leaves),'single_marker_memberships': result,
            'focal_and_neighbor':{k:leaves[k] for k in (FOCAL,NEIGHBOR)},
            'prior_minimum_additions_M101_ref_alt':{k:leaves[k]['counts']['M101'] for k in PREDICTED_M101},
            'threshold_sensitivity':cutoffs,
            's11_parental_overlap':len(data['S11_parental_overlap']),
            's7_s11_overlapping_marker_leaf_entries':2*len(data['S11_parental_overlap']),
            'progeny_counts':child_counts, 'progeny_joint_M103_M120':{
                'both':len(positive['M103']&positive['M120']),
                'M103_only':len(positive['M103']-positive['M120']),
                'M120_only':len(positive['M120']-positive['M103']),
                'neither':len(kids.keys()-(positive['M120']|positive['M103']))},
            'GZ_nine_progeny':{'inherited':sum(r[1] for r in gz),
                               'de_novo':sum(r[2] for r in gz)}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract',type=Path,nargs=5,metavar=('WANG_S1','WANG_S2','JI_S7','JI_S11','WANG_GZ'))
    opts=parser.parse_args()
    obj=(extract(opts.extract) if opts.extract else
         analyze(json.loads((HERE/'peach_inputs.json').read_bytes())))
    print(json.dumps(obj,indent=2))
