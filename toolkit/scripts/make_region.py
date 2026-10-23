"""Freeze a regional layer pack version: regions/<id>/<ver>/manifest.json (immutable) from regions/<id>/region.json.
Usage: python scripts/make_region.py jerusalem j1 [--pin LAYER=VERSION] [--note "..."]
A region pack = region-only layers (registry scope 'region:<id>') + their group placement, legend order and bookmarks.
It sits between the national base and a project: compose(base, regions=[...], projects=[...]).
Each layer is pinned to its registry 'current' version unless --pin is given."""
import os,sys,json,argparse; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
ap=argparse.ArgumentParser(); ap.add_argument('region'); ap.add_argument('version'); ap.add_argument('--pin',action='append',default=[]); ap.add_argument('--note',default='')
a=ap.parse_args(); reg=registry(); d=f"{ROOT}/regions/{a.region}"; D=load_json(f"{d}/region.json")
if not re.fullmatch(r'[a-z]\d+',a.version): sys.exit("region version: letter + number, e.g. j1")
out=f"{d}/{a.version}/manifest.json"
if os.path.exists(out): sys.exit(f"{out} exists – region versions are immutable; use the next number")
prev=load_json(f"{d}/{D['current']}/manifest.json") if D.get('current') else None
pins=dict(p.split('=') for p in a.pin); S=load_style(released_styles()[-1]); layers=[]
for e in D['layers']:
    L=reg['layers'][e['id']]
    if L.get('scope')!=f"region:{a.region}": print(f"WARNING {e['id']}: registry scope is {L.get('scope')!r}, expected region:{a.region}")
    if e['id'] not in S['layers']: sys.exit(f"{e['id']}: no style spec in {S['style_version']}")
    ver=pins.get(e['id'],L['current']); layer_version(reg,e['id'],ver); layers.append(dict(id=e['id'],version=ver,group=e['group']))
M=dict(region=a.region,region_version=a.version,title=D['title'],description=D['description'],created=today(),previous=prev and prev['region_version'],
  style_min=D['style_min'],map_view=D['map_view'],bbox=D.get('bbox'),groups=D['groups'],layers=layers,legend_order=D.get('legend_order'),bookmarks=D['bookmarks'],note=a.note,outputs={})
save_json(out,M); D['current']=a.version; save_json(f"{d}/region.json",D)
ch=[f"## {a.version} – {today()}"]
pv={l['id']:l['version'] for l in prev['layers']} if prev else {}
for l in layers:
    if l['id'] not in pv: ch.append(f"- שכבה: `{l['id']}` ({l['version']}) → קבוצה {l['group']}")
    elif pv[l['id']]!=l['version']: ch.append(f"- `{l['id']}`: {pv[l['id']]} → {l['version']}")
for i in pv:
    if i not in {l['id'] for l in layers}: ch.append(f"- שכבה הוסרה: `{i}`")
if a.note: ch.append(f"- הערה: {a.note}")
cp=f"{d}/CHANGELOG.md"; old=open(cp).read() if os.path.exists(cp) else f"# CHANGELOG – חבילה אזורית {D['title']} ({a.region})\n\n"
head,_,rest=old.partition("\n\n"); open(cp,'w').write(head+"\n\n"+"\n".join(ch)+"\n\n"+rest)
print("created",out); print("\n".join(ch))
