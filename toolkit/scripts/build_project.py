"""Build a project on its pinned base: dist/<slug>_p<N>__base_<v>.geolibre (+ web copy).
Usage: python scripts/build_project.py har-hotzvim
       python scripts/build_project.py --showcase   # base + all projects in publish/web_root.json (the one-click GitHub file)"""
import os,sys; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
if sys.argv[1]=='--showcase':
    W=load_json(f"{ROOT}/publish/web_root.json"); bv=W['base_version']
    proj=compose(bv,W['projects'],view=base_manifest(bv)['map_view'],name=W['name'])
    tag=W['tag']; write_outputs(proj,f"showcase_{tag}")
else:
    slug=sys.argv[1]; P=project_cfg(slug)
    write_outputs(compose(P['base_version'],[slug]),f"{slug}_p{P['project_version']}__base_{P['base_version']}")
