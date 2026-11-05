"""Defluens acceptance contracts: no fake GF success and no auto-release."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from console.acceptance import EXPECTED_OPERATIONS, CoreAcceptance, acceptance_matrix, save_report


def catalog():
    return {
        'languages': {'fr': {},'en':{}}, 'subjects':['mira','lea','noa'],
        'objects':['book','document','flower'], 'polarities':['positive','negative'],
        'tenses':['present','past','future'],
        'intents':{
            intent: {'operation':operation, 'options':['first','last'],
                     **({'requires_object':True} if intent=='transitive' else {}),
                     **({'requires_subject':False,'supports_tense':False} if intent=='directive' else {})}
            for intent,operation in EXPECTED_OPERATIONS.items()
        },
    }


def fake_client():
    c=MagicMock()
    c.core_catalog.return_value={'ok':True,'result':catalog()}
    def batch(vectors):
        rows=[]
        for vec in vectors:
            lang=vec['recipe']['language']; items=vec['recipe']['items']
            if ':reject:' in vec['case_id']:
                rows.append({'case_id':vec['case_id'],'ok':False,'validated':False})
                continue
            req={'request_id':'sha256:fixture','capability_profile':f'defluens-core-{lang}-1',
                 'runtime_selector':{'runtime_set_id':f'defluens-core-{lang}-1'},
                 'context':{'target_language':lang},
                 'semantic_graph':{'statements':[{'id':f's{i}', 'polarity':item['polarity']}
                                                 for i,item in enumerate(items,1)]},
                 'obligations':[{'obligation_id':f'o{i}','semantic_refs':[f's{i}'],'ordering':'FIXED'}
                                for i in range(1,len(items)+1)]}
            rows.append({'case_id':vec['case_id'],'ok':True,'validated':True,'request':req})
        return {'ok':True,'result':{'schema_id':'semantik.defluens-core-batch','results':rows}}
    c.core_batch.side_effect=batch
    c.core_status.return_value={'languages':{'fr':{'ready':False},'en':{'ready':False}}}
    return c


def test_matrix_36_vectors_languages_and_bounds():
    p,n=acceptance_matrix(catalog())
    assert len(p)==28 and len(n)==8
    assert len({x['case_id'] for x in p+n})==36
    assert {x['language'] for x in p+n}=={'fr','en'}
    assert {len(x['recipe']['items']) for x in p}=={1,3,8}


def test_structural_does_not_claim_gf_success():
    client=fake_client()
    report=CoreAcceptance(client).run()
    assert report['status']=='STRUCTURAL_PASS_ONLY'
    assert report['structural_passed'] is True
    assert report['real_gf_candidate_passed'] is False
    assert report['totals']=={'authorized':28,'expected_rejections':8,
                              'structurally_validated':28,'gf_candidates_verified':0,
                              'blocked_pgf':0,'failed':0}
    client.preview_candidate.assert_not_called()
    assert report['released'] is False and report['activated'] is False


def test_real_requires_locked_pgf_before_any_gf_call():
    client=fake_client()
    report=CoreAcceptance(client).run('real')
    assert report['status']=='BLOCKED_PGF'
    assert report['totals']['blocked_pgf']==28
    assert report['totals']['gf_candidates_verified']==0
    assert not report['real_gf_candidate_passed']
    client.preview_candidate.assert_not_called()


def test_real_cannot_ignore_missing_coverage():
    client=fake_client()
    client.core_status.return_value={'languages':{'fr':{'ready':True},'en':{'ready':True}}}
    client.preview_candidate.return_value={
        'ok':True,'result':{'status':'CANDIDATE_PREVIEW','released':False,'activated':False,
                            'communication_result':{'runtime':{'runtime_set_id':'defluens-core-fr-1'},
                                                    'plain_text':'Fixture only','coverage':[]}}}
    report=CoreAcceptance(client).run('real')
    assert report['status']=='FAILED'
    assert report['totals']['gf_candidates_verified']==0
    assert not report['real_gf_candidate_passed']


def test_fail_closed_on_inconsistent_batch():
    client=fake_client()
    client.core_batch.return_value={'ok':True,'result':{'schema_id':'semantik.defluens-core-batch','results':[]}}
    client.core_batch.side_effect=None
    with pytest.raises(RuntimeError,match='incomplete'):
        CoreAcceptance(client).run('structural')


def test_no_overwrite_reports(tmp_path):
    p=tmp_path/'nested'/'audit.json'
    save_report({'status':'STRUCTURAL_PASS_ONLY'},p)
    before=p.read_bytes()
    with pytest.raises(FileExistsError):save_report({'status':'FAILED'},p)
    assert p.read_bytes()==before


def test_missing_operation_fails_catalog():
    c=catalog()
    c['intents']['event']['operation']='invented'
    with pytest.raises(ValueError,match='event'):acceptance_matrix(c)


def test_real_can_pass_only_upstream_candidate_with_exact_coverage():
    client=fake_client()
    client.core_status.return_value={'languages':{'fr':{'ready':True,'pgf_sha256':'f'*64},
                                                   'en':{'ready':True,'pgf_sha256':'e'*64}}}
    def preview(request, runtime):
        return {'ok':True,'result':{'status':'CANDIDATE_PREVIEW','released':False,'activated':False,
            'communication_result':{'runtime':{'runtime_set_id':runtime},
                                    'plain_text':'FIXTURE ONLY – NOT GF',
                                    'coverage':[{'obligation_id':x['obligation_id']} for x in request['obligations']]}}}
    client.preview_candidate.side_effect=preview
    report=CoreAcceptance(client).run('real')
    assert report['status']=='REAL_GF_CANDIDATE_PASS'
    assert report['real_gf_candidate_passed']
    assert report['totals']['gf_candidates_verified']==28
    assert client.preview_candidate.call_count==28
    assert report['released'] is False and not report['linguistically_certified']
    # The fixture verifies reporting only, not actual GF.
