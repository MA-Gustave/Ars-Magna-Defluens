"""Local UI contract: only semantic checks in HTTP, never real GF."""
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

from console.core import Settings
from console.server import start
from console.qualification import CoreQualification
from test_acceptance_v010 import fake_client


def test_local_qualification_route_token_and_real_mode_guard(tmp_path):
    defaults={k:str(tmp_path/k) for k in ('wordbench','observatory','compendium','rgl','gf','reports','alignment')}
    settings=Settings(tmp_path/'settings.json', defaults=defaults)
    server=start(open_browser=False, settings=settings)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        # Replace *only* the upstream client with deterministic double; the
        # HTTP route and immutable artifact writing execute as shipped.
        server.console_app.core_qualification=CoreQualification(fake_client())
        host=f'http://127.0.0.1:{server.server_address[1]}'
        def post(mode,token):
            return urllib.request.urlopen(urllib.request.Request(
                host+'/api/semantik/core-qualification',
                data=json.dumps({'mode':mode}).encode(),
                headers={'X-Defluens-Token':token,'Content-Type':'application/json'},
                method='POST'),timeout=5)
        with urllib.request.urlopen(host+'/') as response:
            assert 'v011-audit' in response.read().decode()
        try:
            post('structural','INVALID')
        except urllib.error.HTTPError as error:
            assert error.code==403
        else:
            raise AssertionError('HTTP token bypassed')
        with post('structural',server.console_app.token) as response:
            result=json.load(response)
        assert result['status']=='STRUCTURAL_PASS_ONLY'
        assert result['totals']['parity_pairs']==14
        assert result['real_gf_candidate_passed'] is False
        assert Path(result['report_path']).is_file()
        assert Path(result['review_path']).is_file()
        try:
            post('real',server.console_app.token)
        except urllib.error.HTTPError as error:
            assert error.code==400
        else:
            raise AssertionError('Browser triggered GF real mode')
    finally:
        server.shutdown()
        server.server_close()

