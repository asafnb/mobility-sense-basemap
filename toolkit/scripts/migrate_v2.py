"""One-off migration (2026-10-21): turn the v2 build (legacy/build_v2.py) into the versioned toolkit.
Copies source GeoJSON into dated files, writes layers/layers.json and the har-hotzvim project layers.
Kept for the record; do not re-run (it refuses to overwrite)."""
import json,os,shutil,sys
sys.path.insert(0,os.path.dirname(__file__)); from lib import ROOT,file_info,save_json
H='/workspace/research/hatzav'; HH='/workspace/har-hotzvim-map/public/data'
man={l['layer_id']:l for l in json.load(open(f'{H}/manifest.json'))['layers']}
DRIVE={"nataz_kayam":"1eMCIv475qqzrZichdIiVoDlx2mZ4YYKt","nataz_planned":"10yxS1EOcp7i7nav_pqbtE1pJ-Wkv4Eqf","bicycle_jer_2019":"1TakTsKDJnV61imDlr-Z6yxi8BtYs35CD","bph_infra_exist":"1nW938p1kg5alG5wwNDdfojVG9fJUwWPR","bph_infra_plan":"1Ia1uPDfPfW7-7zY6AhdYvSwVcES8MZlv","ofneidan":"18P8qNBa4IzOOatE6MJypRIOaV5tvQHsX","brt_line":"1vb4iwwUy2LkahsbjdPizeWIr2JdETY7a","lrt_line":"1dI2ttSCDXyUGMp10eS1jhRUS0jQR1vbF","lrt_stat":"1E1OZS68xOgB3noj2dynCX5e0vF1ocCHS","mataan_jlm_2040":"13FfoAE2hUUF8afhLbBDONr1LJ3suWhuz","mataan_jlm_2050":"1eydeE0vzaa7ihanWlPy5gULox5HFZcP9","metro_line":"1WdnXJymGDL-EWsKbxYH9loa9jCW-x00-","metro_line_jlm":"1SzPQKZlEg0vYkaHKKy2wKTdm4gFZGBNW","metro_stat":"164l7bfZKUh3-ogbr0NZWk4tvnS0DKADf","rail_stat":"1oymkuJMuBLyb_29UDDhZsY7tIrWa87Df","rail_strat_station":"1S5KwElPNX-KT_9-pK2pHEil6hAKUd6vt","rail_strategic":"1XkTlupxCrH5ap_CLM0nxvirEm2kkCBso"}
DFOLD={"nataz":"1ccHoKntnfd1KRVLwYhDkqWLv29Vh7Iq7","bike":"1IXgWYqEFXWZc165jKFpvhMDPFE4shLNJ","mataan":"1mjssONFLKTPhhB-lZHH5219AfigORjQj"}
NATAZF=[("PTLNAME","שם"),("STATUS","סטטוס"),("PTLTYPE","סוג"),("AUTHORITY","רשות"),("TRAFAUTH","רשות תמרור"),("PTLDIR","כיוון"),("FRHR_WK","שעת התחלה (חול)"),("TOHR_WK","שעת סיום (חול)"),("LENGT","אורך (מ׳)"),("LASTCHANGE","עדכון אחרון")]
NATAZP=[("PTLNAME","שם"),("STATUS","סטטוס"),("PTLTYPE","סוג"),("AUTHORITY","רשות"),("ROADNAME","כביש"),("INAUGUR","מועד פתיחה"),("PLANOPER","גורם מתכנן"),("EXECOPER","גורם מבצע"),("SOURCE","מקור"),("LENGTH_M","אורך (מ׳)"),("LASTCHANGE","עדכון אחרון")]
BIKEE=[("STREETNAME","רחוב"),("AUTHORITY","רשות"),("BPHType","סוג"),("DirType","כיווניות"),("OPEN_YEAR","שנת פתיחה"),("USABLE","שמישות"),("LENGTH_M","אורך (מ׳)")]
BIKEP=[("STREETNAME","רחוב"),("AUTHORITY","רשות"),("STATUS","סטטוס"),("STARTDATE","תחילת ביצוע"),("FINISHDATE","סיום"),("PROJOPER","גורם מבצע"),("LEN","אורך (מ׳)")]
OFN=[("DP_NAME","שם"),("DP_DESC","תיאור"),("STATUS","סטטוס"),("COMP","גורם"),("LENGT","אורך (מ׳)")]
JB=[("name","שם"),("status","סטטוס"),("Year","שנה")]
LRTL=[("NAME","קו"),("LINE_EG","Line"),("STATUS","סטטוס"),("START_","מוצא"),("DESTNATION","יעד"),("MTR_AREA","מטרופולין"),("FREQ","תדירות (דק׳)"),("COMP","חברה")]
LRTS=[("STAT_NAME","תחנה"),("LINE","קו"),("STATUS","סטטוס"),("TYPE","סוג"),("ENTRC_EXIT","כניסה/יציאה"),("MTR_AREA","מטרופולין")]
MET=[("NAME","קו"),("DESCRPTION","תיאור")]; METS=[("NAME","תחנה"),("NAMEENG","Station"),("LINE","קו"),("MASAD","קוד")]
METJ=[("LINE_NAME","קו"),("YEAR","שנה")]
BRT=[("NAME","שם"),("LINE","קו"),("STATUS","סטטוס"),("ORIGIN","מוצא"),("DESTNATION","יעד"),("date","עדכון")]
RS=[("ASSET_NAME","תחנה"),("STATUS","סטטוס")]; RSL=[("SEGMENT","מקטע"),("UPGRADE","שדרוג"),("UPGRAD","טווח שדרוג"),("ISACTIVE","פעילות")]
RSS=[("STAT_NAMEH","תחנה"),("STAT_NAME","Station"),("YEAR","שנה")]
J40=[("LINE_NAME","קו"),("COLOR","צבע"),("ORIGIN","מוצא"),("DESTNATION","יעד")]; J50=[("LINE_NAME","קו"),("TYPE","סוג"),("YEAR","שנה")]
TMA=[("NAME","דרך"),("MAVAT_NAME","סיווג"),("REMARKS","הערות"),("DATA_DATE","תאריך נתונים")]
# web: popup fields kept in the slim web copy (None = all popup fields) and merge = dissolve identical-attribute features
D=[("nataz_kayam","נת״צ קיימים","g_nataz","nataz",NATAZF,None,False,"מסונן: STATUS≠מבוטל"),
("nataz_planned","נת״צ מתוכננים","g_nataz","nataz",NATAZP,["PTLNAME","STATUS","AUTHORITY","ROADNAME","INAUGUR"],True,""),
("bph_infra_exist","תשתית רכיבה קיימת","g_bike","bike",BIKEE,["STREETNAME","AUTHORITY","BPHType","OPEN_YEAR"],True,"מוצג מזום 9"),
("bph_infra_plan","תשתית רכיבה מתוכננת","g_bike","bike",BIKEP,["STREETNAME","AUTHORITY","STATUS","FINISHDATE"],True,"מוצג מזום 9"),
("ofneidan","אופנידן","g_bike","bike",OFN,None,False,""),
("bicycle_jer_2019","שבילי אופניים – ירושלים (2019)","g_bike","bike",JB,None,False,""),
("lrt_line","קווי רכבת קלה","g_lrt","mataan",LRTL,None,False,"צבע לפי שדה NAME"),
("lrt_stat","תחנות רכבת קלה","g_lrt","mataan",LRTS,None,False,""),
("metro_line","קווי מטרו (גוש דן)","g_metro","mataan",MET,None,False,""),
("metro_stat","תחנות מטרו","g_metro","mataan",METS,None,False,""),
("metro_line_jlm","מטרו – מטרופולין ירושלים","g_metro","mataan",METJ,None,False,""),
("brt_line","קווי BRT","g_brt","mataan",BRT,None,False,"מוצק כהה=בביצוע"),
("rail_strategic","מסילות – תכנית אסטרטגית","g_rail","mataan",RSL,None,False,""),
("rail_stat","תחנות רכבת נוסעים","g_rail","mataan",RS,None,False,""),
("rail_strat_station","תחנות – תכנית אסטרטגית","g_rail","mataan",RSS,None,False,""),
("mataan_jlm_2040","מתע״ן ירושלים 2040","g_jlm","mataan",J40,None,False,"צבע לפי שדה COLOR"),
("mataan_jlm_2050","מתע״ן ירושלים 2050","g_jlm","mataan",J50,None,False,"צבע לפי שדה LINE_NAME"),
]
reg_path=f'{ROOT}/layers/layers.json'
if os.path.exists(reg_path): sys.exit('layers.json exists – refusing to overwrite')
reg=dict(registry_version=1,updated="2026-10-21",github_size_limit_bytes=512000,
 _doc="כל שכבה: מטא־דאטה + רשימת גרסאות. קבצים מתוארכים ב־data/layers/<id>/<id>_<YYYY-MM>.geojson; אף פעם לא דורסים גרסה. storage=github → נכנס לריפו (קטן); drive → רק בדרייב.",
 layers={})
def add(lid,title,group,folder,popup,webf,merge,note,src_path,man_rec,drive_id=None,status="active"):
    ver=man_rec['download_date'][:7] if man_rec else "2026-10"
    dst=f"data/layers/{lid}/{lid}_{ver}.geojson"; os.makedirs(f"{ROOT}/data/layers/{lid}",exist_ok=True)
    if not os.path.exists(f"{ROOT}/{dst}"): shutil.copy2(src_path,f"{ROOT}/{dst}")
    fi=file_info(f"{ROOT}/{dst}")
    v=dict(version=ver,data_date=man_rec['download_date'] if man_rec else "2026-10-14",
      source_modified=(man_rec or {}).get('resource_last_modified','')[:10] or None,file=dst,**fi,
      storage="github+drive" if fi['bytes']<=reg['github_size_limit_bytes'] else "drive",
      drive_file_id=drive_id,drive_note="קובץ הדרייב נקרא בשם הישן <id>.geojson (תוכן זהה)" if drive_id else None,
      changes="גרסה ראשונה ברג'יסטרי (הורדה מ־data.gov.il ב־14.10.2026)")
    reg['layers'][lid]=dict(title=title,group=group,drive_folder=folder,drive_folder_id=DFOLD.get(folder),status=status,
      source=dict(publisher="משרד התחבורה / data.gov.il",dataset=(man_rec or {}).get('source_dataset'),endpoint=(man_rec or {}).get('endpoint'),ckan_api=(man_rec or {}).get('ckan_api')),
      attribution="משרד התחבורה / data.gov.il",note=note,crs="EPSG:2039→EPSG:4326",
      popup=dict(title_field=popup[0][0],fields=[list(p) for p in popup]),
      web=dict(fields=webf,merge=merge),current=ver,versions=[v])
for lid,title,g,folder,pop,webf,merge,note in D:
    add(lid,title,g,folder,pop,webf,merge,note,f"{H}/{folder}/{lid}.geojson",man[lid],DRIVE[lid])
tm=dict(download_date="2026-10-17",resource_last_modified="2020-03-01",source_dataset="https://data.gov.il/dataset/tma42_roads",endpoint=None,ckan_api=None)
add("tma42_roads","תמ״א 42 – כבישים (2020)","g_roads","new_roads",TMA,["NAME","MAVAT_NAME","REMARKS"],False,"מועמדת: לא נכללת בבסיס v3 עד אישור אסף. REMARKS='שמור לתכנון' = מתוכנן",
    f"{H}/new_roads/tma42_roads.geojson",tm,None,status="candidate")
reg['layers']['tma42_roads']['versions'][0]['data_date']="2026-10-17"
save_json(reg_path,reg)
# project layers (har-hotzvim)
P=f"{ROOT}/projects/har-hotzvim/layers"; os.makedirs(P,exist_ok=True)
for src,dst in [(f"{HH}/projects.geojson","hh_projects_2026-10.geojson"),(f"{HH}/companies.geojson","hh_companies_2026-10.geojson"),(f"{H}/project_road22_har_hotzvim/road22_jerusalem.geojson","road22_jlm_2026-10.geojson")]:
    if not os.path.exists(f"{P}/{dst}"): shutil.copy2(src,f"{P}/{dst}")
print("migrated",len(reg['layers']))
