"""v0.5 development-preview and multilingual public-CLI boundary tests.

All real GF generation still requires Windows gf.exe and a compiled PGF.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from console.semantik import SemantikClient


def fixture_client(tmp_path):
    reports=tmp_path/'Downloads'/'Ars_Magna_Defluens'/'practical_pilot_runs'
    return SemantikClient({'reports':str(reports),'semantik':str(tmp_path/'sa'),
                           'wordbench':str(tmp_path/'wordbench'),'gf':str(tmp_path/'gf.exe')})


def write_candidate(client):
    root=client._candidate_dir()
    root.mkdir(parents=True)
    hashes={}
    for n in ['grammar.pgf','bridge.json','lexicon.json','profile.json','conformance.suite.json']:
        b=(n+':test').encode('utf-8')
        (root/n).write_bytes(b)
        hashes[n]=hashlib.sha256(b).hexdigest()
    (root/'pipeline.lock.json').write_text(json.dumps({'runtime_set_id':'konstellation-fr-3','inputs':hashes}))
    (root/'build-report.json').write_text(json.dumps({'status':'PGF_BUILT_CANDIDATE_ONLY'}))
    return root


def test_candidate_status_fails_closed_on_tamper(tmp_path):
    c=fixture_client(tmp_path)
    assert c.candidate_status()['ready'] is False
    root=write_candidate(c)
    assert c.candidate_status()['ready'] is True
    (root/'grammar.pgf').write_text('tampered')
    assert c.candidate_status()['ready'] is False


def test_preview_requires_real_candidate_before_invoking_sa(tmp_path,monkeypatch):
    c=fixture_client(tmp_path)
    monkeypatch.setattr(c,'_call',lambda *args,**kwargs: (_ for _ in ()).throw(AssertionError('Should not call SA')))
    result=c.preview_candidate({'x':1})
    assert result['ok'] is False and result['status']=='CANDIDATE_NOT_READY'


def test_multilingual_preserves_request_and_delegates(tmp_path,monkeypatch):
    c=fixture_client(tmp_path)
    sa=tmp_path/'sa'/'src'/'semantik_architect'/'adapters'/'inbound'/'cli'
    sa.mkdir(parents=True)
    (sa/'main.py').write_text('# present')
    original={'context':{'target_language':'fr','target_locale':'fr-CA'},
              'runtime_selector':{'runtime_set_id':'fr-legacy'},'obligations':[{'id':'o1'}]}
    before=copy.deepcopy(original)
    calls=[]
    def runner(root,module,argv,*,payload,**kwargs):
        calls.append((argv,copy.deepcopy(payload)))
        return {'ok':payload['context']['target_language']=='fr','exit_code':0 if payload['context']['target_language']=='fr' else 2,
                'result':{'plain_text':'Phrase issue de SA'} if payload['context']['target_language']=='fr'
                else {'code':'SA-RUN-001','message_safe':'Runtime not released'}}
    monkeypatch.setattr(c,'_call',runner)
    output=c.render_many(original,['fr','de'])
    assert original==before
    assert [x['language'] for x in output['results']]==['fr','de']
    assert output['success_count']==1
    assert output['results'][0]['text']=='Phrase issue de SA'
    assert output['results'][1]['text'] is None
    assert all('runtime_selector' not in payload for _argv,payload in calls)
    assert all(argv[-2:]==['render','-'] for argv,_payload in calls)


def test_reject_unbounded_languages(tmp_path):
    c=fixture_client(tmp_path)
    try:
        c.render_many({'context':{}},['fr','fr'])
    except ValueError as exc:
        assert 'distinct' in str(exc)
    else:
        raise AssertionError('duplicate language accepted')
