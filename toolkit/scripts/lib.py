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
def load_style(version):
    p=f"{ROOT}/style/versions/style_{version}.json"
    if not os.path.exists(p): raise SystemExit(f"style version {version} not released (missing {p}); run release_style.py")
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
            s.update({k:v for k,v in S['planned'].items() if not k.startswith('_')}); s['lineDecorationColor']=c
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
    ov={}
    for p in P: ov=deep_merge(ov,p.get('style_overrides',{}))
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
    order=list(S['layer_order'])
    for p in P:
        for g in p['groups']:
            gg=dict(id=g['id'],name=g['name'],collapsed=g.get('collapsed',False),visible=True,opacity=1)
            if g.get('parent'): gg['parentId']=g['parent']
            groups.append(gg); order.append(g['id'])
        for pl in p['layers']:
            spec=deep_merge(pl['style'],ov.get(pl['id'],{}))
            gj=load_geojson(f"{ROOT}/projects/{p['slug']}/{pl['file']}")
            desc={k:v for k,v in dict(title=pl.get('desc_title',pl['title']),attribution=pl.get('attribution'),lineage=f"גרסה {pl['version']}; "+pl.get('lineage','')).items() if v}
            lay=_layer(pl['id'],pl['title'],pl['group'],geolibre_style(spec,S),popup(pl['popup']),spec.get('visible',True),gj,f"data/{pl['group']}/{pl['id']}.geojson",desc,spec.get('filter'))
            lay['_web']=pl.get('web',{}); layers.append(lay)
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
        legend=dict(title=S['legend']['title'],groupByLayer=S['legend']['groupByLayer'],order=[l['id'] for l in layers],overrides={}),
        interaction=S['interaction'],metadata=meta)
    return proj
# ---------- outputs ----------
def strip_internal(proj):
    p=copy.copy(proj); p['layers']=[{k:v for k,v in l.items() if k!='_web'} for l in proj['layers']]; return p
def web_slim(proj,nd=5,tol=0.00005):
    """Slim copy for GitHub / web.geolibre.app: 5-decimal coords, ~5 m simplification, only used props, optional dissolve."""
    from shapely.geometry import shape,mapping
    from shapely.geometry import MultiLineString,MultiPolygon,MultiPoint
    out=copy.deepcopy(proj); new=[]
    for l in out['layers']:
        w=l.pop('_web',{}) or {}
        s=l['style']; keep=[f['field'] for f in l['popup']['fields']]
        if w.get('fields'): keep=[k for k in keep if k in w['fields']]; l['popup']['fields']=[f for f in l['popup']['fields'] if f['field'] in keep]
        need=set(keep)|{l['popup']['titleField']}
        if s.get('vectorStyleProperty'): need.add(s['vectorStyleProperty'])
        if s.get('labels',{}).get('enabled'): need.add(s['labels']['field'])
        if l.get('filterExpression'): need|=set(re.findall(r'"get",\s*"([^"]+)"',json.dumps(l['filterExpression'],ensure_ascii=False)))
        feats=[]
        for f in l['geojson']['features']:
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
        assert '_web' not in l
    for g in proj['layerGroups']:
        if g.get('parentId'): assert g['parentId'] in gids
    assert set(proj['legend']['order'])==set(ids)
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
