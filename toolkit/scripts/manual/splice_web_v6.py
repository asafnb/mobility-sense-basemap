"""Web copy of base v6 without the heavy Drive-only layers on this machine.
The light-rail layers (lrt_line + its derived layers, lrt_stat) are produced by the toolkit's own
compose() + web_slim() from the 2026-11 layer versions; every other layer is taken unchanged from the
published v5 web copy (their pinned versions are identical in v5 and v6).
Usage: python splice_v6.py <toolkit dir> <v5 web file> <out web file>"""
import sys, os, json, copy
TK, V5, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, f'{TK}/scripts')
import lib

reg = lib.registry(); B = lib.base_manifest('v6'); P5 = lib.base_manifest('v5')
changed = {l['id'] for l in B['layers']} - {l['id'] for l in P5['layers'] if l in B['layers']}
assert changed == {'lrt_line', 'lrt_stat'}, changed
assert B['style_version'] == P5['style_version']

# stand-ins for layers whose files are only in Drive: one throw-away feature each (never written out)
stub = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {},
        "geometry": {"type": "LineString", "coordinates": [[35.0, 31.0], [35.001, 31.001]]}}]}
made = []
for l in B['layers']:
    L, v = lib.layer_version(reg, l['id'], l['version'])
    p = f"{TK}/{v['file']}"
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(stub, open(p, 'w')); made.append(p)
try:
    proj = lib.compose('v6')
    web = lib.web_slim(proj)
finally:
    for p in made:
        os.remove(p)

S = lib.load_style(B['style_version'])
lrt_ids = {i for i, s in S['layers'].items() if i in ('lrt_line', 'lrt_stat') or s.get('source') in ('lrt_line', 'lrt_stat')}
new = {l['id']: l for l in web['layers'] if l['id'] in lrt_ids}
old = lib.load_json(V5)
out = copy.deepcopy(old)
seen = set()
for i, l in enumerate(out['layers']):
    if l['id'] in new:
        out['layers'][i] = new[l['id']]; seen.add(l['id'])
missing = set(new) - seen
assert not missing, f"layers not in the v5 web copy: {missing}"
for i in new:
    if i in web.get('styles', {}):
        out['styles'][i] = web['styles'][i]
out['metadata'] = web['metadata']
out['name'] = web['name']
print(lib.validate(out, 'web v6 (spliced)'))
for i in sorted(new):
    o = next(l for l in old['layers'] if l['id'] == i)
    print(f"{i}: {len(o['geojson']['features'])} -> {len(new[i]['geojson']['features'])} features")
lib.save_json(OUT, out, compact=True)
print('bytes', os.path.getsize(OUT), 'v5 bytes', os.path.getsize(V5))
print('metadata', json.dumps(out['metadata'], ensure_ascii=False)[:600])
