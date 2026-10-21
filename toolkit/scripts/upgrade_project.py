"""Move a project to a newer base version. Keeps project layers + overrides, bumps project_version,
archives the previous project.json in projects/<slug>/history/, builds the new versioned file. Old builds stay.
Usage: python scripts/upgrade_project.py har-hotzvim v4 [--no-build]"""
import os,sys,subprocess; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
slug,nb=sys.argv[1],sys.argv[2]; P=project_cfg(slug); base_manifest(nb)
if P['base_version']==nb: sys.exit(f"{slug} already on {nb}")
reg=registry(); B=base_manifest(nb); ids={l['id'] for l in B['layers']}
for k in list(P.get('style_overrides',{}))+P.get('hide_base_layers',[]):
    if k not in ids and k not in {l['id'] for l in P['layers']}: print(f"WARNING override/hide refers to {k}, not in {nb}")
save_json(f"{ROOT}/projects/{slug}/history/project_p{P['project_version']}__base_{P['base_version']}.json",P)
P['history'].append(dict(project_version=P['project_version'],base_version=P['base_version'],archived=today()))
P['project_version']+=1; P['base_version']=nb; P['upgraded']=today()
save_json(f"{ROOT}/projects/{slug}/project.json",P); print(f"{slug}: now p{P['project_version']} on {nb}")
if '--no-build' not in sys.argv: subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'build_project.py'),slug],check=True)
