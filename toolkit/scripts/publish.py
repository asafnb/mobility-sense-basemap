"""Publishing is done by the agent with the Drive and GitHub connectors (no credentials live on the box).
This script prints the exact upload plan and records the resulting ids, so the registry always knows where each file is.
  python scripts/publish.py plan base v3            # full .geolibre -> Drive (new file), web copy listed for GitHub
  python scripts/publish.py plan project har-hotzvim
  python scripts/publish.py plan showcase           # one-click GitHub file (same filename, link keeps working)
  python scripts/publish.py plan layers             # layer versions without a Drive id yet
  python scripts/publish.py plan region jerusalem j1  # region preview build -> Drive + region layers without a Drive id
  python scripts/publish.py record region jerusalem j1 <drive_file_id>
  python scripts/publish.py record base v3 <drive_file_id>
  python scripts/publish.py record project har-hotzvim <drive_file_id>
  python scripts/publish.py record layer nataz_kayam 2026-11 <drive_file_id>
  python scripts/publish.py record github <commit_sha> <note>
Rule: Drive uploads always create a NEW file with the versioned name; nothing is trashed or overwritten."""
import os,sys,json,glob; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
GEO="1FXJJjrB6ppsCjv1HFHneKLkIGdqTmEQp"; REPO="asafnb/mobility-sense-basemap"; LOG=f"{ROOT}/publish/publish_log.json"
def log(e):
    l=load_json(LOG) if os.path.exists(LOG) else []; l.append(dict(e,date=today())); save_json(LOG,l)
cmd=sys.argv[1:]; plan=[]
if cmd[0]=='plan':
    if cmd[1]=='base':
        bv=cmd[2]; s=f"mobility-sense-base_{bv}"
        plan.append(dict(action="drive_upload",source=f"{DIST}/{s}.geolibre",folder_id=GEO,name=f"{s}.geolibre"))
        plan.append(dict(action="github_put",source=f"{DIST}/{s}.web.geolibre.json",repo=REPO,path=f"bases/{s}.web.geolibre.json",optional=True))
    elif cmd[1]=='project':
        P=project_cfg(cmd[2]); s=f"{P['slug']}_p{P['project_version']}__base_{P['base_version']}"
        s+="".join(f"+{r['id']}_{r['version']}" for r in P.get('regions',[]))
        plan.append(dict(action="drive_upload",source=f"{DIST}/{s}.geolibre",folder_id=P['drive'].get('geolibre_folder_id',GEO),name=f"{s}.geolibre"))
        plan.append(dict(action="github_put",source=f"{DIST}/{s}.web.geolibre.json",repo=REPO,path=f"projects/{P['slug']}.web.geolibre.json",note="stable per-project link"))
    elif cmd[1]=='region':
        rid,ver=cmd[2],cmd[3]; M=region_manifest(rid,ver); D=load_json(f"{ROOT}/regions/{rid}/region.json"); reg=registry()
        import glob as _g
        for f in sorted(_g.glob(f"{DIST}/region_{rid}_{ver}__base_*.geolibre")):
            plan.append(dict(action="drive_upload",source=f,folder_id=D['drive'].get('folder_id') or GEO,name=os.path.basename(f)))
        for e in M['layers']:
            L,v=layer_version(reg,e['id'],e['version'])
            if not v.get('drive_file_id'): plan.append(dict(action="drive_upload",source=f"{ROOT}/{v['file']}",folder_id=D['drive'].get('layer_folder_id') or L.get('drive_folder_id'),name=os.path.basename(v['file']),layer=e['id'],version=v['version']))
    elif cmd[1]=='showcase':
        W=load_json(f"{ROOT}/publish/web_root.json")
        plan.append(dict(action="github_put",source=f"{DIST}/showcase_{W['tag']}.web.geolibre.json",repo=REPO,path=W['github_path'],note="keep filename – one-click link"))
    elif cmd[1]=='layers':
        reg=registry()
        for lid,L in reg['layers'].items():
            for v in L['versions']:
                if not v.get('drive_file_id'): plan.append(dict(action="drive_upload",source=f"{ROOT}/{v['file']}",folder_id=L.get('drive_folder_id'),name=os.path.basename(v['file']),layer=lid,version=v['version'],status=L['status']))
    print(json.dumps(plan,ensure_ascii=False,indent=1))
elif cmd[0]=='record':
    if cmd[1]=='base':
        p=f"{ROOT}/base/{cmd[2]}/manifest.json"; M=load_json(p); M['outputs']['full_drive_file_id']=cmd[3]; save_json(p,M)
    elif cmd[1]=='project':
        p=f"{ROOT}/projects/{cmd[2]}/project.json"; P=load_json(p)
        P['builds'].append(dict(project_version=P['project_version'],base_version=P['base_version'],drive_file_id=cmd[3],date=today())); save_json(p,P)
    elif cmd[1]=='region':
        p=f"{ROOT}/regions/{cmd[2]}/{cmd[3]}/manifest.json"; M=load_json(p); M['outputs']['preview_drive_file_id']=cmd[4]; save_json(p,M)
    elif cmd[1]=='layer':
        reg=registry(); L,v=layer_version(reg,cmd[2],cmd[3]); v['drive_file_id']=cmd[4]; save_json(f"{ROOT}/layers/layers.json",reg)
    log(dict(kind=cmd[1],args=cmd[2:])); print("recorded")
