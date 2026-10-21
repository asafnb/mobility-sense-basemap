"""Monthly Hatzav check: ask data.gov.il whether any active layer changed since its registered version.
Usage: python scripts/check_hatzav.py            # report only (no downloads, nothing written)
       python scripts/check_hatzav.py --apply    # download + register new versions for the changed layers
Next steps after --apply: publish.py plan layers -> make_base.py v<N> -> build_base.py -> ask Asaf which projects to upgrade."""
import os,sys,json,subprocess; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
reg=registry(); changed=[]
for lid,L in reg['layers'].items():
    if L['status']!='active' or not L['source'].get('ckan_api'): continue
    r=subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'add_layer_version.py'),lid,'--fetch','--dry-run'],capture_output=True,text=True)
    out=(r.stdout+r.stderr).strip().splitlines(); print(" | ".join(out[-2:]))
    if any('CHANGED' in x for x in out): changed.append(lid)
print("changed:",changed or "none")
if changed and '--apply' in sys.argv:
    for lid in changed: subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'add_layer_version.py'),lid,'--fetch'],check=True)
