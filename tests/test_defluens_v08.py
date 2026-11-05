"""Defluens is a public-command client. It must not implement a second GF renderer."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from console.semantik import SemantikClient

@pytest.fixture
def client(tmp_path):
    sa=tmp_path/'sa';(sa/'src/semantik_architect/adapters/inbound/cli').mkdir(parents=True)
    (sa/'src/semantik_architect/adapters/inbound/cli/main.py').write_text('# stub')
    wb=tmp_path/'wb';(wb/'src/gf_wordbench/practical').mkdir(parents=True)
    (wb/'src/gf_wordbench/practical/batch.py').write_text('# stub')
    (wb/'tools').mkdir();(wb/'tools/build_semantik_profile3_candidate.py').write_text('# stub')
    (tmp_path/'rgl/src/api').mkdir(parents=True)
    (tmp_path/'rgl/src/api/SyntaxFre.gf').write_text('stub')
    gf=tmp_path/'gf.exe';gf.write_bytes(b'FAKE')
    return SemantikClient({'semantik':str(sa),'wordbench':str(wb),'rgl':str(tmp_path/'rgl'), 'gf':str(gf),'reports':str(tmp_path/'reports')})

def test_core_canonical_request_only_via_public_cli(client,monkeypatch):
    calls=[]
    monkeypatch.setattr(client,'_call',lambda root,module,argv,**kw:(calls.append((argv,kw)) or {'ok':True,'result':{'schema_version':'1.0'}}))
    out=client.core_request({'language':'fr','items':[{'intent':'attribute','subject':'mira','concept':'ready'}]})
    assert out['ok'] and 'defluens-core-request' in calls[0][0]
    assert calls[0][1]['payload']['language']=='fr'

def test_core_preview_only_candidate_path(client,monkeypatch):
    monkeypatch.setattr(client,'core_request',lambda r:{'ok':True,'result':{'capability_profile':'defluens-core-fr-1'}})
    captured=[]
    monkeypatch.setattr(client,'preview_candidate',lambda request,runtime:(captured.append((request,runtime)) or {'ok':False,'status':'CANDIDATE_NOT_READY'}))
    outcome=client.core_preview({'language':'fr','items':[]})
    assert not outcome['ok'] and outcome['released'] is False
    assert captured[0][1]=='defluens-core-fr-1'

@pytest.mark.parametrize('lang', ['fr','en'])
def test_core_build_is_wordbench_delegate(client,monkeypatch,lang):
    seen=[]
    monkeypatch.setattr(client,'build_candidate',lambda profile:(seen.append(profile) or {'ok':False}))
    client.core_build(lang)
    assert seen==['defluens-core-'+lang+'-1']

def test_core_compare_cannot_claim_release(client,monkeypatch):
    monkeypatch.setattr(client,'core_preview',lambda r:{'ok':False,'result':{'error':'PGF NOT BUILT'}})
    out=client.core_preview_many({'language':'fr','items':[]},['fr','en'])
    assert not out['all_success'] and out['success_count']==0 and out['released'] is False
    assert all(not r['ok'] and r['text'] is None for r in out['results'])

def test_core_invalid_languages_rejected(client):
    with pytest.raises(ValueError):client.core_preview_many({},['fr','es'])
