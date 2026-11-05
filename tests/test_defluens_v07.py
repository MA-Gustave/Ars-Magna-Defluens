"""Defluens uses public SA and WordBench commands; never generates text locally."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from console.semantik import SemantikClient


def make_client(tmp_path):
    wb=tmp_path/'wb';sa=tmp_path/'sa';rgl=tmp_path/'rgl'
    (wb/'src/gf_wordbench/practical').mkdir(parents=True)
    (wb/'src/gf_wordbench/practical/batch.py').write_text('# public')
    (wb/'tools').mkdir();(wb/'tools/build_semantik_profile3_candidate.py').write_text('# builder')
    (sa/'src/semantik_architect/adapters/inbound/cli').mkdir(parents=True)
    (sa/'src/semantik_architect/adapters/inbound/cli/main.py').write_text('# cli')
    (rgl/'src/api').mkdir(parents=True)
    (rgl/'src/api/SyntaxFre.gf').write_text('# gf')
    gf=tmp_path/'gf.exe';gf.write_bytes(b'STUB')
    return SemantikClient({'wordbench':str(wb),'semantik':str(sa),'gf':str(gf),
        'rgl':str(rgl),'reports':str(tmp_path/'reports')})


def test_attribute_request_is_a_public_sa_call(tmp_path,monkeypatch):
    c=make_client(tmp_path);seen=[]
    def fake_call(root,module,argv,**kw):
        seen.append(argv);return {'ok':True,'result':{'capability_profile':'defluens-attribute-fr-1'}}
    monkeypatch.setattr(c,'_call',fake_call)
    assert c.attribute_request('mira','ready','negative','past')['ok']
    assert 'defluens-attribute-request' in seen[0]
    assert '--polarity' in seen[0] and 'negative' in seen[0]


def test_preview_routes_to_candidate_not_production(tmp_path,monkeypatch):
    c=make_client(tmp_path)
    monkeypatch.setattr(c,'candidate_status',lambda x:{'ready':True,'candidate_dir':str(tmp_path)})
    argv=[]
    monkeypatch.setattr(c,'_call',lambda root,module,args,**kw:(argv.extend(args) or {'ok':False,'result':{'code':'SA-LEX-002'}}))
    result=c.preview_candidate({'schema_version':'1.0'},'defluens-attribute-fr-1')
    assert not result['ok']
    assert 'preview-candidate' in argv and 'defluens-attribute-fr-1' in argv


def test_missing_candidate_remains_unavailable(tmp_path):
    c=make_client(tmp_path)
    assert c.candidate_status('defluens-attribute-fr-1')['ready'] is False
    assert c.preview_candidate({'schema_version':'1.0'},'defluens-attribute-fr-1')['ok'] is False
