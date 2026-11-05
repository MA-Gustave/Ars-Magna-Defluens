from pathlib import Path
from console.lexical import LexicalCoordinator
from console.core import Settings


def test_settings_detect_local_dik_layout(tmp_path):
    dik=tmp_path/'diK'/'diK'/'src'/'dik';dik.mkdir(parents=True)
    (dik/'cli.py').write_text('')
    defaults={'dik':str(tmp_path/'diK')}
    from console.core import default_paths
    defaults={**default_paths(),**defaults}
    settings=Settings(store=tmp_path/'none.json',defaults=defaults)
    assert settings.health()['dik'] is True


def test_local_cli_handoff_respects_ownership(tmp_path, monkeypatch):
    root=tmp_path/'diK'/'diK'
    (root/'src'/'dik').mkdir(parents=True)
    (root/'src'/'dik'/'cli.py').write_text('')
    obs=tmp_path/'obs';obs.mkdir();(obs/'lexemes.jsonl').write_text('{}\n')
    calls=[]
    def fake_exec(root,module,args,timeout=120):
        calls.append((module,args))
        return {'ok':True,'result':{'status':'CANDIDATE_ONLY'},'exit_code':0}
    monkeypatch.setattr(LexicalCoordinator,'_exec',staticmethod(fake_exec))
    coord=LexicalCoordinator({'dik':str(root.parent),'reports':str(tmp_path/'reports'/'practical_pilot_runs')})
    result=coord.diK_handoff(str(obs),'fr')
    assert result['ok'] and result['released'] is False
    assert len(calls)==2 and calls[0][1][0:2]==['world','gf-handoff']
    assert calls[1][1][0:2]==['world','semantik-knowledge']


def test_wrong_dik_input_fails_closed(tmp_path):
    root=tmp_path/'diK'/'diK'; (root/'src'/'dik').mkdir(parents=True)
    (root/'src'/'dik'/'cli.py').write_text('')
    coord=LexicalCoordinator({'dik':str(root.parent),'reports':str(tmp_path/'reports'/'x')})
    try:
        coord.diK_handoff(str(tmp_path/'missing'),'fr')
        assert False
    except FileNotFoundError:
        pass
