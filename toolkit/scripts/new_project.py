"""Create a new project folder from the latest base.
Usage: python scripts/new_project.py <slug> "<כותרת>" --center LNG,LAT [--zoom 14] [--bbox W,S,E,N] [--group-name "..."]
Creates projects/<slug>/project.json + layers/ and prints the Drive folder plan (folder is created by the agent with the Drive connector)."""
import os,sys,argparse,glob; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
ap=argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('title'); ap.add_argument('--center',required=True); ap.add_argument('--zoom',type=float,default=14)
ap.add_argument('--bbox'); ap.add_argument('--group-name'); ap.add_argument('--base')
a=ap.parse_args(); d=f"{ROOT}/projects/{a.slug}"
if os.path.exists(d): sys.exit(f"{d} exists")
bases=sorted(glob.glob(f"{ROOT}/base/v*/manifest.json"),key=lambda p:int(p.split('/')[-2][1:]))
bv=a.base or load_json(bases[-1])['base_version']; c=[float(x) for x in a.center.split(',')]
gid="g_"+a.slug.replace('-','_')
P=dict(slug=a.slug,title=a.title,project_version=1,base_version=bv,created=today(),
  map_view=dict(center=c,zoom=a.zoom),bbox=[float(x) for x in a.bbox.split(',')] if a.bbox else None,
  bookmarks=[dict(id=a.slug,name=a.title,lng=c[0],lat=c[1],zoom=a.zoom)],
  groups=[dict(id=gid,name=a.group_name or a.title,parent="g_proj")],layers=[],style_overrides={},hide_base_layers=[],
  drive=dict(parent_folder_id="1kQNcrF_oRPg-XthWZCxcrWLp6kh57zOM",parent_folder_name="חצב/פרויקטים",folder_name=a.title,folder_id=None,
     geolibre_folder_id="1FXJJjrB6ppsCjv1HFHneKLkIGdqTmEQp"),
  history=[],builds=[],
  _doc="layers[]: id,title,group,version,file (layers/<id>_<YYYY-MM>.geojson),style (כמו style.json),popup{title_field,fields},attribution,lineage,web{fields,merge}")
os.makedirs(f"{d}/layers"); save_json(f"{d}/project.json",P)
open(f"{d}/README.md","w").write(f"# {a.title}\n\nבסיס: {bv}. שכבות הפרויקט ב־layers/. ראו README הראשי.\n")
print("created",d); print(f"Drive plan: create folder '{a.title}' under {P['drive']['parent_folder_name']} ({P['drive']['parent_folder_id']}), then set drive.folder_id in project.json")
