"""Register a NEW version of a layer (never overwrites). Used by the monthly Hatzav check.
Usage:
  python scripts/add_layer_version.py nataz_kayam --fetch            # check data.gov.il; download+convert only if the source changed
  python scripts/add_layer_version.py nataz_kayam --file new.geojson  # or a shapefile .zip (any CRS -> WGS84)
Options: --date YYYY-MM-DD (data date, default today) --dry-run
Result: data/layers/<id>/<id>_<YYYY-MM>.geojson + new entry in layers/layers.json (current=new). Bases are NOT changed –
run make_base.py to include it in a new base version."""
import os,sys,json,argparse,subprocess,urllib.request,tempfile,hashlib; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
ap=argparse.ArgumentParser(); ap.add_argument('id'); ap.add_argument('--file'); ap.add_argument('--fetch',action='store_true'); ap.add_argument('--date',default=today()); ap.add_argument('--dry-run',action='store_true')
a=ap.parse_args(); reg=registry(); L=reg['layers'][a.id]; cur=[v for v in L['versions'] if v['version']==L['current']][0]
src_mod=None; path=a.file
if a.fetch:
    api=L['source'].get('ckan_api') or ("https://data.gov.il/api/3/action/package_show?id="+L['source']['dataset'].rstrip('/').split('/')[-1])
    d=json.load(urllib.request.urlopen(api,timeout=60))['result']
    zr=[r for r in d['resources'] if r['url'].endswith('.zip') and 'km' not in r['url'].split('/')[-1]]
    if not zr: sys.exit("no zip resource found")
    r=zr[0]; src_mod=(r.get('last_modified') or r.get('created') or '')[:10]
    print(f"{a.id}: source last_modified {src_mod} (registered {cur.get('source_modified')})")
    if src_mod and src_mod==cur.get('source_modified'): print("unchanged – nothing to do"); sys.exit(0)
    if a.dry_run: print("CHANGED (dry run)"); sys.exit(0)
    path=tempfile.mktemp(suffix='.zip'); subprocess.run(['curl','-s','-L','-m','900','-A','Mozilla/5.0','-o',path,r['url']],check=True)
if not path: sys.exit("give --file or --fetch")
if path.endswith('.zip') or path.endswith('.shp'):
    import geopandas as gpd
    g=gpd.read_file(('zip://' if path.endswith('.zip') else '')+path); g=g.to_crs(4326) if g.crs else g
    tmp=tempfile.mktemp(suffix='.geojson'); g.to_file(tmp,driver='GeoJSON'); path=tmp
new=load_json(path)
def keys(d): return {hashlib.md5(json.dumps([f.get('properties'),f.get('geometry')],sort_keys=True,ensure_ascii=False).encode()).hexdigest() for f in d['features']}
old=load_json(f"{ROOT}/{cur['file']}"); ko,kn=keys(old),keys(new)
if ko==kn: print("content identical to current version – nothing registered"); sys.exit(0)
ver=a.date[:7]; existing={v['version'] for v in L['versions']}; n=2
while ver in existing: ver=f"{a.date[:7]}-{n}"; n+=1
dst=f"data/layers/{a.id}/{a.id}_{ver}.geojson"
if os.path.exists(f"{ROOT}/{dst}"): sys.exit(f"{dst} exists")
changes=f"{len(old['features'])}→{len(new['features'])} ישויות; {len(kn-ko)} חדשות/שונו, {len(ko-kn)} הוסרו/שונו"
print(f"new version {ver}: {changes}")
if a.dry_run: sys.exit(0)
save_json(f"{ROOT}/{dst}",new,compact=True); fi=file_info(f"{ROOT}/{dst}")
L['versions'].append(dict(version=ver,data_date=a.date,source_modified=src_mod,file=dst,**fi,
   storage="github+drive" if fi['bytes']<=reg['github_size_limit_bytes'] else "drive",drive_file_id=None,changes=changes,previous=L['current']))
L['current']=ver; reg['updated']=today(); save_json(f"{ROOT}/layers/layers.json",reg)
print(f"registered {dst}; next: publish.py plan-layers (upload to Drive), then make_base.py v<N>")
