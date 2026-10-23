"""Move a project to a newer base version (and/or pin regional packs). Keeps project layers + overrides, bumps project_version,
archives the previous project.json in projects/<slug>/history/, builds the new versioned file. Old builds stay.
Usage: python scripts/upgrade_project.py har-hotzvim v5 [--region jerusalem=j1 ...] [--note "..."] [--no-build]
Project layers whose id is now provided by a pinned region pack (e.g. road22_jlm, hh_companies -> jerusalem j1) are removed
from the project (with their derived helper layers and legend entries); the region pack's registry version is used instead.
Their project-layer files stay in projects/<slug>/layers/ (history) – nothing is deleted."""
import os,sys,subprocess,argparse; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
ap=argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('base'); ap.add_argument('--region',action='append',default=[]); ap.add_argument('--note',default=''); ap.add_argument('--no-build',action='store_true')
a=ap.parse_args(); slug,nb=a.slug,a.base; P=project_cfg(slug); B=base_manifest(nb)
regions=list(P.get('regions',[]))
for r in a.region:
    rid,_,ver=r.partition('=')
    ver=ver or load_json(f"{ROOT}/regions/{rid}/region.json")['current']
    region_manifest(rid,ver); regions=[x for x in regions if x['id']!=rid]+[dict(id=rid,version=ver)]
if P['base_version']==nb and regions==P.get('regions',[]): sys.exit(f"{slug} already on {nb} with the same region packs")
R=[region_manifest(r['id'],r['version']) for r in regions]
S=load_style(B['style_version'])
for r in R:
    if style_key(B['style_version'])<style_key(r.get('style_min','s1.0')): sys.exit(f"region {r['region']} {r['region_version']} needs style ≥ {r['style_min']} (base {nb} has {B['style_version']})")
rids={e['id'] for r in R for e in r['layers']}
rderived={k for k,v in S['layers'].items() if v.get('source') in rids}
moved=[l['id'] for l in P['layers'] if l['id'] in rids]
dropped=[l['id'] for l in P['layers'] if l['id'] not in rids and (l.get('derived_from') in moved or l['id'] in rderived)]
save_json(f"{ROOT}/projects/{slug}/history/project_p{P['project_version']}__base_{P['base_version']}.json",P)
P['history'].append(dict(project_version=P['project_version'],base_version=P['base_version'],regions=P.get('regions',[]),archived=today(),
    **({"moved_to_region":moved,"dropped_helpers":dropped} if moved or dropped else {}),**({"note":a.note} if a.note else {})))
gone=set(moved)|set(dropped)
P['layers']=[l for l in P['layers'] if l['id'] not in gone]
lg=P.get('legend',{})
if 'order' in lg: lg['order']=[i for i in lg['order'] if i not in gone]
for k in ('customEntries','overrides'):
    if k in lg: lg[k]={i:v for i,v in lg[k].items() if i not in gone}
P['style_overrides']={k:v for k,v in P.get('style_overrides',{}).items() if k not in gone}
used={l['group'] for l in P['layers']}; P['groups']=[g for g in P['groups'] if g['id'] in used or any(x.get('parent')==g['id'] for x in P['groups'])]
ids={l['id'] for l in B['layers']}|rids|{l['id'] for l in P['layers']}
for k in list(P.get('style_overrides',{}))+P.get('hide_base_layers',[]):
    if k not in ids: print(f"WARNING override/hide refers to {k}, not in {nb} / region packs")
P['project_version']+=1; P['base_version']=nb; P['regions']=regions; P['upgraded']=today()
save_json(f"{ROOT}/projects/{slug}/project.json",P)
print(f"{slug}: now p{P['project_version']} on {nb}"+"".join(f" + {r['id']} {r['version']}" for r in regions))
if moved: print("moved to region pack:",moved,"| removed helper layers:",dropped)
if not a.no_build: subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'build_project.py'),slug],check=True)
