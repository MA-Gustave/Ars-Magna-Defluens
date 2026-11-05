"""No GF is mocked as *real*. Doubles test protocol enforcement only."""
from __future__ import annotations
import csv
from pathlib import Path
import pytest

from test_acceptance_v010 import fake_client
from console.qualification import CoreQualification, _sha, write_qualification


def _valid_output(request, runtime, text='MOCK ONLY'):
    language = request['context']['target_language']
    obligations = request['obligations']
    blocks = [{'block_id':f'b{i}', 'kind':'utterance', 'text':text+str(i),
               'obligation_ids':[row['obligation_id']]}
              for i,row in enumerate(obligations,1)]
    coverage = [{'obligation_id':row['obligation_id'], 'block_ids':[f'b{i}'],
                 'realization_unit_ids':[f'u{i}']}
                for i,row in enumerate(obligations,1)]
    result = {'schema_version':'1.0', 'language': language,
              'locale':'fr-CA' if language=='fr' else 'en-CA',
              'blocks':blocks, 'coverage':coverage,
              'runtime':{'runtime_set_id':runtime,'capability_profile':runtime,
                         'sa_version':'1.0.0','sa_gf_contract_version':'1.0'},
              'plain_text':'\n'.join(b['text'] for b in blocks)}
    result['deterministic_result_id'] = 'sha256:' + _sha(result)
    return result


def mock_ready():
    client = fake_client()
    original_batch = client.core_batch.side_effect
    def normalized_batch(vectors):
        response = original_batch(vectors)
        for entry in response['result']['results']:
            if 'request' in entry:
                lang = entry['request']['context']['target_language']
                entry['request']['context']['target_locale'] = 'fr-CA' if lang == 'fr' else 'en-CA'
        return response
    client.core_batch.side_effect = normalized_batch
    client.core_status.return_value = {'languages':{
        'fr':{'ready':True,'pgf_sha256':'f'*64,'pipeline_lock_sha256':'a'*64},
        'en':{'ready':True,'pgf_sha256':'e'*64,'pipeline_lock_sha256':'b'*64},
    }}

    def batch(vectors, runtime):
        lang = 'fr' if runtime.endswith('fr-1') else 'en'
        rows = [{'case_id':v['case_id'], 'ok':True,
                 'communication_result':_valid_output(v['request'], runtime)}
                for v in vectors]
        return {'ok':True, 'result':{
            'schema_id':'semantik.candidate-preview-batch', 'status':'CANDIDATE_PREVIEW_BATCH',
            'runtime_set_id':runtime, 'candidate_only':True, 'released':False,
            'activated':False, 'linguistically_certified':False,
            'pgf_sha256':client.core_status.return_value['languages'][lang]['pgf_sha256'],
            'pipeline_lock_sha256':client.core_status.return_value['languages'][lang]['pipeline_lock_sha256'],
            'results':rows}}
    client.preview_candidate_batch.side_effect = batch
    return client


def test_structural_has_14_semantic_pairs_and_no_gf():
    c = mock_ready()
    report = CoreQualification(c).run()
    assert report['status'] == 'STRUCTURAL_PASS_ONLY'
    assert report['cross_language_parity_passed']
    assert report['totals']['parity_pairs'] == 14
    assert report['totals']['gf_candidates_verified'] == 0
    assert report['released'] is False and report['linguistically_certified'] is False
    c.preview_candidate_batch.assert_not_called()


def test_real_blocked_when_both_pgf_missing():
    c = fake_client()
    report = CoreQualification(c).run('real')
    assert report['status'] == 'BLOCKED_PGF'
    assert report['totals']['blocked_pgf'] == 28
    assert report['totals']['gf_candidates_verified'] == 0
    c.preview_candidate_batch.assert_not_called()


def test_real_uses_two_locked_upstream_batches_not_28_processes():
    c = mock_ready()
    report = CoreQualification(c).run('real')
    assert report['status'] == 'REAL_GF_CANDIDATE_PASS'
    assert report['totals']['gf_candidates_verified'] == 28
    assert report['totals']['human_reviews_completed'] == 0
    assert c.preview_candidate_batch.call_count == 2
    assert all(len(call.args[0]) == 14 for call in c.preview_candidate_batch.call_args_list)
    assert all(x['human_review'] == 'PENDING' for x in report['cases'] if x['kind'] == 'authorized')
    assert not report['linguistically_certified']


def test_real_fails_closed_on_missing_block_and_hash_drift():
    c = mock_ready()
    original = c.preview_candidate_batch.side_effect
    def broken(vectors, runtime):
        r = original(vectors, runtime)
        if runtime.endswith('fr-1'):
            r['result']['results'][0]['communication_result']['blocks'].pop()
        return r
    c.preview_candidate_batch.side_effect = broken
    report = CoreQualification(c).run('real')
    assert report['status'] == 'FAILED'
    assert report['totals']['gf_candidates_verified'] == 27
    assert 'block' in next(x['error'] for x in report['cases'] if x['status'] == 'FAILED').lower()

    c = mock_ready()
    def hash_drift(vectors, runtime):
        r = mock_ready().preview_candidate_batch.side_effect(vectors, runtime)
        r['result']['pgf_sha256'] = '0' * 64
        return r
    c.preview_candidate_batch.side_effect = hash_drift
    report = CoreQualification(c).run('real')
    assert report['status'] == 'FAILED'
    assert report['totals']['gf_candidates_verified'] == 0


def test_cross_language_semantics_must_be_identical():
    c = fake_client()
    base = c.core_batch.side_effect
    calls = 0
    def corrupt_second_batch(vectors):
        nonlocal calls
        calls += 1
        answer = base(vectors)
        if calls == 1:
            target = next(x for x in answer['result']['results'] if x['case_id']=='en:attribute:positive')
            target['request']['semantic_graph']['graph_id'] = 'unexpected-en-only'
        return answer
    c.core_batch.side_effect = corrupt_second_batch
    report = CoreQualification(c).run()
    assert report['status'] == 'FAILED'
    assert not report['cross_language_parity_passed']
    assert report['totals']['failed'] == 2


def test_duplicate_batch_rows_are_not_accepted():
    c = mock_ready()
    orig = c.preview_candidate_batch.side_effect
    def dupe(vectors, runtime):
        result = orig(vectors, runtime)
        result['result']['results'][1]['case_id'] = result['result']['results'][0]['case_id']
        return result
    c.preview_candidate_batch.side_effect = dupe
    report = CoreQualification(c).run('real')
    assert report['status']=='FAILED'
    assert report['totals']['gf_candidates_verified'] == 0


def test_write_review_file_immutable_and_not_human_certification(tmp_path):
    report = CoreQualification(mock_ready()).run('real')
    p, sheet = write_qualification(report, tmp_path/'qualification.json')
    assert p.is_file() and sheet.is_file()
    with sheet.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    assert len(rows)==28
    assert all(x['human_review']=='PENDING' for x in rows)
    assert rows[0]['candidate_text'].startswith('MOCK ONLY')
    with pytest.raises(FileExistsError):
        write_qualification(report,p)


def test_tabular_formula_injection_escape(tmp_path):
    report = CoreQualification(mock_ready()).run('real')
    next(x for x in report['cases'] if x['kind'] == 'authorized')['candidate_text'] = '=1+2'
    _, sheet = write_qualification(report,tmp_path/'audit.json')
    with sheet.open(encoding='utf-8-sig',newline='') as f:
        rows = list(csv.DictReader(f,delimiter='\t'))
    assert rows[0]['candidate_text'] == "'=1+2"
