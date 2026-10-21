"""Create a new base version manifest = style version + pinned layer versions.
Usage: python scripts/make_base.py v4 [--style s2] [--add LAYER] [--remove LAYER] [--pin LAYER=VERSION] [--note "..."]
Defaults: latest released style, the 'current' version of every layer in the previous base (+ --add)."""
import os,sys,json,argparse,glob; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
ap=argparse.ArgumentParser(); ap.add_argument('version'); ap.add_argument('--style'); ap.add_argument('--from',dest='prev')
ap.add_argument('--add',action='append',default=[]); ap.add_argument('--remove',action='append',default=[]); ap.add_argument('--pin',action='append',default=[]); ap.add_argument('--note',default='')
a=ap.parse_args(); reg=registry()
out=f"{ROOT}/base/{a.version}/manifest.json"
if os.path.exists(out): sys.exit(f"{a.version} exists – base versions are immutable")
bases=sorted(glob.glob(f"{ROOT}/base/v*/manifest.json"),key=lambda p:int(p.split('/')[-2][1:]))
prev=load_json(f"{ROOT}/base/{a.prev}/manifest.json") if a.prev else (load_json(bases[-1]) if bases else None)
styles=sorted(glob.glob(f"{ROOT}/style/versions/style_s*.json"),key=lambda p:int(p.split('_s')[-1][:-5]))
sv=a.style or load_json(styles[-1])['style_version']; load_style(sv)
ids=[l['id'] for l in prev['layers']] if prev else []
ids=[i for i in ids if i not in a.remove]+[i for i in a.add if i not in ids]
pins=dict(p.split('=') for p in a.pin)
layers=[dict(id=i,version=pins.get(i,reg['layers'][i]['current'])) for i in ids]
for l in layers: layer_version(reg,l['id'],l['version'])
M=dict(base_version=a.version,created=today(),name=prev['name'] if prev else "Mobility Sense – מפת בסיס ישראל",
  description=prev['description'] if prev else "",previous=prev and prev['base_version'],style_version=sv,layers=layers,
  map_view=prev['map_view'] if prev else dict(center=[34.95,31.45],zoom=7.2),bookmarks=prev['bookmarks'] if prev else [],note=a.note,outputs={})
save_json(out,M)
# changelog
ch=[f"## {a.version} – {today()}"]
if prev:
    pv={l['id']:l['version'] for l in prev['layers']}; nv={l['id']:l['version'] for l in layers}
    if prev['style_version']!=sv: ch.append(f"- עיצוב: {prev['style_version']} → {sv}")
    for i in nv:
        if i not in pv: ch.append(f"- שכבה נוספה: `{i}` ({nv[i]})")
        elif pv[i]!=nv[i]:
            L,v=layer_version(reg,i,nv[i]); ch.append(f"- `{i}`: {pv[i]} → {nv[i]}"+(f" – {v.get('changes')}" if v.get('changes') else ""))
    for i in pv:
        if i not in nv: ch.append(f"- שכבה הוסרה: `{i}`")
if a.note: ch.append(f"- הערה: {a.note}")
if len(ch)==1: ch.append("- ללא שינוי בשכבות/עיצוב")
cp=f"{ROOT}/base/CHANGELOG.md"; old=open(cp).read() if os.path.exists(cp) else "# CHANGELOG – מפת הבסיס\n\n"
head,_,rest=old.partition("\n\n"); open(cp,'w').write(head+"\n\n"+"\n".join(ch)+"\n\n"+rest)
print("created",out); print("\n".join(ch))
