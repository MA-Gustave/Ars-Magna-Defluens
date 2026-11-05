"""Optional quiet Windows launcher. Double-click or use pyw -3 Ars_Magna_Defluens.pyw."""
from pathlib import Path
import os
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from console.server import main
if __name__=='__main__':
    try:main()
    except Exception as exc:
        try:
            from console.core import local_state_dir
            p=local_state_dir()/'launcher_error.log'
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(str(exc),encoding='utf-8')
        except OSError:pass
