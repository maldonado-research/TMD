#!/usr/bin/env python3
"""MIT. Read-only reference annotation/source join audit; no network, fits or writes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, 'Duplicate JSON key: ' + k)
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def representation(capture):
    value = capture.get('response', capture.get('result', {}).get('value', {}))
    data = value.get('structuredContent')
    if isinstance(data, dict) and 'markdown' in data:
        return data['markdown']
    for item in value.get('content', []):
        if item.get('type') == 'text':
            try:
                data = json.loads(item['text'])
            except ValueError:
                continue
            if isinstance(data, dict) and 'markdown' in data:
                return data['markdown']
    raise ValueError('No provider markdown representation')


def genbank(path, old_tag):
    text = path.read_text()
    require(text.startswith('LOCUS') and text.rstrip().endswith('//'), 'Invalid GenBank framing')
    region = re.search(r'REGION: (\d+)\.\.(\d+)', text)
    require(region is not None, 'Missing accession region')
    lo, hi = map(int, region.groups())
    sequence_parts = re.split(r'^ORIGIN\s*$', text, maxsplit=1, flags=re.M)
    require(len(sequence_parts) == 2, 'Missing ORIGIN sequence block')
    seq = ''.join(re.findall('[acgt]+', sequence_parts[1].split('//', 1)[0])).upper()
    require(len(seq) == hi - lo + 1, 'Reference slice length mismatch')
    features = re.findall(r'^     CDS +([^\n]+)\n(.*?)(?=^     \S|^ORIGIN)', text, re.M | re.S)
    target = [(loc, body) for loc, body in features if '/old_locus_tag="'+old_tag+'"' in body]
    require(len(target) == 1, 'Missing/ambiguous old locus mapping')
    loc, body = target[0]
    m = re.fullmatch(r'(complement\()?([0-9]+)\.\.([0-9]+)\)?', loc.strip())
    require(m is not None, 'Unsupported target CDS location')
    reverse = bool(m[1]); start, end = int(m[2]), int(m[3])
    dna = seq[start-1:end]
    if reverse:
        dna = dna.translate(str.maketrans('ACGT', 'TGCA'))[::-1]
    def q(key):
        match = re.search(r'/'+key+r'="([^"]+)"', body)
        require(match is not None, 'Missing qualifier: '+key)
        return re.sub(r'\s+', '', match[1])
    protein = q('translation')
    require('/codon_start=1' in body and '/transl_table=11' in body, 'Unexpected translation convention')
    require(len(dna) == 3*(len(protein)+1), 'CDS/translation length mismatch')
    require('VERSION     NC_012660.1' in text and 'AM181176.4' in text, 'Reference accession drift')
    require('Assembly: GCF_000009225.2' in text and 'Annotation Date                   :: 12/21/2021' in text,
            'Reference assembly/annotation date drift')
    require('Annotation Software revision      :: 5.3' in text, 'Reference PGAP revision drift')
    record = {'accession':'NC_012660.1', 'identical_record_as_reported':'AM181176.4',
              'assembly':'GCF_000009225.2', 'annotation_date':'2021-12-21', 'annotation_pipeline':'NCBI PGAP 5.3',
              'exact_slice_sha256':sha(path),
              'old_locus_tag':old_tag, 'current_locus_tag':q('locus_tag'),
              'protein_id':q('protein_id'), 'genomic_start':lo+start-1,
              'genomic_end':lo+end-1, 'strand':-1 if reverse else 1,
              'cds_nucleotides':len(dna), 'protein_residues':len(protein),
              'codon_start':1, 'translation_table':11,
              'source_slice_start':lo, 'source_slice_end':hi}
    return record, dna, protein, seq


def derive(cache, root):
    module_spec = importlib.util.spec_from_file_location('r28_source_reader', root/'research/matched_source_feasibility/verify_sources.py')
    reader = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(reader)
    workbook, _ = reader.workbook(cache/'R28_fig6.xlsx')
    mws_rows = workbook['Mws']['rows']
    origins = []
    for row in (13, 15, 16, 17, 18, 19):
        r = mws_rows[row]
        genome = int(re.fullmatch(r'[ACGT](\d+)[ACGT]', r['A'])[1])
        gene = int(re.fullmatch(r'[ACGT](\d+)[ACGT]', r['D'])[1])
        origins.append({'row':row, 'genome_cell':'A'+str(row), 'gene_cell':'D'+str(row),
                        'genome_label':r['A'], 'gene_label':r['D'], 'implied_forward_origin':genome-gene+1})
    require(len({r['implied_forward_origin'] for r in origins}) == 1, 'Inconsistent historical workbook origin')
    historical_origin = origins[0]['implied_forward_origin']
    aws, aws_dna, aws_protein, _ = genbank(cache/'S05.gb', 'PFLU5211')
    mws, mws_dna, mws_protein, mws_slice = genbank(cache/'S06.gb', 'PFLU5329')
    for witness in origins:
        label = witness['genome_label']
        position = int(label[1:-1])
        require(mws_slice[position-mws['source_slice_start']] == label[0],
                'Workbook genome reference base does not match acquired slice')
    aws_row = workbook['Aws']['rows'][22]
    require(aws_row['D'] == '229-261' and aws_row['C'] == 'del 33 bp', 'Aws source label changed')
    require(aws_row['A'] == '5707405-5707437' and aws_row['G'] == 'del Y77-Q87',
            'Aws genome/peptide source label changed')
    deleted = aws_dna[228:261]
    peptide = aws_protein[76:87]
    # Table 11 uses the standard code for these internal codons.
    table = {'TAC':'Y','ACC':'T','GAC':'D','CTG':'L','ATC':'I','AAA':'K','GGC':'G','ACT':'T','CAG':'Q','GTC':'V','GCC':'A'}
    require(''.join(table[deleted[i:i+3]] for i in range(0,len(deleted),3)) == peptide,
            'Deleted codons do not reproduce annotated peptide')
    genome_variant = historical_origin + 2183 - 1
    current_position = genome_variant - mws['genomic_start'] + 1
    index = current_position - 1
    codon_start = index - index % 3
    codon = mws_dna[codon_start:codon_start+3]
    require(mws_dna[index] == 'T', 'Historical-coordinate genomic reference base not T')
    mutant = codon[:index%3] + 'C' + codon[index%3+1:]
    historical_aa = (2183-1)//3+1
    current_aa = index//3+1
    require(mws_protein[current_aa-1] == table[codon], 'Current translation disagrees with codon')
    article = representation(read(cache/'R28_2009.json'))
    supplement = representation(read(cache/'R27_supplement.json'))
    require('| WSR | _mwsR_ | T2183C | V272A |' in article, 'Original WSR string lost')
    require('WST contains an in-frame deletion (33 nucleotides)' in article, 'Original WST source anchor lost')
    require('Repeated sequencing of _wsp_ from WSX revealed no mutation' in article, 'WSX unresolved anchor lost')
    require('Δ32bp (229-261)' in supplement and 'MPB10583' in supplement and 'MPB10613' in supplement,
            'Karita source labels lost')
    return {'schema_version':1, 'reference_records':[aws,mws],
            'awsX_deletion':{'source_2009_label':'Δ229-261','source_2009_reported_length':33,
                            'source_2009_reported_peptide':'ΔYTDDLIKGTTQ','source_2025_literal':'Δ32bp (229-261)',
                            'reference_cds_interval_one_based_inclusive':[229,261],
                            'reference_genomic_interval_one_based_inclusive':[aws['genomic_end']-261+1,aws['genomic_end']-229+1],
                            'length':len(deleted),'deleted_sequence_sha256':hashlib.sha256(deleted.encode()).hexdigest(),
                            'translated_deleted_peptide':peptide,'source_2019_workbook_row':22,
                            'repeat_positions_one_based':[m.start()+1 for m in re.finditer('ACCCAG',aws_dna)],
                            'MPB10583_sequence_verified':False,'Karita_annotation_corrected':False},
            'mwsR_coordinate_join':{'historical_origin_basis':'Lind2019 Figure6 source data Mws paired genome/gene SNP coordinates; inferred coordinate origin, not stock sequence',
                                   'historical_coordinate_witnesses':origins,'historical_implied_genomic_origin':historical_origin,
                                   'current_CDS_start_offset_nt':mws['genomic_start']-historical_origin,
                                   'source_2009_nucleotide_label':'T2183C','source_2009_protein_label':'V272A',
                                   'conditional_genomic_position':genome_variant,'reference_codon':codon,'alternate_codon':mutant,
                                   'historical_origin_protein_consequence':table[codon]+str(historical_aa)+table[mutant],
                                   'current_CDS_position':current_position,'current_protein_consequence':table[codon]+str(current_aa)+table[mutant],
                                   'literal_current_CDS_position_2183_base':mws_dna[2182],
                                   'condition':'2009/Karita T2183C must use the same coordinate origin implied by the 2019 workbook; that equality is not independently authenticated.',
                                   'MPB10613_sequence_verified':False,'historical_WSR_record_corrected':False},
            'historical_cohort':{'molecular_table_counts':{'Wsp':16,'Aws':6,'Mws':3,'Unresolved':1},
                                 'functional_Wsp_associated_count':17,'WSX_molecular_gene':None,
                                 'same_2007_2009_collection':True,'new_independent_origins':0}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cache',type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    public = read(package/'PUBLIC_FILES.json')
    require({p.name for p in package.iterdir() if p.is_file()} == set(public['public_files']), 'Public allowlist mismatch')
    for p in package.rglob('*'):
        require(not p.is_symlink() and (not p.is_dir()), 'Unexpected directory or symlink')
    for r in public['files']:
        require(Path(r['path']).name == r['path'], 'Unsafe public path')
        path = package/r['path']
        require(path.stat().st_size == r['bytes'] and sha(path) == r['sha256'], 'Public fingerprint mismatch: '+r['path'])
    sums = {}
    for line in (package/'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ',1)
        require(name not in sums and Path(name).name == name, 'Unsafe/duplicate sum path')
        sums[name] = digest
    require(set(sums) == set(public['public_files'])-{'SHA256SUMS.txt'}, 'Hash closure mismatch')
    require(all(sha(package/name)==digest for name,digest in sums.items()), 'SHA256SUMS mismatch')
    provenance = read(package/'SOURCE_PROVENANCE.json')
    require(provenance['logical_scientific_calls'] == len(provenance['calls']) == 6, 'Call budget drift')
    require(sum(r['bytes'] for r in provenance['saved_acquisition_files']) == provenance['saved_acquisition_bytes'] <= 8388608,
            'Byte accounting drift')
    for r in provenance['inherited_dependencies']:
        path = root/r['path']
        require(path.stat().st_size == r['bytes'] and sha(path) == r['sha256'], 'Inherited dependency drift')
    study = read(root/'research/prospective_design/REGISTRY_CANDIDATE.json')['study_inputs_requiring_resolution']
    planning = read(root/'research/native_origin_controls/PROSPECTIVE_CONTROL_FIELDS.json')['actual_values']
    require(len(study)==26 and all(v is None for v in study.values()), 'Study NULL registry drift')
    require(len(planning)==18 and all(v is None for v in planning.values()), 'Planning NULL registry drift')
    decision = read(package/'DECISION.json')
    require(decision['matched_panels_admitted']==0 and not decision['new_biological_fit'], 'Admission drift')
    audit = read(package/'DERIVED_SOURCE_AUDIT.json')
    require(audit['awsX_deletion']['length']==33 and audit['mwsR_coordinate_join']['literal_current_CDS_position_2183_base']=='A', 'Derived annotation drift')
    replay = 'UNRUN: no source cache supplied'
    if args.source_cache:
        for r in provenance['saved_acquisition_files']+provenance['reused_source_files']:
            require(Path(r['filename']).name == r['filename'], 'Unsafe source path')
            path = args.source_cache/r['filename']
            require(path.stat().st_size==r['bytes'] and sha(path)==r['sha256'], 'Source fingerprint mismatch: '+r['filename'])
        require(derive(args.source_cache,root)==audit, 'Source/reference replay mismatch')
        replay = 'PASS: exact reference slices, CDS loci/codons, reused workbook coordinates and selected source anchors'
    print(json.dumps({'status':'PASS','source_replay':replay,'study_nulls':26,'planning_nulls':18,
                      'matched_panels_admitted':0,'stock_sequences_authenticated':0,'new_biological_fit':False},indent=2))


if __name__=='__main__':
    main()
