"""Adversarial structural cases; entirely synthetic, never biological data."""
import contextlib
from copy import deepcopy
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from preflight import audit_tables, main, StructuralError


def result(row_id, barcode, fitness='0', population='bc01', experiment='synthetic'):
    return dict(row_id=row_id, experiment=experiment, population=population,
                barcode=barcode, row_role='individual', fitness=fitness)


def annotation(barcode, label='CNV', population='bc01', experiment='synthetic'):
    return dict(experiment=experiment, population=population,
                barcode=barcode, cnv_annotation=label)


class PreflightTests(unittest.TestCase):
    def test_equal_length_positional_data_does_not_supply_identity(self):
        # Equal lengths cannot identify which estimate belongs to which barcode.
        with self.assertRaises(StructuralError):
            audit_tables([{'fitness': '1'}, {'fitness': '0'}], [annotation('A'), annotation('B')])
        a = audit_tables([result('r1', 'A', '1'), result('r2', 'B', '0')], [annotation('A')])
        b = audit_tables([result('r1', 'B', '1'), result('r2', 'A', '0')], [annotation('A')])
        self.assertNotEqual(a['individual_records'], b['individual_records'])
        self.assertFalse(a['source_row_binding_and_role_provenance_verified'])
        self.assertFalse(b['source_row_binding_and_role_provenance_verified'])

    def test_permutations_preserve_keyed_findings_and_reconcile_all_rows(self):
        rows = [result('r1', 'A', '1e-2'), result('r2', 'B', '0'),
                result('r3', 'A', '-0.1', population='bc04')]
        calls = [annotation('A'), annotation('B', 'noCNV'), annotation('orphan')]
        expected = audit_tables(rows, calls)
        for rp in itertools.permutations(rows):
            for ap in itertools.permutations(calls):
                self.assertEqual(audit_tables(list(rp), list(ap)), expected)
        self.assertEqual(expected['individual_rows'], 3)
        self.assertEqual(expected['matched_individual_rows'], 2)
        self.assertEqual(expected['unmatched_individual_rows_kept_unknown'], 1)
        self.assertEqual(expected['orphan_annotation_rows'], 1)

    def test_duplicate_keys_and_row_identifiers_reject_join_expansion(self):
        bad_pairs = [([result('r1', 'A'), result('r2', 'A')], []),
                     ([result('r1', 'A'), result('r1', 'B')], []),
                     ([result('r1', 'A')], [annotation('A'), annotation('A')])]
        for rows, calls in bad_pairs:
            with self.subTest(rows=rows, calls=calls), self.assertRaises(StructuralError):
                audit_tables(rows, calls)

    def test_zero_and_missing_annotation_do_not_imply_absent_event(self):
        x = audit_tables([result('r1', 'A', '0')], [])
        self.assertEqual(x['individual_rows'], 1)
        self.assertEqual(x['individual_records'][0]['annotation_status'], 'unmatched_unknown')
        self.assertIsNone(x['individual_records'][0]['source_cnv_annotation'])
        for flag in ['biological_lineage_identity_verified', 'genotype_negative_truth_verified',
                     'source_row_binding_and_role_provenance_verified', 'clock_units_verified',
                     'source_execution_verified', 'native_measurement_admitted']:
            self.assertIs(x[flag], False)

    def test_nonindividual_rows_require_roles_and_remain_accounted(self):
        rows = [result('r1', 'A', '0')]
        for role in ['aggregate', 'padding']:
            rows.append(dict(row_id=role, experiment='synthetic', population='bc01',
                             row_role=role, barcode=None, fitness=None))
        for perm in itertools.permutations(rows):
            x = audit_tables(list(perm), [])
            self.assertEqual(x['result_rows'], 3)
            self.assertEqual(x['individual_rows'], 1)
            self.assertEqual(len(x['explicitly_excluded_rows']), 2)
        bad = deepcopy(rows);bad[0].pop('row_role')
        with self.assertRaises(StructuralError): audit_tables(bad, [])
        bad = deepcopy(rows);bad[1]['fitness'] = '0'
        with self.assertRaises(StructuralError): audit_tables(bad, [])

    def test_no_identifier_coercion_normalization_or_implicit_alias(self):
        for field, value in [('barcode', 1), ('barcode', True), ('barcode', ' A'),
                             ('population', ''), ('experiment', 'x\ny')]:
            row=result('r1', 'A');row[field]=value
            with self.subTest(field=field, value=value), self.assertRaises(StructuralError):
                audit_tables([row], [])
        x=audit_tables([result('r1','A',population='bc04')],[annotation('A',population='bc01')])
        self.assertEqual(x['matched_individual_rows'],0)
        self.assertEqual(x['orphan_annotation_rows'],1)

    def test_ambiguous_or_nonfinite_numeric_values_and_empty_frames_rejected(self):
        for value in [None, True, 0.1, 'NaN', 'Infinity', ' 1', '1_0', '1,0']:
            with self.subTest(value=value), self.assertRaises(StructuralError):
                audit_tables([result('r1','A',value)], [])
        for rows in [[], {}, [dict(row_id='p', experiment='x', population='y',
                                   barcode=None, fitness=None, row_role='padding')]]:
            with self.assertRaises(StructuralError): audit_tables(rows, [])

    def test_cli_binds_exact_input_and_rejects_duplicate_JSON_members(self):
        payload={'result_rows':[result('r1','A')], 'annotation_rows':[]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'synthetic.json';p.write_text(json.dumps(payload))
            out=io.StringIO()
            with contextlib.redirect_stdout(out): self.assertEqual(main([str(p)]),0)
            x=json.loads(out.getvalue());self.assertEqual(x['input_JSON_bytes'],p.stat().st_size)
            p.write_text('{"result_rows":[],"result_rows":[],"annotation_rows":[]}')
            err=io.StringIO()
            with contextlib.redirect_stderr(err): self.assertEqual(main([str(p)]),2)
            self.assertEqual(json.loads(err.getvalue())['status'],'REJECTED')


if __name__=='__main__': unittest.main()
