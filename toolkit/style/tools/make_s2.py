"""One-off: build style/style.json s2.0 from Carto's review proposal (/workspace/carto/geolibre-review/style-proposal.json)
+ s1 shared blocks + fixes found while applying it (ofneidan status values, EN category, mataan zoom gating)."""
import json,copy
S1=json.load(open('/workspace/geolibre/style/versions/style_s1.json'))
P=json.load(open('/workspace/carto/geolibre-review/style-proposal.json'))
S=copy.deepcopy(S1)
S['style_version']='s2.0'; S['updated']='2026-10-21'
S['description']="סגנון מפת הבסיס של Mobility Sense. s2.0 = יישום סקירת העיצוב של Carto (21.10.2026). קיים = קו רציף, בביצוע = קו חלול, מתוכנן = קו מקווקו (ריבועים לבנים). בוטל/מוקפא לא מוצגים."
S['palette']=dict(P['palette'],PROJ_ROAD="#6D28D9",PROJ_ROAD_INK="#4C1D95",PROJ_POI="#F59E0B",PROJ_POI_INK="#92400E",PROJ_CO="#0D9488",PROJ_CO_INK="#115E59")  # PROJ_* = tokens for project-owned layers
LRT=dict(P['categories']['LRT'])
EN={"RED":LRT["אדום"],"GREEN":LRT["ירוק"],"LIGHT GREEN":LRT["ירוק בהיר"],"BLUE":LRT["כחול"],"LIGHT BLUE":LRT["תכלת"],
    "PINK":LRT["ורוד"],"YELLOW":LRT["צהוב"],"BROWN":LRT["חום"],"ORANGE":"#EA580C","PURPLE":LRT["סגול"]}
S['categories']={"LRT":LRT,"EN":EN}
S['line_defaults']=P['line_defaults']
S['planned']=P['planned']
S['label_defaults'].update(P['label_defaults_patch'])
S['zoom_bands']=P['zoom_bands']
S['layer_stack_bottom_to_top']=list(P['layer_stack_bottom_to_top'])
L=copy.deepcopy(P['layers'])
# --- fix: ofneidan STATUS values in the data are נפתח לתנועה/ביצוע/תכנון/הליך מכרזי/ייזום/לא הוקצה/HOLD (no 'קיים').
OFN_E=["==",["get","STATUS"],"נפתח לתנועה"]; OFN_C=["==",["get","STATUS"],"ביצוע"]
OFN_P=["in",["get","STATUS"],["literal",["תכנון","הליך מכרזי","ייזום","לא הוקצה"]]]   # HOLD = frozen -> excluded
def rules(widths,color,label):
    B=[(None,10),(10,13),(13,None)]; out=[]
    for i,(lo,hi) in enumerate(B):
        r={"id":f"r{i}","label":label,"isElse":False,"filter":"[\"all\"]","color":color,"strokeWidth":widths[i]}
        if lo is not None: r['minZoom']=lo
        if hi is not None: r['maxZoom']=hi
        out.append(r)
    return {"vectorStyleMode":"rule-based","vectorRules":out}
lab=L['ofneidan']['label']
L['ofneidan']={"kind":"line","color":"@OFN_E","width":3,"filter":OFN_E,"label":lab,
    "extra":{"minZoom":10,**rules([2,2.5,3.5],"#065F46","נפתח לתנועה")}}
L['ofneidan__constr']={"source":"ofneidan","title":"אופנידן – בביצוע","kind":"line","color":"@OFN_C","width":3,"filter":OFN_C,
    "extra":{"minZoom":10,**rules([2.2,3.2,4.4],"#0F766E","בביצוע")}}
L['ofneidan__constr_core']={"source":"ofneidan","title":"אופנידן בביצוע (ליבה)","legend":False,"kind":"line","color":"@WHITE","width":1,"filter":OFN_C,
    "extra":{"minZoom":10,**rules([1,1.4,2],"#FFFFFF","ליבה")}}
L['ofneidan__plan']={"source":"ofneidan","title":"אופנידן – בתכנון","kind":"line","color":"@OFN_P","width":3,"filter":OFN_P,
    "extra":{"minZoom":11,**rules([2,2.5,3.5],"#4FB3A9","בתכנון"),"lineDecoration":"square","lineDecorationColor":"#ffffff","lineDecorationSize":5,"lineDecorationSpacing":11}}
st=S['layer_stack_bottom_to_top']; i=st.index('ofneidan')
st[i:i+1]=['ofneidan__plan','ofneidan','ofneidan__constr','ofneidan__constr_core']
# --- mataan JLM plans: all planned -> knock-out dashes only from z10 (decorations swamp thin lines below)
for k in ('mataan_jlm_2040','mataan_jlm_2050'): L[k]['extra']['minZoom']=10
S['layers']=L
leg=copy.deepcopy(P['legend'])
leg['customEntries']['ofneidan']={"title":"אופנידן","items":[{"label":"נפתח לתנועה","color":"#065F46","shape":"line","size":3}]}
leg['customEntries']['ofneidan__constr']={"title":"אופנידן – בביצוע (קו חלול)","items":[{"label":"בביצוע","color":"#0F766E","shape":"line","size":4}]}
leg['customEntries']['ofneidan__plan']={"title":"אופנידן – בתכנון (מקווקו, מזום 11)","items":[{"label":"תכנון / מכרז / ייזום (ללא HOLD)","color":"#4FB3A9","shape":"line","size":3}]}
leg['customEntries']['metro_line_jlm']={"title":"מטרו ירושלים – מתוכנן","items":[{"label":"מתוכנן (מזום 10)","color":"#312E81","shape":"line","size":4}]}
o=leg['order']; o.insert(o.index('metro_line')+1,'metro_line_jlm'); j=o.index('ofneidan'); o[j+1:j+1]=['ofneidan__constr','ofneidan__plan']
leg['overrides']={k:{"hidden":True} for k,v in L.items() if v.get('legend') is False}
leg['_order_note']="סדר המקרא מלמעלה למטה (top-first). שכבות שלא ברשימה מוצגות אחריה."
S['legend']=leg
S.pop('layer_order',None); S.pop('_layer_order_note',None)
S['_stack_note']="layer_stack_bottom_to_top קובע את סדר הציור (האחרון למעלה). שכבות פרויקט מצוירות מעל כל שכבות הבסיס."
S['_derived_note']="שכבה עם 'source' = שכבה נגזרת: אותם נתונים ואותה גרסה כמו שכבת המקור ברשום, עם filter וסגנון משלה (למשל קו חלול = שכבת צבע + שכבת ליבה לבנה)."
S['override_policy']={
 "_doc":"כללי style_overrides בפרויקט (נאכפים ב־lib.compose)",
 "base_layer_allowed_keys":["visible","width","label","extra.minZoom","extra.maxZoom"],
 "forbidden_on_base_layers":"צבע, palette, categorized, filter, planned, lineDecoration*, vectorRules – קידוד הסטטוס (רציף/חלול/מקווקו) והפלטה קבועים לכל הפרויקטים",
 "merge":"deep merge; רשימות (vectorRules, filter, customEntries.items) מוחלפות בשלמותן; כמה פרויקטים – האחרון בשורת הפקודה גובר, עם אזהרה על התנגשות",
 "project_layers":"שכבות של הפרויקט חופשיות, אבל צבעים צריכים להיות טוקנים מה־palette (@TOKEN)"}
json.dump(S,open('/workspace/geolibre/style/style.json','w'),ensure_ascii=False,indent=1)
print(len(L),'layer specs; stack',len(st))
