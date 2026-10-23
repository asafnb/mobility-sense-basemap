"""One-off: build style/style.json s3.0 from s2.0 (Asaf, 23.10.2026):
 1) one colour per infrastructure family – existing / under construction / planned share the SAME hue;
    status = line treatment: existing thick+solid+opaque, under construction hollow, planned thin+dashed(white squares)+60% opacity.
 2) Jerusalem-only layers move from the national base to the regional pack regions/jerusalem (j1);
    their styles stay here (one style for everything) but the base no longer pins them.
Major bump (s3.0): new derived layer ids (nataz_planned__constr*, bph_infra_plan__constr*, bicycle_jer_2019__plan,
road22_jlm(__core), hh_companies), palette tokens removed (BUS_NAT/BUS_P/BIKE_P/OFN_E/OFN_C/OFN_P), new spec key 'opacity'."""
import json,copy
ROOT='/workspace/geolibre'
S=json.load(open(f'{ROOT}/style/versions/style_s2.0.json'))
S['style_version']='s3.0'; S['updated']='2026-10-23'
S['description']=("סגנון מפת הבסיס של Mobility Sense. s3.0 = צבע אחד לכל משפחת תשתית (נת״צ, אופניים, אופנידן, רכבת קלה לפי צבע קו, מטרו, BRT, רכבת כבדה). "
  "הסטטוס מוצג בסגנון הקו ולא בצבע: קיים = קו עבה, רציף, אטום; בביצוע = קו חלול; מתוכנן = קו דק, מקווקו (ריבועים לבנים) ושקוף 60%. בוטל/מוקפא לא מוצגים. "
  "שכבות ירושלים בלבד עברו לחבילה האזורית regions/jerusalem.")
PL=S['palette']
for k in ['BUS_NAT','BUS_P','BIKE_P','OFN_E','OFN_C','OFN_P']: PL.pop(k,None)
PL.update(OFN="#0F766E",ROAD_NEW="#6D28D9",ROAD_NEW_INK="#4C1D95",POI_CO="#0D9488",POI_CO_INK="#115E59")
OP=0.6   # planned opacity
S['planned']=dict(S['planned'],opacity=OP,_note="מתוכנן = אותו צבע כמו הקיים, קו דק יותר + ריבועים לבנים לאורכו (מראה מקווקו; GeoLibre אינו תומך ב-dasharray) + שקיפות 60% (opacity). בביצוע = קו חלול (שכבת צבע + ליבה לבנה). קיים = קו עבה, רציף, אטום.")
S['status_encoding']={"_doc":"צבע = משפחת תשתית; סגנון = סטטוס. רוחבים לפי zoom_bands (ארצי / מטרופולין / עיר).",
  "existing":"עבה, רציף, opacity 1","under_construction":"חלול: מסגרת בצבע המשפחה + ליבה לבנה","planned":f"דק, ריבועים לבנים (מקווקו), opacity {OP}"}
def rules(widths,color,label,bands=((None,10),(10,13),(13,None))):
    out=[]
    for i,(lo,hi) in enumerate(bands):
        r={"id":f"r{i}","label":label,"isElse":False,"filter":"[\"all\"]","color":color,"strokeWidth":widths[i]}
        if lo is not None: r['minZoom']=lo
        if hi is not None: r['maxZoom']=hi
        out.append(r)
    return {"vectorStyleMode":"rule-based","vectorRules":out}
def deco(size,spacing): return {"lineDecoration":"square","lineDecorationColor":"#ffffff","lineDecorationSize":size,"lineDecorationSpacing":spacing}
def recolor_rules(spec,widths):   # LRT-style per-line rules: keep colours, new widths per band
    for r in spec['extra']['vectorRules']: r['strokeWidth']=widths[int(r['id'][1:])%3]
L=S['layers']; LRT=S['categories']['LRT']
BUS,BIKE,OFN,RAIL,METRO,BRT,W=PL['BUS'],PL['BIKE'],PL['OFN'],PL['RAIL'],PL['METRO'],PL['BRT'],"#FFFFFF"
# ---------- נת"צ ----------
L['nataz_kayam']['extra']=dict(L['nataz_kayam']['extra'],**rules([0.9,2.0,3.2],BUS,"קיים"))
NP_C=["==",["get","STATUS"],"בביצוע"]
L['nataz_planned']={"kind":"line","color":"@BUS","width":1.1,"opacity":OP,"filter":["!",NP_C],
  "extra":{"minZoom":11,**rules([0.8,1.1,1.6],BUS,"מתוכנן"),**deco(4,9)}}
L['nataz_planned__constr']={"source":"nataz_planned","title":"נת״צ – בביצוע","kind":"line","color":"@BUS","width":2.4,"filter":NP_C,
  "extra":{"minZoom":10,**rules([1.4,2.6,3.8],BUS,"בביצוע")}}
L['nataz_planned__constr_core']={"source":"nataz_planned","title":"נת״צ בביצוע (ליבה)","legend":False,"kind":"line","color":"@WHITE","width":1,"filter":NP_C,
  "extra":{"minZoom":10,**rules([0.5,1.0,1.5],W,"ליבה")}}
# ---------- אופניים ----------
L['bph_infra_exist']['extra']=dict(L['bph_infra_exist']['extra'],**rules([1.0,1.5,2.6],BIKE,"קיים"))
BP_C=["==",["get","STATUS"],"בביצוע"]
L['bph_infra_plan']={"kind":"line","color":"@BIKE","width":1.0,"opacity":OP,"filter":["!",["in",["get","STATUS"],["literal",["בוטל","מוקפא","בביצוע"]]]],
  "extra":{"minZoom":12,**rules([0.8,1.0,1.4],BIKE,"מתוכנן"),**deco(4,9)}}
L['bph_infra_plan__constr']={"source":"bph_infra_plan","title":"תשתית רכיבה – בביצוע","kind":"line","color":"@BIKE","width":2,"filter":BP_C,
  "extra":{"minZoom":12,**rules([1.4,2.0,3.0],BIKE,"בביצוע")}}
L['bph_infra_plan__constr_core']={"source":"bph_infra_plan","title":"תשתית רכיבה בביצוע (ליבה)","legend":False,"kind":"line","color":"@WHITE","width":1,"filter":BP_C,
  "extra":{"minZoom":12,**rules([0.5,0.8,1.2],W,"ליבה")}}
JB_E=["==",["get","status"],"קיים"]
L['bicycle_jer_2019']={"kind":"line","color":"@BIKE","width":1.5,"visible":False,"filter":JB_E,"extra":{"minZoom":11,**rules([1.0,1.5,2.6],BIKE,"קיים")}}
L['bicycle_jer_2019__plan']={"source":"bicycle_jer_2019","title":"שבילי אופניים ירושלים 2019 – בתכנון","kind":"line","color":"@BIKE","width":1,"opacity":OP,"visible":False,"filter":["!",JB_E],
  "extra":{"minZoom":11,**rules([0.8,1.0,1.4],BIKE,"בתכנון"),**deco(4,9)}}
# ---------- אופנידן (משפחה אחת, צבע אחד) ----------
L['ofneidan']['color']="@OFN"; L['ofneidan']['label']['color']=OFN
L['ofneidan']['extra']=dict(L['ofneidan']['extra'],**rules([2.0,2.6,3.8],OFN,"נפתח לתנועה"))
L['ofneidan__constr']['color']="@OFN"; L['ofneidan__constr']['extra']=dict(L['ofneidan__constr']['extra'],**rules([2.2,3.2,4.4],OFN,"בביצוע"))
L['ofneidan__plan']=dict(L['ofneidan__plan'],color="@OFN",width=1.6,opacity=OP)
L['ofneidan__plan']['extra']=dict(L['ofneidan__plan']['extra'],**rules([1.2,1.6,2.2],OFN,"בתכנון"),**deco(5,10))
# ---------- רכבת כבדה ----------
L['rail_strategic']['extra']=dict(L['rail_strategic']['extra'],**rules([1.6,2.4,3.4],RAIL,"פעיל"))
L['rail_strategic__plan']=dict(L['rail_strategic__plan'],width=1.4,opacity=OP)
L['rail_strategic__plan']['extra']=dict(L['rail_strategic__plan']['extra'],**rules([1.0,1.4,2.0],RAIL,"מתוכנן"),**deco(5,11))
L['rail_strategic__plan_nat']=dict(L['rail_strategic__plan_nat'],color="@RAIL",width=1.0,opacity=0.45)
# ---------- BRT ----------
L['brt_line']=dict(L['brt_line'],width=1.6,opacity=OP); L['brt_line']['extra']=dict(L['brt_line']['extra'],**rules([1.0,1.6,2.2],BRT,"בתכנון / בדיקה"),**deco(5,11))
L['brt_line__nat']=dict(L['brt_line__nat'],color="@BRT",width=1.0,opacity=0.45)
L['brt_line__constr']['extra']=dict(L['brt_line__constr']['extra'],**rules([2.0,3.6,5.0],BRT,"בביצוע"))
# ---------- מטרו (כל הקווים בתכנון) ----------
for k in ('metro_line','metro_line_jlm'):
    L[k]=dict(L[k],width=2.4,opacity=0.65); L[k]['extra']=dict(L[k]['extra'],**rules([1.6,2.4,3.4],METRO,"מתוכנן"),**deco(5,12))
L['metro_line__nat']=dict(L['metro_line__nat'],color="@METRO",width=1.2,opacity=0.5)
# ---------- רכבת קלה: צבע = צבע הקו, אותו צבע לכל הסטטוסים ----------
recolor_rules(L['lrt_line'],[2.4,4.0,5.6]); recolor_rules(L['lrt_line__constr'],[2.4,4.0,5.6])
L['lrt_line__constr_core']['extra']=dict(L['lrt_line__constr_core']['extra'],**rules([0.9,1.8,2.6],W,"ליבה"))
L['lrt_line__plan']=dict(L['lrt_line__plan'],width=2,opacity=OP); recolor_rules(L['lrt_line__plan'],[1.2,2.0,2.8])
L['lrt_line__plan']['extra'].update(deco(5,12))
L['lrt_line__plan_nat']=dict(L['lrt_line__plan_nat'],width=1.0,opacity=0.5,categorized={"prop":"NAME","map":dict(LRT,**{"קו אדום קיים":LRT["אדום"],"אדום מקוקו":LRT["אדום"],"ירוק מקוקו":LRT["ירוק"]})})
for k in ('mataan_jlm_2040','mataan_jlm_2050'):
    L[k]=dict(L[k],width=1.8,opacity=OP); L[k]['extra']=dict(L[k]['extra'],**deco(5,12))
# ---------- חבילה אזורית ירושלים: כביש 22 (בביצוע = חלול), חברות הר החוצבים ----------
RB=((None,13),(13,15),(15,None))
L['road22_jlm']={"kind":"line","color":"@ROAD_NEW","width":5,"label":{"field":"name","placement":"line","minZoom":14,"color":"@ROAD_NEW_INK","size":12,"haloColor":"#ffffff","haloWidth":2,"maxWidth":8,
  "sizeExpression":"[\"interpolate\",[\"linear\"],[\"zoom\"],14,11,16,14]"},"extra":rules([3,5,7],PL['ROAD_NEW'],"בביצוע",RB)}
L['road22_jlm__core']={"source":"road22_jlm","title":"כביש 22 (ירושלים) – בביצוע (ליבה)","legend":False,"kind":"line","color":"@WHITE","width":2,"extra":rules([1.2,2.2,3.2],W,"ליבה",RB)}
L['hh_companies']={"kind":"point","color":"@POI_CO","radius":6,"extra":{"strokeColor":"#ffffff","strokeWidth":1.5},
  "label":{"field":"name_he","placement":"point","minZoom":14,"anchor":"top","offsetY":1,"color":"@POI_CO_INK"}}
# ---------- groups (Jerusalem groups now come from the region pack) ----------
S['groups']=[g for g in S['groups'] if g['id']!='g_jlm']
for g in S['groups']:
    if g['id']=='g_bike': g['name']="אופניים"
S['_groups_note']="קבוצות ריקות לא נכתבות לקובץ. קבוצות של חבילה אזורית מוגדרות ב־regions/<id>/<ver>/manifest.json."
# ---------- draw order ----------
S['layer_stack_bottom_to_top']=["bicycle_jer_2019__plan","bicycle_jer_2019","bph_infra_plan","bph_infra_plan__constr","bph_infra_plan__constr_core","bph_infra_exist",
 "ofneidan__plan","ofneidan","ofneidan__constr","ofneidan__constr_core","nataz_planned","nataz_planned__constr","nataz_planned__constr_core","nataz_kayam",
 "road22_jlm","road22_jlm__core","mataan_jlm_2040","mataan_jlm_2050",
 "rail_strategic__plan_nat","rail_strategic__plan","rail_strategic","brt_line__nat","brt_line","brt_line__constr","brt_line__constr_core",
 "metro_line__nat","metro_line_jlm","metro_line","lrt_line__plan_nat","lrt_line__plan","lrt_line__constr","lrt_line__constr_core","lrt_line",
 "rail_strat_station","rail_stat","metro_stat","lrt_stat","hh_companies"]
# ---------- legend: one section per family, one row per status ----------
def tint(h,a=OP):
    h=h.lstrip('#'); c=[int(h[i:i+2],16) for i in (0,2,4)]; return "#%02X%02X%02X"%tuple(round(x*a+255*(1-a)) for x in c)
def item(label,color,size,planned=False): return {"label":label,"color":tint(color) if planned else color,"shape":"line","size":size}
def fam(title,c,e,cs,p,ex="קיים",pl="מתוכנן"):
    it=[]
    if e: it.append(item(f"{ex} – קו עבה ורציף",c,e))
    if cs: it.append(item("בביצוע – קו חלול",c,cs))
    if p: it.append(item(f"{pl} – קו דק, מקווקו ושקוף",c,p,True))
    return {"title":title,"items":it}
CE={"custom:status":{"title":"איך לקרוא את המפה: צבע = סוג תשתית · סגנון הקו = סטטוס","items":[
   item("קיים – קו עבה, רציף, צבע מלא",RAIL,4),item("בביצוע – קו חלול (מסגרת בצבע, ליבה לבנה)",RAIL,4),
   item("מתוכנן – אותו צבע, קו דק מקווקו ושקוף",RAIL,2,True),{"label":"בוטל / מוקפא – לא מוצג","color":"#D1D5DB","shape":"line","size":1}]}}
lrt=[item("קיים – קו עבה ורציף (אדום: ת״א, ירושלים)",LRT['אדום'],4),item("בביצוע – קו חלול (סגול)",LRT['סגול'],4)]
lrt+=[item(f"מתוכנן – {n}",LRT[n],2,True) for n in ["אדום","ירוק","ירוק בהיר","סגול","כחול","תכלת","צהוב","נופית","ורוד","חום","חום דרומי"]]
CE['lrt_line']={"title":"רכבת קלה (צבע = צבע הקו) – קיים / בביצוע / מתוכנן","items":lrt}
CE['metro_line']=fam("מטרו גוש דן (M1–M3) – מתוכנן",METRO,0,0,3)
CE['brt_line']=fam("BRT – בביצוע / מתוכנן",BRT,0,4,2,pl="בתכנון / בדיקת ישימות")
CE['rail_strategic']=fam("רכבת כבדה – פעילה / מתוכננת",RAIL,3,0,1.6,ex="פעילה",pl="מתוכננת / לא פעילה")
CE['rail_stat']=S['legend']['customEntries']['rail_stat']
CE['nataz_kayam']=fam("נת״צ – קיים / בביצוע / מתוכנן",BUS,3,3.5,1.4,pl="מתוכנן (מזום 11)")
CE['ofneidan']=fam("אופנידן – קיים / בביצוע / מתוכנן",OFN,3.5,4,2,ex="נפתח לתנועה",pl="בתכנון (מזום 11; ללא HOLD)")
CE['bph_infra_exist']=fam("תשתית רכיבה – קיים / בביצוע / מתוכנן",BIKE,2.5,3,1.2,ex="קיימת (מזום 11)",pl="מתוכננת (מזום 12; ללא בוטל/מוקפא)")
# region-pack layers (shown only when the region pack is loaded)
CE['metro_line_jlm']=fam("ירושלים · מטרו – מתוכנן",METRO,0,0,3)
CE['mataan_jlm_2040']={"title":"ירושלים · תוכנית מתע״ן 2040 – מתוכנן (צבע = צבע הקו)","items":[item("קו מתוכנן",LRT['ירוק'],2,True),item("קו מתוכנן",LRT['כחול'],2,True)]}
CE['mataan_jlm_2050']={"title":"ירושלים · תוכנית מתע״ן 2050 – מתוכנן (צבע = צבע הקו)","items":[item("קו מתוכנן",LRT['אדום'],2,True),item("קו מתוכנן",LRT['סגול'],2,True)]}
CE['bicycle_jer_2019']=fam("ירושלים · שבילי אופניים 2019 – קיים / בתכנון",BIKE,2.5,0,1.2,pl="בתכנון")
CE['road22_jlm']={"title":"ירושלים · כביש 22 – בביצוע (קו חלול)","items":[item("בביצוע · פתיחה צפויה: סוף 2027",PL['ROAD_NEW'],5)]}
CE['hh_companies']={"title":"ירושלים · חברות ומשרדים – הר החוצבים","items":[{"label":"חברה / משרד","color":PL['POI_CO'],"shape":"circle","size":6}]}
HIDE=["nataz_planned","nataz_planned__constr","bph_infra_plan","bph_infra_plan__constr","ofneidan__constr","ofneidan__plan","rail_strategic__plan","brt_line__constr",
      "lrt_line__constr","lrt_line__plan","bicycle_jer_2019__plan"]
OV={k:{"hidden":True} for k in HIDE}
for k,v in L.items():
    if v.get('legend') is False: OV[k]={"hidden":True}
S['legend']=dict(S['legend'],customEntries=CE,overrides=OV,order=["custom:status","lrt_line","metro_line","brt_line","rail_strategic","rail_stat","nataz_kayam","ofneidan","bph_infra_exist",
  "metro_line_jlm","mataan_jlm_2040","mataan_jlm_2050","bicycle_jer_2019","road22_jlm","hh_companies"],
  _order_note="סדר המקרא מלמעלה למטה. מקטע אחד לכל משפחת תשתית, שורה לכל סטטוס; שכבות הסטטוס האחרות של אותה משפחה מוסתרות במקרא (overrides). צבעי 'מתוכנן' במקרא = הצבע בשקיפות 60% על לבן.")
S['override_policy']['forbidden_on_base_layers']+="; opacity (חלק מקידוד הסטטוס)"
json.dump(S,open(f'{ROOT}/style/style.json','w',encoding='utf-8'),ensure_ascii=False,indent=1); open(f'{ROOT}/style/style.json','a').write('\n')
print("wrote style.json",S['style_version'],len(L),"layer specs")
