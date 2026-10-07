"""Independent exact source-unit/vector checks; no software-run authentication."""
import argparse
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as E
import zipfile

NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ZIP_SHA='9f73dd3346c5061526fb577941a771ff39eb5828348b15c6d67c51284dfdeae6'
XML_SHA='937c7eded441b32eea42777d703647965e6090ccb5850017f2b5b6cbd4ea53c2'


def run(zip_path,article_path,audit_path):
    raw=Path(zip_path).read_bytes();xml=Path(article_path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==ZIP_SHA
    assert hashlib.sha256(xml).hexdigest()==XML_SHA
    main=E.fromstring(xml).find('article')
    assert main is not None
    for sid,rate,ci in [('sec006','4.2 × 10-7','95% CI = 4.5 – 3.9 × 10-7'),
                        ('sec007','7.2 × 10-9','95% CI = 9.2 – 5.4 × 10-9')]:
        sec=next(x for x in main.find('body').iter('sec') if x.get('id')==sid)
        text=' '.join(''.join(sec.itertext()).split())
        assert rate in text and ci in text and 'per base-pair per replication' in text
    outer=zipfile.ZipFile(io.BytesIO(raw))
    names=[n for n in outer.namelist() if n.endswith('Colony Counts Fluctuation assays_20_6_24 .xlsx') and not n.startswith('__MACOSX/')]
    assert len(names)==1
    book=zipfile.ZipFile(io.BytesIO(outer.read(names[0])))
    strings=[''.join(x.itertext()) for x in E.fromstring(book.read('xl/sharedStrings.xml')).findall('x:si',NS)]
    links={x.get('Id'):x.get('Target') for x in E.fromstring(book.read('xl/_rels/workbook.xml.rels'))}
    ws=E.fromstring(book.read('xl/workbook.xml'))
    sheet=next(s for s in ws.findall('x:sheets/x:sheet',NS) if s.get('name')=='Calculation of C565T frequency')
    target=links[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
    member=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    cells={}
    for cell in E.fromstring(book.read(member)).findall('x:sheetData/x:row/x:c',NS):
        v=cell.find('x:v',NS)
        if v is not None:
            cells[cell.get('r')]=strings[int(v.text)] if cell.get('t')=='s' else F(v.text)
    groups={};identities=[]
    for row in range(2,26):
        get=lambda col:cells[col+str(row)]
        bg=get('B');h,l,den=get('H'),get('L'),get('M')
        corrected=h*l/den;density=h*20/(get('I')*get('J'));terminal=get('E')*20000000
        values={'candidate_H':h,'confirmed_L':l,'sequenced_M':den,
                'candidate_pool_corrected_estimate':corrected,
                'candidate_density_estimate_CFU_per_ml':density,
                'C565T_corrected_density_estimate_CFU_per_ml':density*l/den,
                'terminal_density_estimate_CFU_per_ml':terminal,
                'nominal_terminal_population_estimate_CFU_in_6ml':6*terminal}
        groups.setdefault(bg,[]).append(values)
        identities.append((int(get('A')),bg,int(get('C'))))
    assert len(set(identities))==24
    audit=json.loads(Path(audit_path).read_text());checks=0
    for item in audit['source_unit_quantity_fingerprints']:
        vector=[r[item['quantity']] for r in groups[item['background']]]
        payload=(json.dumps([str(x) for x in vector],indent=2)+'\n').encode()
        assert hashlib.sha256(payload).hexdigest()==item['ordered_vector_sha256'];checks+=1
        assert str(min(vector))==item['minimum'];checks+=1
        assert str(max(vector))==item['maximum'];checks+=1
        assert sum(x.denominator!=1 for x in vector)==item['noninteger_estimates'];checks+=1
        assert len(vector)==item['culture_occurrences']==12;checks+=1
    fractional={bg:sum(v['candidate_pool_corrected_estimate'].denominator!=1 for v in rows) for bg,rows in groups.items()}
    assert sorted(fractional.values())==[0,9]
    return {'status':'passed','source_XML_sha256':XML_SHA,'source_ZIP_sha256':ZIP_SHA,
            'source_rows':24,'source_quantity_vectors':len(audit['source_unit_quantity_fingerprints']),
            'exact_vector_digest_range_and_integrality_checks':checks,
            'reported_rate_interval_unit_source_checks':2,
            'noninteger_candidate_pool_estimates_by_background':fractional,
            'actual_historical_submission_authenticated':False,
            'Excel_cached_decimal_vectors_hashed':False,'new_source_acquisitions':0,
            'biological_fit_or_confidence_interval_reproduction':False,
            'actual_study_fields_resolved':0,'raw_source_exported':False}


if __name__=='__main__':
    if not __debug__:
        raise SystemExit('Independent verification requires assertions enabled; run without -O/-OO.')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--zip',required=True,type=Path)
    p.add_argument('--article',required=True,type=Path)
    p.add_argument('--audit',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();result=run(a.zip,a.article,a.audit)
    result['reviewer_script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
