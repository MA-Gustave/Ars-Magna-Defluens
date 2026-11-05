"""Defluens only orchestrates real WordBench / SemantiK public entry points."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from console.semantik import SemantikClient


def make_client(tmp_path):
    wb=tmp_path/'wb'; sa=tmp_path/'sa'; rgl=tmp_path/'rgl';
    (wb/'src/gf_wordbench/practical').mkdir(parents=True)
    (wb/'src/gf_wordbench/practical/pilot.py').write_text('# present')
    (wb/'tools').mkdir()
    (wb/'tools/preview_defluens_capability.py').write_text('# present')
    (sa/'src/semantik_architect/adapters/inbound/cli').mkdir(parents=True)
    (sa/'src/semantik_architect/adapters/inbound/cli/main.py').write_text('# present')
    (rgl/'src').mkdir(parents=True)
    gf=tmp_path/'gf.exe';gf.write_bytes(b'fixture-not-gf')
    c=SemantikClient({'wordbench':str(wb),'semantik':str(sa),'gf':str(gf),
                     'rgl':str(rgl),'reports':str(tmp_path/'reports')})
    return c


def test_capability_catalog_calls_sa_public_cli(tmp_path,monkeypatch):
    c=make_client(tmp_path);called=[]
    def fake_call(root,module,args,**kw):
        called.append((module,args))
        return {'ok':True,'result':{'total':15}}
    monkeypatch.setattr(c,'_call',fake_call)
    assert c.practical_intents()['result']['total']==15
    assert called[0][1][-1]=='defluens-intents'


def test_single_preview_rejects_invalid_selection(tmp_path):
    c=make_client(tmp_path)
    for lang,cap in [('Fre','made-up'),('../Fre','factual-present')]:
        try:c.practical_preview(lang,cap)
        except ValueError:pass
        else:raise AssertionError('Invalid untrusted selection admitted')


def test_single_preview_runs_wordbench_and_keeps_raw_evidence(tmp_path,monkeypatch):
    c=make_client(tmp_path);seen=[]
    class FakeProcess:
        returncode=0;stderr='';stdout=json.dumps({'status':'candidate_for_review',
                    'language':'Fre','capability':'factual-negation',
                    'candidate':"Mira n' &+ est pas prête",'gf_executed':True,'released':False})
    def fake_run(cmd,**kwargs):
        seen.append((cmd,kwargs));return FakeProcess()
    import console.semantik as target
    monkeypatch.setattr(target.subprocess,'run',fake_run)
    result=c.practical_preview('Fre','factual-negation')
    assert result['ok'] and result['readable']=="Mira n'est pas prête"
    assert result['candidate']=="Mira n' &+ est pas prête"
    assert result['released'] is False
    cmd,kw=seen[0]
    assert '--capability' in cmd and cmd[cmd.index('--capability')+1]=='factual-negation'
    assert kw['shell'] is False
