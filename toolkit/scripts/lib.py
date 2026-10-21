"""Mobility Sense GeoLibre toolkit – shared logic.
Concepts: style version (style/versions/style_<v>.json) + layer versions (layers/layers.json)
= base version (base/<base>/manifest.json). Projects pin a base version and add their own layers."""
import json,os,copy,hashlib,time,datetime,re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST=f"{ROOT}/dist"
def load_json(p): return json.load(open(p,encoding='utf-8'))
def save_json(p,d,compact=False):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,'w',encoding='utf-8') as f:
        if compact: json.dump(d,f,ensure_ascii=False,separators=(',',':'))
        else: json.dump(d,f,ensure_ascii=False,indent=1); f.write('\n')
def file_info(p):
    b=open(p,'rb').read(); n=None
    try: n=len(json.loads(b)['features'])
    except Exception: pass
    return dict(bytes=len(b),features=n,sha256=hashlib.sha256(b).hexdigest()[:16])
def today(): return datetime.date.today().isoformat()
# ---------- style ----------
def style_key(v):
    """'s1' == 's1.0' < 's1.1' < 's2.0'. Major = layer ids/splits/schema; minor = colour/width/label tweaks."""
    m=re.fullmatch(r's(\d+)(?:\.(\d+))?',v)
    if not m: raise SystemExit(f"bad style version {v!r} (expected s<major>.<minor>)")
    return (int(m.group(1)),int(m.group(2) or 0))
def style_file(version):
    for c in (version,f"s{style_key(version)[0]}" if style_key(version)[1]==0 else None,"s%d.%d"%style_key(version)):
        if c and os.path.exists(f"{ROOT}/style/versions/style_{c}.json"): return f"{ROOT}/style/versions/style_{c}.json"
    return None
def released_styles():
    import glob
    vs=[os.path.basename(p)[6:-5] for p in glob.glob(f"{ROOT}/style/versions/style_s*.json")]
    return sorted(vs,key=style_key)
def load_style(version):
    p=style_file(version)
    if not p: raise SystemExit(f"style version {version} not released; run release_style.py")
    return load_json(p)
def _res(v,S):
    if isinstance(v,str) and v.startswith('@'):
        k=v[1:]
        if k in S['palette']: return S['palette'][k]
        if k in S['categories']: return {kk:_res(vv,S) for kk,vv in S['categories'][k].items()}
        raise KeyError(f"unknown style reference {v}")
    if isinstance(v,dict): return {k:_res(x,S) for k,x in v.items()}
    return v
def deep_merge(a,b):
    out=copy.deepcopy(a)
    for k,v in (b or {}).items():
        out[k]=deep_merge(out[k],v) if isinstance(v,dict) and isinstance(out.get(k),dict) else copy.deepcopy(v)
    return out
def geolibre_style(spec,S):
    """Turn a compact style spec (style.json 'layers' entry) into a GeoLibre layer style dict."""
    sp=_res(spec,S); c=sp['color']
    if sp['kind']=='point':
        s=dict(fillColor=c,**S['point_defaults'],circleRadius=sp.get('radius',4))
    else:
        s=dict(strokeColor=c,strokeWidth=sp.get('width',2),fillColor=c,**S['line_defaults'])
        if sp.get('planned'):
            s.update({k:v for k,v in S['planned'].items() if not k.startswith('_')}); s.setdefault('lineDecorationColor',c)
    if sp.get('categorized'):
        m=sp['categorized']['map']
        s.update(vectorStyleMode="categorized",vectorStyleProperty=sp['categorized']['prop'],vectorStyleStops=[{"value":k,"color":v,"label":k} for k,v in m.items()])
    if sp.get('label'):
        l=dict(sp['label']); pl=l.get('placement','point')
        lab=dict(S['label_defaults'],enabled=True,placement=pl,dedupe="unique" if pl=="line" else "off"); lab.update(l)
        s['labels']=lab
    s.update(sp.get('extra',{}))
    return s
def popup(p):
    return dict(click=True,hover=True,titleField=p['title_field'],fields=[dict(field=f,label=l,**({"hover":True} if i==0 else {})) for i,(f,l) in enumerate(p['fields'])])
# ---------- data ----------
def _rnd(c,n):
    if isinstance(c[0],(int,float)): return [round(c[0],n),round(c[1],n)]
    return [_rnd(x,n) for x in c]
def load_geojson(path,nd=6):
    d=load_json(path)
    for f in d['features']:
        if f.get('geometry'): f['geometry']['coordinates']=_rnd(f['geometry']['coordinates'],nd)
    return d
def registry(): return load_json(f"{ROOT}/layers/layers.json")
def layer_version(reg,lid,ver):
    L=reg['layers'][lid]
    for v in L['versions']:
        if v['version']==ver: return L,v
    raise SystemExit(f"layer {lid} has no version {ver}")
def base_manifest(bv): return load_json(f"{ROOT}/base/{bv}/manifest.json")
def project_cfg(slug): return load_json(f"{ROOT}/projects/{slug}/project.json")
# ---------- override policy (style.json override_policy) ----------
BASE_OVERRIDE_KEYS={'visible','width','label','extra'}; BASE_OVERRIDE_EXTRA={'minZoom','maxZoom'}
def check_overrides(slug,ov,S,project_ids):
    """Projects may change visibility, minZoom/maxZoom, labels and width of base layers – never palette or status encoding.
    Unknown layer ids and unknown keys are rejected (a typo used to be added silently)."""
    errs=[]; lab_keys=set(S['label_defaults'])
    for lid,o in ov.items():
        if lid in project_ids:
            col=o.get('color')
            if isinstance(col,str) and not col.startswith('@'): print(f"WARNING {slug}: {lid}.color {col} – use a palette token (@PROJ_...)")
            continue
        if lid not in S['layers']: errs.append(f"{lid}: not a base or project layer"); continue
        for k,v in o.items():
            if k not in BASE_OVERRIDE_KEYS: errs.append(f"{lid}.{k}: not allowed on a base layer (allowed: {sorted(BASE_OVERRIDE_KEYS)})")
            elif k=='extra':
                bad=set(v)-BASE_OVERRIDE_EXTRA
                if bad: errs.append(f"{lid}.extra.{sorted(bad)}: only minZoom/maxZoom may be overridden")
            elif k=='label':
                bad=set(v)-lab_keys
                if bad: errs.append(f"{lid}.label.{sorted(bad)}: unknown label keys")
    if errs: raise SystemExit(f"style_overrides of project {slug} rejected:\n  "+"\n  ".join(errs))
def merge_overrides(P,S):
    ov={}; owner={}
    for p in P:
        po=p.get('style_overrides',{}); check_overrides(p['slug'],po,S,{l['id'] for l in p['layers']})
        for lid,o in po.items():
            if lid in owner and owner[lid]!=p['slug']:
                print(f"WARNING override conflict on {lid}: {owner[lid]} vs {p['slug']} – {p['slug']} wins (last on command line)")
            owner[lid]=p['slug']
        ov=deep_merge(ov,po)
    return ov
# ---------- compose ----------
def _layer(lid,name,gid,style,pop,visible,geojson,rel,desc,filt=None):
    lay=dict(id=lid,name=name,type="geojson",source={"type":"geojson"},visible=visible,opacity=1,style=style,metadata={"localFile":rel},geojson=geojson,groupId=gid,popup=pop,descriptiveMetadata=desc)
    if filt: lay['filterExpression']=filt
    return lay
def compose(bv,projects=(),view=None,name=None):
    """Build a GeoLibre project dict: base version bv + project slugs (in order)."""
    B=base_manifest(bv); S=load_style(B['style_version']); reg=registry()
    P=[project_cfg(s) for s in projects]
    for p in P:
        if p['base_version']!=bv: raise SystemExit(f"project {p['slug']} is pinned to {p['base_version']}, not {bv}; run upgrade_project.py")
    ov=merge_overrides(P,S)
    hidden=set(sum([p.get('hide_base_layers',[]) for p in P],[]))
    groups=[]
    for g in S['groups']:
        used={reg['layers'][l['id']]['group'] for l in B['layers']}
        if g['id']=='g_roads' and 'g_roads' not in used: continue
        if g['id']=='g_proj' and not P: continue
        gg=dict(id=g['id'],name=g['name'],collapsed=g.get('collapsed',False),visible=True,opacity=1)
        if g.get('parent'): gg['parentId']=g['parent']
        groups.append(gg)
    layers=[]
    for ent in B['layers']:
        lid=ent['id']; L,v=layer_version(reg,lid,ent['version'])
        spec=deep_merge(S['layers'][lid],ov.get(lid,{}))
        gj=load_geojson(f"{ROOT}/{v['file']}")
        rel=f"data/{L['group']}/{lid}.geojson"
        lineage=f"גרסה {v['version']}; הורד {v['data_date']}; עודכן במקור {v.get('source_modified') or '?'}; {v['features']} ישויות; {L.get('crs','')}"+(f"; {L['note']}" if L.get('note') else "")
        desc=dict(title=L['title'],attribution=L['attribution'],lineage=lineage)
        if L['source'].get('dataset'): desc['links']=[{"href":L['source']['dataset'],"rel":"via","title":"data.gov.il"}]
        desc={k:desc[k] for k in ['title','attribution','links','lineage'] if k in desc}
        lay=_layer(lid,L['title'],L['group'],geolibre_style(spec,S),popup(L['popup']),spec.get('visible',True) and lid not in hidden,gj,rel,desc,spec.get('filter'))
        lay['_web']=L.get('web',{}); layers.append(lay)
    # derived layers: style entries with "source": <registry id> reuse that layer's data + pinned version (review §5.1)
    pinned={e['id']:e['version'] for e in B['layers']}
    for did,dspec in S['layers'].items():
        src=dspec.get('source')
        if not src or src not in pinned: continue
        L,v=layer_version(reg,src,pinned[src]); spec=deep_merge(dspec,ov.get(did,{}))
        desc=dict(title=spec.get('title',L['title']),attribution=L['attribution'],lineage=f"נגזרת מ־{src} (גרסה {v['version']}); "+(f"מסנן: {json.dumps(spec.get('filter'),ensure_ascii=False)}" if spec.get('filter') else ""))
        lay=_layer(did,spec.get('title',L['title']),L['group'],geolibre_style(spec,S),popup(L['popup']),spec.get('visible',True) and src not in hidden and did not in hidden,
                   load_geojson(f"{ROOT}/{v['file']}"),f"data/{L['group']}/{src}.geojson",desc,spec.get('filter'))
        lay['_web']=L.get('web',{}); lay['_legend']=spec.get('legend',True); layers.append(lay)
    for l in layers:
        if l['id'] in S['layers'] and S['layers'][l['id']].get('legend') is False: l['_legend']=False
    order=[g['id'] for g in S['groups']] if 'layer_order' not in S else list(S['layer_order'])
    for p in P:
        for g in p['groups']:
            gg=dict(id=g['id'],name=g['name'],collapsed=g.get('collapsed',False),visible=True,opacity=1)
            if g.get('parent'): gg['parentId']=g['parent']
            groups.append(gg); order.append(g['id'])
        byid={l['id']:l for l in p['layers']}
        for pl in p['layers']:
            if pl.get('derived_from'):   # derived project layer: same file/version/popup as its source entry, own style/filter
                pl=dict({k:v for k,v in byid[pl['derived_from']].items() if k not in ('id','title','style','legend')},**pl)
            spec=deep_merge(pl['style'],ov.get(pl['id'],{}))
            gj=load_geojson(f"{ROOT}/projects/{p['slug']}/{pl['file']}")
            desc={k:v for k,v in dict(title=pl.get('desc_title',pl['title']),attribution=pl.get('attribution'),lineage=f"גרסה {pl['version']}; "+pl.get('lineage','')).items() if v}
            lay=_layer(pl['id'],pl['title'],pl['group'],geolibre_style(spec,S),popup(pl['popup']),spec.get('visible',True),gj,f"data/{pl['group']}/{pl['id']}.geojson",desc,spec.get('filter'))
            lay['_web']=pl.get('web',{}); lay['_legend']=pl.get('legend',True); lay['_proj']=True; layers.append(lay)
    stack=S.get('layer_stack_bottom_to_top')
    if stack:   # review §5.2: explicit bottom→top stack for base layers; project layers above, in project order
        def key(l):
            if l.get('_proj'): return (2,order.index(l['groupId']) if l['groupId'] in order else len(order),0)
            if l['id'] in stack: return (0,stack.index(l['id']),0)
            return (1,order.index(l['groupId']) if l['groupId'] in order else len(order),0)
        layers.sort(key=key)
    else:
        layers.sort(key=lambda l:order.index(l['groupId']) if l['groupId'] in order else len(order))
    now=int(time.time()*1000)
    bms=[dict(b,pitch=0,bearing=0,createdAt=now,groupId="regions") for b in B['bookmarks']]
    bgroups=[{"id":"regions","name":"אזורי פרויקטים","collapsed":False}]
    for p in P:
        for b in p.get('bookmarks',[]): bms.append(dict(b,pitch=0,bearing=0,createdAt=now,groupId="projects"))
    if P: bgroups.append({"id":"projects","name":"פרויקטים","collapsed":False})
    mv=view or (P[-1]['map_view'] if P and P[-1].get('map_view') else B['map_view'])
    title=name or (P[-1]['title'] if P else B['name'])
    meta=dict(description=B['description']+("" if not P else " פרויקטים: "+", ".join(p['title'] for p in P)),created=B['created'],built=today(),
        base_version=bv,style_version=B['style_version'],layer_versions={l['id']:l['version'] for l in B['layers']},
        projects=[dict(slug=p['slug'],project_version=p['project_version'],base_version=p['base_version']) for p in P],
        toolkit="https://github.com/asafnb/mobility-sense-basemap/tree/main/toolkit",
        note=S['planned']['_note'])
    proj=dict(version="0.2.0",name=title,mapView=dict(center=mv['center'],zoom=mv['zoom'],bearing=0,pitch=0),
        basemapStyleUrl=S['basemap']['url'],basemapVisible=S['basemap']['visible'],basemapOpacity=S['basemap']['opacity'],blankBackgroundColor=None,
        layers=layers,selectedLayerId=None,layerGroups=groups,styles={},bookmarkGroups=bgroups,bookmarks=bms,
        legend=build_legend(S,P,layers,bv,B['style_version']),
        interaction=S['interaction'],metadata=meta)
    return proj
def build_legend(S,P,layers,bv,sv):
    """Review §3/§5.3: pass legend.order (top-first) / customEntries / overrides through. Project legend entries go on top
    (after the 'how to read' section); helper layers (legend:false) are hidden. Title carries style+base version for traceability."""
    SL=S['legend']; ids=[l['id'] for l in layers]
    ce=copy.deepcopy(SL.get('customEntries',{})); ovr=copy.deepcopy(SL.get('overrides',{}))
    proj_order=[]
    for p in P:
        pl=p.get('legend',{}); ce.update(copy.deepcopy(pl.get('customEntries',{}))); ovr.update(copy.deepcopy(pl.get('overrides',{})))
        proj_order+=pl.get('order',[l['id'] for l in p['layers']])
    for l in layers:
        if l.get('_legend') is False: ovr[l['id']]={"hidden":True}
    if 'order' in SL:
        base=[i for i in SL['order'] if i in ids or i.startswith('custom:')]
        head=[i for i in base if i.startswith('custom:')]; base=[i for i in base if not i.startswith('custom:')]
        order=head+[i for i in proj_order if i in ids]+base
        order+=[i for i in reversed(ids) if i not in order]          # anything not listed: top-first by draw order
    else: order=list(reversed(ids))                                   # s1: legend.order is top-first = reverse draw order
    ce={k:v for k,v in ce.items() if k in ids or k.startswith('custom:')}; ovr={k:v for k,v in ovr.items() if k in ids}
    d=dict(title=f"{SL['title']} · {sv} / {bv}",groupByLayer=SL['groupByLayer'],order=order,overrides=ovr)
    if ce: d['customEntries']=ce
    return d
# ---------- outputs ----------
def strip_internal(proj):
    p=copy.copy(proj); p['layers']=[{k:v for k,v in l.items() if not k.startswith('_')} for l in proj['layers']]; return p
class _NoEval(Exception): pass
def eval_filter(e,props):
    """Minimal MapLibre-expression evaluator for the filters used in style.json (all/any/!/==/!=/in+literal/get).
    Raises _NoEval for anything else (then the feature is kept)."""
    if not isinstance(e,list) or not e: return e
    op=e[0]
    if op=='get': return props.get(e[1])
    if op=='literal': return e[1]
    if op=='all': return all(eval_filter(x,props) for x in e[1:])
    if op=='any': return any(eval_filter(x,props) for x in e[1:])
    if op=='!': return not eval_filter(e[1],props)
    if op=='==': return eval_filter(e[1],props)==eval_filter(e[2],props)
    if op=='!=': return eval_filter(e[1],props)!=eval_filter(e[2],props)
    if op=='in':
        hay=eval_filter(e[2],props)
        if isinstance(hay,list): return eval_filter(e[1],props) in hay
    raise _NoEval(op)
def prefilter(feats,filt):
    if not filt: return feats
    try: return [f for f in feats if eval_filter(filt,f.get('properties') or {})]
    except _NoEval: return feats
def web_slim(proj,nd=5,tol=0.00005):
    """Slim copy for GitHub / web.geolibre.app: 5-decimal coords, ~5 m simplification, only used props, optional dissolve."""
    from shapely.geometry import shape,mapping
    from shapely.geometry import MultiLineString,MultiPolygon,MultiPoint
    out=copy.deepcopy(proj); new=[]
    for l in out['layers']:
        w=l.pop('_web',{}) or {}
        for k in [k for k in l if k.startswith('_')]: l.pop(k)
        s=l['style']; keep=[f['field'] for f in l['popup']['fields']]
        if w.get('fields'): keep=[k for k in keep if k in w['fields']]; l['popup']['fields']=[f for f in l['popup']['fields'] if f['field'] in keep]
        need=set(keep)|{l['popup']['titleField']}
        if s.get('vectorStyleProperty'): need.add(s['vectorStyleProperty'])
        if s.get('labels',{}).get('enabled'): need.add(s['labels']['field'])
        if l.get('filterExpression'): need|=set(re.findall(r'"get",\s*"([^"]+)"',json.dumps(l['filterExpression'],ensure_ascii=False)))
        for r in s.get('vectorRules') or []:
            f=r.get('filter'); f=json.loads(f) if isinstance(f,str) and f.strip().startswith('[') else f
            need|=set(re.findall(r'"get",\s*"([^"]+)"',json.dumps(f,ensure_ascii=False)))
        feats=[]
        for f in prefilter(l['geojson']['features'],l.get('filterExpression')):   # web copy: drop features the layer filter hides
            if not f.get('geometry'): continue
            g=shape(f['geometry'])
            if g.geom_type not in('Point','MultiPoint'): g=g.simplify(tol,preserve_topology=True)
            if g.is_empty: continue
            feats.append(({k:v for k,v in (f.get('properties') or {}).items() if k in need},g))
        if w.get('merge'):
            grp={}
            for pr,g in feats: grp.setdefault(json.dumps(pr,sort_keys=True,ensure_ascii=False),(pr,[]))[1].append(g)
            feats=[]
            for pr,gs in grp.values():
                parts=[]
                for g in gs: parts+=list(g.geoms) if hasattr(g,'geoms') else [g]
                t=parts[0].geom_type
                M={'LineString':MultiLineString,'Polygon':MultiPolygon,'Point':MultiPoint}[t]
                feats.append((pr,M(parts) if len(parts)>1 else parts[0]))
        l['geojson']={"type":"FeatureCollection","features":[{"type":"Feature","properties":pr,"geometry":dict(type=mapping(g)['type'],coordinates=_rnd(_tolist(mapping(g)['coordinates']),nd))} for pr,g in feats]}
        new.append(l)
    out['layers']=new; out['metadata']=dict(out['metadata'],web_copy=f"גרסה קלה לרשת: קואורדינטות 5 ספרות, פישוט ~5 מ׳, שדות מצומצמים. הגרסה המלאה בדרייב.")
    return out
def _tolist(c):
    if isinstance(c,(list,tuple)) and c and isinstance(c[0],(int,float)): return [c[0],c[1]]
    return [_tolist(x) for x in c]
def validate(proj,label=""):
    ids=[l['id'] for l in proj['layers']]; gids={g['id'] for g in proj['layerGroups']}
    assert len(ids)==len(set(ids)),"duplicate layer ids"
    for l in proj['layers']:
        assert l['groupId'] in gids, f"{l['id']}: unknown group {l['groupId']}"
        assert l['geojson']['type']=='FeatureCollection' and l['geojson']['features'], f"{l['id']}: empty geojson"
        for f in l['geojson']['features'][:50]:
            c=f['geometry']['coordinates']
            while isinstance(c[0],list): c=c[0]
            assert 33<c[0]<37 and 29<c[1]<34, f"{l['id']}: coords outside Israel {c}"
        assert not any(k.startswith('_') for k in l)
    for g in proj['layerGroups']:
        if g.get('parentId'): assert g['parentId'] in gids
    lo=proj['legend']['order']; assert len(lo)==len(set(lo)),"duplicate legend.order"
    assert set(ids)<=set(lo) and all(i in ids or i.startswith('custom:') for i in lo),"legend.order must cover all layers (+custom:*)"
    for k in proj['legend'].get('customEntries',{}): assert k in ids or k.startswith('custom:'),k
    json.loads(json.dumps(proj,ensure_ascii=False))
    return f"OK {label}: {len(ids)} layers, {len(proj['layerGroups'])} groups, {len(proj['bookmarks'])} bookmarks"
def write_outputs(proj,stem,outdir=DIST,web=True):
    os.makedirs(outdir,exist_ok=True)
    full=strip_internal(proj); print(validate(full,"full"))
    fp=f"{outdir}/{stem}.geolibre"
    if os.path.exists(fp): raise SystemExit(f"{fp} exists – versioned outputs are never overwritten. Bump the version.")
    save_json(fp,full,compact=True); res=dict(full=fp,full_bytes=os.path.getsize(fp))
    if web:
        wp=f"{outdir}/{stem}.web.geolibre.json"; w=web_slim(proj); print(validate(w,"web"))
        save_json(wp,w,compact=True); res.update(web=wp,web_bytes=os.path.getsize(wp))
        if res['web_bytes']>3_300_000: print(f"WARNING web copy {res['web_bytes']/1e6:.2f} MB > 3.3 MB connector limit")
    print(json.dumps(res,ensure_ascii=False)); return res
