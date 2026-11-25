"""Jerusalem light rail status update (25.11.2026) for the mobility-sense-basemap toolkit.
Reads lrt_line / lrt_stat 2026-10 and writes edited GeoJSON files to pass to add_layer_version.py --file.
Only Jerusalem features change. Geometry of split lines is cut at station positions; nothing is redrawn."""
import copy, json, sys, collections
from shapely.geometry import shape, mapping, Point, LineString
from shapely.ops import substring, transform
import pyproj

TK, OUT = sys.argv[1], sys.argv[2]
JLM = 'מטרופולין ירושלים'
to_itm = pyproj.Transformer.from_crs(4326, 2039, always_xy=True).transform
to_wgs = pyproj.Transformer.from_crs(2039, 4326, always_xy=True).transform
lines = json.load(open(f'{TK}/data/layers/lrt_line/lrt_line_2026-10.geojson', encoding='utf-8'))
stats = json.load(open(f'{TK}/data/layers/lrt_stat/lrt_stat_2026-10.geojson', encoding='utf-8'))


def feat(name):
    fs = [f for f in lines['features'] if f['properties']['MTR_AREA'] == JLM and f['properties']['NAME'] == name]
    assert len(fs) == 1, (name, len(fs))
    return fs[0]


st_itm = [(f, transform(to_itm, shape(f['geometry']))) for f in stats['features'] if f['properties']['MTR_AREA'] == JLM]


def along(geom, names_only=False):
    """Jerusalem stations within 50 m of a line, ordered along it: [(name, position_m, feature)]."""
    out = {}
    for f, p in st_itm:
        if p.distance(geom) < 50:
            out.setdefault(f['properties']['STAT_NAME'], (geom.project(p), f))
    return sorted(((n, pos, f) for n, (pos, f) in out.items()), key=lambda x: x[1])


def piece(src, geom_itm, a, b, status, note):
    g = substring(geom_itm, min(a, b), max(a, b))
    f = copy.deepcopy(src)
    f['geometry'] = mapping(transform(to_wgs, g))
    f['properties']['STATUS'] = status
    f['properties']['LENGT'] = round(g.length / 1000, 3) if isinstance(src['properties'].get('LENGT'), (int, float)) else src['properties'].get('LENGT')
    f['properties']['Shape_Leng'] = round(g.length, 3) if isinstance(src['properties'].get('Shape_Leng'), (int, float)) else src['properties'].get('Shape_Leng')
    log.append(f"{src['properties']['NAME']}: {note} -> {status} ({g.length/1000:.1f} km)")
    return f


log = []
new_features = []
opened = set()   # station names that are now in service

# 1) Red line extensions (Neve Yaakov - Hadassah Ein Kerem): in service since Feb 2025
red = feat('אדום'); red_g = transform(to_itm, shape(red['geometry']))
assert red_g.geom_type == 'LineString'
for n, pos, f in along(red_g):
    if f['properties']['LINE'].startswith('אדום'):
        opened.add(n)

# 2) L3 (layer name "ירוק מקוקו"): Malha - Binyanei HaUma - Damascus Gate in service (21.8.2026, extended 10.11.2026)
l3 = feat('ירוק מקוקו'); l3_g = transform(to_itm, shape(l3['geometry']))
assert l3_g.geom_type == 'LineString'
s3 = along(l3_g); pos3 = {n: p for n, p, _ in s3}
malha, gate = pos3['מנחת (מלחה)'], pos3['שער שכם']
far3 = 0.0 if malha < gate else l3_g.length          # the Modai end, beyond Malha
for n, p, f in s3:
    if min(malha, gate) - 1 <= p <= max(malha, gate) + 1 and n != 'שלומציון המלכה':
        opened.add(n)

# 3) Green line Gilo - Mount Scopus
gr = feat('ירוק'); gr_g = transform(to_itm, shape(gr['geometry']))
assert gr_g.geom_type == 'LineString'
sg = along(gr_g); posg = {n: p for n, p, _ in sg}
gilo, gon, bu = posg['גילה - מערב'], posg['גוננים'], posg['בנייני האומה']
endg = gr_g.length if bu > gilo else 0.0
startg = 0.0 if bu > gilo else gr_g.length

for f in lines['features']:
    p = f['properties']
    if p['MTR_AREA'] != JLM:
        new_features.append(f); continue
    if f is red:
        g = copy.deepcopy(f); g['properties']['STATUS'] = 'קיים'
        log.append('אדום: נווה יעקב – הדסה עין כרם -> קיים (כל הקו)'); new_features.append(g)
    elif f is l3:
        new_features.append(piece(f, l3_g, malha, gate, 'קיים', 'מלחה – שער שכם (L3)'))
        if abs(far3 - malha) > 30:
            new_features.append(piece(f, l3_g, far3, malha, p['STATUS'], 'יצחק מודעי – מלחה (ללא שינוי)'))
    elif f is gr:
        if abs(startg - gilo) > 30:
            new_features.append(piece(f, gr_g, startg, gilo, p['STATUS'], 'קצה גילה (ללא שינוי)'))
        new_features.append(piece(f, gr_g, gilo, gon, 'ביצוע', 'גילה – גוננים (L4, נסיעות מבחן, פתיחה מתוכננת 12/2026)'))
        new_features.append(piece(f, gr_g, gon, bu, 'קיים', 'גוננים – בנייני האומה (תוואי משותף עם L3)'))
        new_features.append(piece(f, gr_g, bu, endg, 'ביצוע', 'בנייני האומה – הר הצופים (פתיחה מתוכננת 2027)'))
    else:
        new_features.append(f)
lines['features'] = new_features

changed = collections.Counter()
for f in stats['features']:
    p = f['properties']
    if p['MTR_AREA'] == JLM and p['STAT_NAME'] in opened and p['STATUS'] != 'קיימת':
        p['STATUS'] = 'קיימת'; changed[p['STAT_NAME']] += 1

for name, d in (('lrt_line', lines), ('lrt_stat', stats)):
    json.dump(d, open(f'{OUT}/{name}_edit.geojson', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('\n'.join(log))
print('stations set to existing:', len(changed), sorted(changed))
c = collections.Counter((f['properties']['NAME'], f['properties']['STATUS']) for f in lines['features'] if f['properties']['MTR_AREA'] == JLM)
print('JLM lines after:', dict(c))
