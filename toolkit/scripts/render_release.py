"""Before/after PNGs for a style release, rendered in the live GeoLibre Web app (not a re-implementation).
Usage: python scripts/render_release.py s2.0 --before dist/showcase_v3_hh-p1.web.geolibre.json --after dist/showcase_v4_hh-p2.web.geolibre.json
Writes style/releases/<style>/<view>_before.png, <view>_after.png and <view>_compare.png (side by side) for the fixed views below.
Needs: google-chrome + playwright-core (npm i playwright-core in $PLAYWRIGHT_DIR, default /workspace/geolibre-render), Pillow."""
import os,sys,json,argparse,subprocess,tempfile,copy; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
VIEWS={  # same three views as Carto's review (+ the Har Hotzvim project view)
 "national":dict(center=[34.95,31.75],zoom=7.6),
 "tel-aviv":dict(center=[34.80,32.07],zoom=12.3),
 "gush-dan":dict(center=[34.82,32.06],zoom=11.2),   # metropolitan band (10–13), s3.0 check: existing vs planned
 "jerusalem":dict(center=[35.20,31.79],zoom=13.6),
 "har-hotzvim":dict(center=[35.214,31.806],zoom=14.8),
}
ap=argparse.ArgumentParser(); ap.add_argument('style'); ap.add_argument('--before',required=True); ap.add_argument('--after',required=True)
ap.add_argument('--views',default=",".join(VIEWS)); ap.add_argument('--wait',type=int,default=16000); ap.add_argument('--compose-only',action='store_true')
a=ap.parse_args(); out=f"{ROOT}/style/releases/{a.style}"; os.makedirs(out,exist_ok=True); tmp=tempfile.mkdtemp()
def compose_pngs():
    try: from PIL import Image,ImageDraw
    except ImportError:   # the GIS venv has no Pillow – use the system python for this step
        subprocess.run(["/usr/bin/python3",__file__,*sys.argv[1:],"--compose-only"],check=True); return
    for v in a.views.split(','):
        A=Image.open(f"{out}/{v}_before.png"); B=Image.open(f"{out}/{v}_after.png")
        W=Image.new('RGB',(A.width+B.width+12,max(A.height,B.height)+40),'white'); W.paste(A,(0,40)); W.paste(B,(A.width+12,40))
        d=ImageDraw.Draw(W); d.text((10,12),f"BEFORE  {os.path.basename(a.before)}",fill='black'); d.text((A.width+22,12),f"AFTER  {os.path.basename(a.after)}  (style {a.style})",fill='black')
        W.save(f"{out}/{v}_compare.png"); print("wrote",f"{out}/{v}_compare.png")
if a.compose_only: compose_pngs(); sys.exit()
jobs=[]
for tag,src in (("before",a.before),("after",a.after)):
    P=load_json(src if os.path.isabs(src) else f"{ROOT}/{src}")
    for v in a.views.split(','):
        q=copy.deepcopy(P); q['mapView']=dict(VIEWS[v],bearing=0,pitch=0)
        q['legend']=dict(q['legend'],panelVisible=True,panelPosition="bottom-right")
        q['interaction']=dict(q.get('interaction',{}),controls=dict(q.get('interaction',{}).get('controls',{}),bookmark=False))
        f=f"{tmp}/{v}_{tag}.json"; save_json(f,q,compact=True)
        jobs.append(dict(file=f,out=f"{out}/{v}_{tag}.png",wait=a.wait,w=1500,h=1000))
jf=f"{tmp}/jobs.json"; save_json(jf,jobs)
subprocess.run(["node",os.path.join(os.path.dirname(__file__),"shot.mjs"),jf],check=True)
compose_pngs()
