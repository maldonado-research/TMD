"""Separate raw-ZIP source-unit oracles; no imports from the audited implementation."""
from pathlib import Path
from fractions import Fraction
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
import re
import zipfile
import xml.etree.ElementTree as E
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--zip', required=True, type=Path)
parser.add_argument('--derived', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
ZIP = args.zip
EXPECTED_SHA = '9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6'
SOURCE = args.derived
data = ZIP.read_bytes()
assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA
source = json.loads(SOURCE.read_text())
outer = zipfile.ZipFile(io.BytesIO(data))
ns = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def member(suffix):
    names = [k for k in outer.namelist() if k.endswith(suffix) and not k.startswith('__MACOSX/')]
    assert len(names) == 1
    return outer.read(names[0])

def cells(book, file, strings):
    result = {}
    for node in E.fromstring(book.read(file)).findall('.//x:sheetData/x:row/x:c', ns):
        v = node.find('x:v', ns)
        if v is None or v.text is None:
            continue
        result[node.get('r')] = strings[int(v.text)] if node.get('t') == 's' else v.text
    return result

book = zipfile.ZipFile(io.BytesIO(member('2024_06_13_rtqpcrSBW25_Fig4B.xlsx')))
strings = [''.join(x.itertext()) for x in E.fromstring(book.read('xl/sharedStrings.xml')).findall('x:si', ns)]
links = {x.get('Id'): x.get('Target') for x in E.fromstring(book.read('xl/_rels/workbook.xml.rels'))}
sheets = {}
for s in E.fromstring(book.read('xl/workbook.xml')).findall('x:sheets/x:sheet', ns):
    target = links[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
    path = target.lstrip('/') if target.startswith('/') else 'xl/' + target
    if s.get('name') in ('Calculations', 'Rdata'):
        sheets[s.get('name')] = cells(book, path, strings)
setup = cells(book, 'xl/worksheets/sheet2.xml', strings)
well_to_primer = {setup['B'+str(r)]: setup['E'+str(r)] for r in range(2, 98) if 'B'+str(r) in setup and 'E'+str(r) in setup}
cal, plotting = sheets['Calculations'], sheets['Rdata']
logs = defaultdict(list)
mapping = []
for r in range(2, 14):
    bg, rep = plotting['A'+str(r)], int(plotting['B'+str(r)])
    genotype = {'SBW25':'SBW25', 'psrA':'SBW25deltapsrA'}[bg]
    matches = [i for i in range(2, 74) if cal.get('K'+str(i)) == genotype and cal.get('L'+str(i)) == '22hr' and cal.get('M'+str(i)) == str(rep) and 'N'+str(i) in cal]
    assert len(matches) == 1
    i = matches[0]
    pairs = []
    for j in (i-1, i):
        ct = (Fraction(cal['C'+str(j)]) + Fraction(cal['D'+str(j)]))/2
        assert abs(ct-Fraction(cal['H'+str(j)])) < Fraction(1,10**11)
        well = cal['G'+str(j)]
        pairs.append((well_to_primer[well], ct, well))
    assert pairs[0][0] == "nlpD5'" and pairs[1][0] == "nlpD3'"
    log_proxy = pairs[0][1] - pairs[1][1]
    assert abs(log_proxy-Fraction(plotting['C'+str(r)])) < Fraction(1,10**11)
    logs[bg].append(log_proxy)
    mapping.append({'background':bg, 'replicate':rep, 'calculation_row':i,
                    'primer_5prime_well':pairs[0][2], 'primer_3prime_well':pairs[1][2],
                    'log2_proxy_Ct5prime_minus_Ct3prime_exact':str(log_proxy)})
means = {k:sum(v,Fraction())/len(v) for k,v in logs.items()}
geom = 2**float(means['SBW25']-means['psrA'])
arithmetic = sum(2**float(x) for x in logs['SBW25'])/sum(2**float(x) for x in logs['psrA'])
assert math.isclose(geom, source['figure4B_transcript_proxy']['geometric_mean_proxy_ratio'], rel_tol=1e-12)
assert math.isclose(arithmetic, source['figure4B_transcript_proxy']['arithmetic_mean_linear_proxy_ratio'], rel_tol=1e-12)

gb = member('Figure 4A sanger sequencing files/nlpD-kan reference sequence.gb').decode()
assert 'promoter        2023..2025' in gb
reference = ''.join(re.findall('[acgt]+',gb.split('ORIGIN')[1].split('//')[0])).upper()
assert reference[2022:2025] == 'CAG'
target = 2022
left, right = reference[target-16:target-1], reference[target+2:target+17]
groups = defaultdict(Counter)
labels = defaultdict(set)
read_count = 0
for occasion, suffix in [(1,'94 documents from 20_12_23 repeated fluctuation trial 1.fastq'),(2,'96 documents from 10_1_24 fluctuation kan400 trial 2.fastq')]:
    lines = member(suffix).decode('ascii').splitlines()
    assert len(lines)%4 == 0
    for index in range(0,len(lines),4):
        header, seq, sep, quality = lines[index:index+4]
        assert len(seq) == len(quality) and sep.startswith('+')
        m = re.match(r'@(MPB\d+)_c(\d+)_',header)
        assert m
        key = occasion,m.group(1)
        label = int(m.group(2))
        assert label not in labels[key]
        labels[key].add(label)
        # An alternative direct-anchor search, not the audited regex caller.
        starts = []
        search_at = 0
        while True:
            at = seq.find(left,search_at)
            if at < 0:break
            if seq[at+18:at+33] == right:starts.append(at)
            search_at = at+1
        call = 'unresolved'
        if len(starts) == 1:
            pos = starts[0]+16
            if seq[pos] in 'ACGT' and ord(quality[pos])-33 >=20:call=seq[pos]
        groups[key][call]+=1
        read_count+=1
for row in source['sequencing']['diagnostic_culture_groups']:
    key=row['occasion'],row['transformant_label']
    assert dict(groups[key]) == row['diagnostic_target_calls']
    assert len(labels[key]) == row['available_read_records']
    assert sorted(set(range(1,9))-labels[key]) == row['missing_expected_colony_labels']
assert read_count == 190 and len(groups) == 24

by_key = {(r['occasion'],r['background'],r['transformant_replicate_number']):r for r in source['figure4A']['integer_source_and_derived_measurement_ledger']}
frequency_book = zipfile.ZipFile(io.BytesIO(member('Colony Counts Fluctuation assays_20_6_24 .xlsx')))
frequency_strings = [''.join(x.itertext()) for x in E.fromstring(frequency_book.read('xl/sharedStrings.xml')).findall('x:si', ns)]
raw_counts = cells(frequency_book, 'xl/worksheets/sheet2.xml', frequency_strings)
confirmation = cells(frequency_book, 'xl/worksheets/sheet3.xml', frequency_strings)
for i in range(2,26):
    r=str(i)
    # An independent simplified source-integer frequency expression; no cached arithmetic as target.
    exact = (Fraction(raw_counts['H'+r])*Fraction(confirmation['L'+r]) /
             (Fraction(raw_counts['I'+r])*Fraction(raw_counts['J'+r])*
              Fraction(confirmation['M'+r])*Fraction(raw_counts['E'+r])*10**6))
    key=int(raw_counts['A'+r]),raw_counts['B'+r],int(raw_counts['C'+r])
    assert Fraction(by_key[key]['corrected_terminal_frequency']) == exact
assert len(by_key)==24
review = {'status':'passed','method':'Separate raw-ZIP XML cell reader, exact averaged Ct differences, source primer-to-well mapping, direct string-anchor sequence diagnostic, and independently simplified source-integer frequency expression.',
          'dataset_sha256':EXPECTED_SHA,'derived_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'qPCR_replicates_mapped':12,'qPCR_primer_direction':'proxy=2^(Ct5prime-Ct3prime); log2 proxy=Ct5prime-Ct3prime',
          'qPCR_mapping':mapping,'geometric_mean_linear_proxy_ratio':geom,'arithmetic_mean_linear_proxy_ratio':arithmetic,
          'sequence_records_diagnostically_checked':read_count,'culture_groups_checked':len(groups),
          'source_frequency_exact_values_compared':24,'sequence_genotypes_overwritten':False,'MSS_fit_performed':False,
          'confidence_intervals_or_biological_inference_performed':False,'new_sampling_law_admitted':False}
args.output.write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({k:v for k,v in review.items() if k!='qPCR_mapping'},indent=2))
