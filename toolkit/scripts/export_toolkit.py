"""List the files that go to GitHub under toolkit/ (scripts, style, registries, manifests, README, small data only).
Usage: python scripts/export_toolkit.py > /tmp/toolkit_files.json"""
import os,sys,json,glob; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
reg=registry(); files=[]
pats=["README.md","requirements.txt",".gitignore","scripts/*.py","style/*.json","style/versions/*.json","layers/layers.json","base/CHANGELOG.md","base/*/manifest.json",
      "projects/*/project.json","projects/*/README.md","projects/*/history/*.json","publish/*.json"]
for p in pats: files+=sorted(glob.glob(f"{ROOT}/{p}"))
for lid,L in reg['layers'].items():
    for v in L['versions']:
        if v['storage'].startswith('github'): files.append(f"{ROOT}/{v['file']}")
for P in glob.glob(f"{ROOT}/projects/*/layers/*.geojson"):
    if os.path.getsize(P)<=reg['github_size_limit_bytes']: files.append(P)
out=[dict(local=f,path="toolkit/"+os.path.relpath(f,ROOT),bytes=os.path.getsize(f)) for f in files]
print(json.dumps(out,ensure_ascii=False,indent=1)); print(f"total {sum(o['bytes'] for o in out)/1e6:.2f} MB in {len(out)} files",file=sys.stderr)
