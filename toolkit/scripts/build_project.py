"""Build a project on its pinned base (+ pinned region packs): dist/<slug>_p<N>__base_<v>[+<region><ver>].geolibre (+ web copy).
Usage: python scripts/build_project.py har-hotzvim [--no-clip]
       python scripts/build_project.py --region jerusalem[=j1] [--base v5]   # region pack preview on a base: dist/region_jerusalem_j1__base_v5
       python scripts/build_project.py --showcase   # publish/web_root.json: base (+ regions + projects) = the one-click GitHub file"""
import os,sys,glob; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
def latest_base(): return sorted(glob.glob(f"{ROOT}/base/v*/manifest.json"),key=lambda p:int(p.split('/')[-2][1:]))[-1].split('/')[-2]
def rtag(R): return "".join(f"+{r['id']}_{r['version']}" for r in R)
if sys.argv[1]=='--showcase':
    W=load_json(f"{ROOT}/publish/web_root.json"); bv=W['base_version']
    proj=compose(bv,W.get('projects',[]),view=base_manifest(bv)['map_view'],name=W['name'],regions=W.get('regions',[]))
    write_outputs(proj,f"showcase_{W['tag']}")
elif sys.argv[1]=='--region':
    r=sys.argv[2]; bv=sys.argv[sys.argv.index('--base')+1] if '--base' in sys.argv else latest_base()
    rid,_,ver=r.partition('='); ver=ver or load_json(f"{ROOT}/regions/{rid}/region.json")['current']; M=region_manifest(rid,ver)
    bb=M.get('bbox'); clip=[bb[0]-.05,bb[1]-.05,bb[2]+.05,bb[3]+.05] if bb and '--no-clip' not in sys.argv else None
    write_outputs(compose(bv,[],regions=[f"{rid}={ver}"]),f"region_{rid}_{ver}__base_{bv}",web_clip=clip)
else:
    slug=sys.argv[1]; P=project_cfg(slug); R=P.get('regions',[])
    # web copy: city-scale base layers clipped to the project area (project bbox ∪ region bboxes, +0.05°) – keeps the link fast and < 3.3 MB
    bb=[b for b in [P.get('bbox')]+[region_manifest(r['id'],r['version']).get('bbox') for r in R] if b]
    clip=[round(min(b[0] for b in bb)-.05,3),round(min(b[1] for b in bb)-.05,3),round(max(b[2] for b in bb)+.05,3),round(max(b[3] for b in bb)+.05,3)] if bb and '--no-clip' not in sys.argv else None
    write_outputs(compose(P['base_version'],[slug]),f"{slug}_p{P['project_version']}__base_{P['base_version']}"+rtag(R),web_clip=clip)
