"""Independent cached-source and synthetic contract checks; no producer import."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import xml.etree.ElementTree as ET

BASE = Path('/workspace/tmd-research-progress/r19_pedigree_contract_2026-10-07/public_candidate')
REVIEW = Path(__file__).resolve().parent
CHECKS = {}

def check(condition, category):
    if not condition:
        raise RuntimeError('Independent check failed: '+category)
    CHECKS[category] = CHECKS.get(category, 0)+1

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source = json.loads((BASE/'SOURCE_LEDGER.json').read_bytes())['primary']
recent = json.loads((BASE/'RECENT_METHODS_REVIEW.json').read_bytes())['selected_primary']
source_receipts = []
for meta, path, offset, anchor_key, hash_key in (
    (source, Path('/workspace/tmd-research-progress/r16_epithelial_lineage_2026-10-07/raw/PMC6280753.xml'), 0, 'verified_anchors', 'normalized_paragraph_sha256'),
    (recent, REVIEW/'raw/PMC12184895.xml', 1, 'anchors', 'normalized_sha256')):
    raw = path.read_bytes()
    expected_hash = meta['raw_xml_sha256'] if offset == 0 else meta['sha256']
    expected_bytes = meta['raw_xml_bytes'] if offset == 0 else meta['bytes']
    check(hashlib.sha256(raw).hexdigest() == expected_hash, 'primary_hashes')
    check(len(raw) == expected_bytes, 'primary_bytes')
    root = ET.fromstring(raw)
    article = root if root.tag == 'article' else root.find('article')
    check(article is not None, 'article_inventory')
    paragraphs = [' '.join(''.join(node.itertext()).split()) for node in article.find('body').iter('p')]
    check(len(paragraphs) == (80 if offset == 0 else 50), 'paragraph_inventories')
    for anchor in meta[anchor_key]:
        index = anchor['body_paragraph_index']-offset
        check(0 <= index < len(paragraphs), 'paragraph_index_ranges')
        check(hashlib.sha256(paragraphs[index].encode()).hexdigest() == anchor[hash_key], 'paragraph_hashes')
    identifiers = {node.attrib['pub-id-type']: ''.join(node.itertext()).strip() for node in article.findall('front/article-meta/article-id')}
    check(identifiers['doi'] == meta['doi'], 'primary_DOIs')
    check(identifiers['pmid'] == (meta['pmid'] if offset == 0 else '40549685'), 'primary_PMIDs')
    permissions = article.find('front/article-meta/permissions')
    license_xml = ET.tostring(permissions, encoding='unicode')
    license_text = ' '.join(''.join(permissions.itertext()).split())
    check('creativecommons.org/licenses/by/4.0/' in license_xml and 'Creative Commons' in license_text and 'Attribution' in license_text, 'article_CC_BY_4_0')
    source_receipts.append({'doi': meta['doi'], 'raw_sha256': expected_hash, 'raw_bytes': expected_bytes, 'anchor_count': len(meta[anchor_key]), 'paragraph_index_convention': 'zero_based' if offset == 0 else 'one_based_subtract_one', 'this_reviewer_inspected_all_listed_anchors': True, 'full_body_inspection_claimed_by_this_reviewer': False, 'equations_pipeline_supplements_raw_data_or_likelihood_replayed': False})

ledger = json.loads((BASE/'SYNTHETIC_LEDGER.json').read_bytes())
rules = json.loads((BASE/'TOY_RULES.json').read_bytes())
cells = {row['cell_id']: row for row in ledger['cells']}
children = {name: [] for name in cells}
for name, row in cells.items():
    if row['parent_cell_id'] is not None:
        children[row['parent_cell_id']].append(name)

def descendants(root):
    pending, result = [root], set()
    while pending:
        node = pending.pop()
        check(node not in result, 'toy_forward_graph_no_repeated_nodes')
        result.add(node)
        pending.extend(children[node])
    return result

check(len(cells) == 13 and len(ledger['divisions']) == 6, 'toy_exposure_counts')
check(sum(Fraction(row['stop_time'])-Fraction(row['birth_time']) for row in cells.values()) == 20, 'toy_cell_time')
check(descendants('F') == set(cells), 'toy_complete_founder_graph')
for division in ledger['divisions']:
    check(set(children[division['parent_cell_id']]) == set(division['daughter_cell_ids']) and len(children[division['parent_cell_id']]) == 2, 'toy_division_links')
stages = {stage: sum(row['stages'][stage] for row in cells.values()) for stage in ('available_at_collection', 'isolated', 'outgrown', 'sequenced')}
check(list(stages.values()) == [5, 4, 3, 3], 'toy_nested_stages')
unknown = {name for name in cells if not children[name] and not cells[name]['stages']['sequenced']}
check(unknown == {'A121', 'A122', 'B1', 'B22'}, 'toy_terminal_unknown_set')
check(all(cells[name]['genotype_status'] == 'unknown' and cells[name]['sample_id'] is None for name in unknown), 'unknown_is_not_reference')
samples = {row['sample_id']: name for name, row in cells.items() if row['sample_id'] is not None}
truth = {row['variant_tag']: row['new_origin_segment'] for row in ledger['synthetic_truth_only']}
callmap = {(row['sample_id'], row['variant_tag']): row['call_state'] for row in ledger['variant_calls']}
check(len(callmap) == 6 and set(callmap) == {(sample, target) for sample in samples for target in truth}, 'toy_complete_target_rows')
truth_descendants = {target: descendants(segment) for target, segment in truth.items()}
for (sample, target), state in callmap.items():
    check((state == 'toy_validated_alternate') == (samples[sample] in truth_descendants[target]), 'toy_inheritance_truth')
positive = {tag: [samples[s] for s in samples if callmap[s, tag] == 'toy_validated_alternate'] for tag in truth}
negative = {tag: [samples[s] for s in samples if callmap[s, tag] == 'toy_validated_reference'] for tag in truth}
check(positive == {'TOY_VARIANT_A': ['A2', 'A11'], 'TOY_VARIANT_B': ['B21']}, 'toy_observed_carriers')
check(sum(map(len, positive.values())) == 3 and len(truth) == 2, 'toy_copies_versus_simulated_origins')
check(len(positive['TOY_VARIANT_A']) == 2 and len(negative['TOY_VARIANT_A']) == 1 and all(name in truth_descendants['TOY_VARIANT_A'] for name in positive['TOY_VARIANT_A']) and negative['TOY_VARIANT_A'][0] not in truth_descendants['TOY_VARIANT_A'], 'toy_branch_support')
check(len(positive['TOY_VARIANT_B']) == 1 and ledger['origin_assignments'][1]['classification'] == 'leaf_ambiguous_not_an_admitted_origin', 'toy_leaf_ambiguity')
check(rules['minimum_positive_descendants'] == 2 and rules['minimum_negative_outgroup_descendants'] == 1 and rules['ancestor_reference_status'] == 'simulated_only', 'toy_locked_predicate_scope')
check(ledger['toy_rules_sha256'] == digest(BASE/'TOY_RULES.json'), 'toy_rule_hash')
for key, value in ledger['design_status'].items():
    if key.startswith('actual_') and key != 'actual_registry_fields_resolved':
        check(value is None, 'actual_choices_NULL')
check(ledger['design_status']['actual_registry_fields_resolved'] == 0 and ledger['stage_control_measurements'] == [] and ledger['event_inclusion_control_measurements'] == [], 'actual_inputs_and_controls_unresolved')
matrix = json.loads((BASE/'REQUIREMENT_MATRIX.json').read_bytes())
check(len(matrix['requirements']) == 13 and matrix['all_actual_study_requirements_fulfilled'] is False, 'requirement_matrix_scope')
for row in matrix['requirements']:
    check(row['candidate_requirement_status'] == 'unresolved' and set(row['primary_paragraph_anchors']) <= {anchor['body_paragraph_index'] for anchor in source['verified_anchors']}, 'requirement_mappings')
weights = {mask: Fraction(1, 8) for mask in range(8)}
OR = sum(weight for mask, weight in weights.items() if mask & 3)
branch = sum(weight for mask, weight in weights.items() if mask & 3 == 3 and mask & 4)
check(OR == Fraction(3, 4) and branch == Fraction(1, 8), 'OR_vs_two_carriers_plus_noncarrier')
check(OR != branch, 'capture_predicates_not_exchangeable')
receipt = {'candidate': 'R000019', 'status': 'independent_core_semantic_checks_passed_pending_final_packaging_pin', 'checks': CHECKS, 'check_total': sum(CHECKS.values()), 'sources': source_receipts, 'synthetic_reconstruction': {'tracked_cells': 13, 'observed_divisions': 6, 'tracked_cell_time': '20', 'nested_stages': stages, 'unsequenced_terminal_genotypes_unknown': sorted(unknown), 'validated_inherited_copies': 3, 'true_origins_known_only_from_simulation': 2, 'branch_supported_origin_hypotheses': 1, 'leaf_ambiguous_hypotheses': 1}, 'predicate_boundary_example': {'scope': 'exact synthetic review illustration only', 'frame': 'two true carriers plus one noncarrier; independent correct target-call marginals 1/2', 'R20_any_carrier_call': str(OR), 'R19_toy_two_carriers_plus_noncarrier_call': str(branch), 'source_complete_native_caller_reproduced': False}}
(REVIEW/'R19_SEMANTIC_CHECKS_PRELIMINARY.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({'check_total': receipt['check_total'], 'checks': CHECKS}))
