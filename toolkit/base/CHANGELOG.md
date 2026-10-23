# CHANGELOG – מפת הבסיס

## v5 – 2026-10-23
- עיצוב: s2.0 → s3.0
- שכבה הוסרה: `bicycle_jer_2019`
- שכבה הוסרה: `metro_line_jlm`
- שכבה הוסרה: `mataan_jlm_2040`
- שכבה הוסרה: `mataan_jlm_2050`
- הערה: בסיס ארצי בלבד: שכבות ירושלים עברו לחבילה האזורית jerusalem j1 (regions/jerusalem). עיצוב s3.0: צבע אחד לכל משפחת תשתית, הסטטוס בסגנון הקו.
- קרדיט: אסף (23.10.2026): להוציא את ירושלים מהכללי לענף ירושלים; קיים ומתוכנן באותו צבע, הקיים מודגש
- שכבות ירושלים (`bicycle_jer_2019`, `metro_line_jlm`, `mataan_jlm_2040`, `mataan_jlm_2050`) עברו לחבילה האזורית `regions/jerusalem` j1, יחד עם `road22_jlm` ו־`hh_companies` מפרויקט הר החוצבים. גרסאות הנתונים לא השתנו (2026-10).
- שכבות נגזרות חדשות: `nataz_planned__constr(_core)`, `bph_infra_plan__constr(_core)`, `bicycle_jer_2019__plan` (בחבילה), `road22_jlm__core` (בחבילה).
- פרטים: `style/releases/s3.0/RELEASE.md`. לפני/אחרי (רינדור GeoLibre Web): `style/releases/s3.0/tel-aviv_compare.png`, `gush-dan_compare.png`, `national_compare.png`, `jerusalem_compare.png`, `har-hotzvim_compare.png`.
- קישור הלחיצה האחת = v5 בלבד (בלי ירושלים ובלי פרויקטים). הר החוצבים: `projects/har-hotzvim.web.geolibre.json`.
- פרויקט `har-hotzvim` שודרג ל־p3 על v5 + jerusalem j1.

## v4 – 2026-10-21
- עיצוב: s1 → s2.0
- הערה: עיצוב s2.0 לפי סקירת העיצוב של Carto: קיים=רציף, בביצוע=קו חלול, מתוכנן=מקווקו (ריבועים לבנים); פסי זום ורוחבים; תיקוני באגים (קו אדום קיים בירושלים, LRT ומסילות לפי סטטוס, בלי בוטל/מוקפא, מקרא)
- קרדיט: סקירת העיצוב של Carto (21.10.2026, /workspace/carto/geolibre-review/review.md)
- תיקונים: קו אדום קיים בירושלים צבוע נכון; רכבת קלה ומסילות לפי קיים/בביצוע/מתוכנן (לא פעיל וחדש 2030/2040 = מתוכנן); תשתית רכיבה מתוכננת בלי בוטל/מוקפא; אופנידן לפי הסטטוסים האמיתיים (HOLD לא מוצג); fillOpacity של קווים = 1; מטרו #312E81; מתוכנן מתחת לקיים; מקרא מלמעלה למטה.
- שכבות נגזרות חדשות (אותם נתונים, מסנן אחר): `lrt_line__plan`, `lrt_line__plan_nat`, `lrt_line__constr`, `lrt_line__constr_core`, `rail_strategic__plan`, `rail_strategic__plan_nat`, `brt_line__nat`, `brt_line__constr`, `brt_line__constr_core`, `metro_line__nat`, `ofneidan__plan`, `ofneidan__constr`, `ofneidan__constr_core`. גרסאות הנתונים לא השתנו (2026-10).
- פרטים: `style/releases/s2.0/RELEASE.md`. לפני/אחרי (רינדור GeoLibre Web): `style/releases/s2.0/national_compare.png`, `tel-aviv_compare.png`, `jerusalem_compare.png`, `har-hotzvim_compare.png`.
- פרויקט `har-hotzvim` שודרג ל־p2 על v4: כביש 22 (ירושלים) כקו חלול (בביצוע), צבעים מטוקני PROJ_*, רשומות מקרא משלו.

## v3 – 2026-10-21
- מעבר למבנה גרסאות: עיצוב `s1` (style/versions/style_s1.json) + 17 שכבות ארציות בגרסה `2026-10`.
- הבסיס מכיל רק שכבות ארציות. שכבות הר החוצבים (חברות, פרויקטים, כביש 22 ירושלים) עברו לפרויקט `har-hotzvim` (p1).
- סימניית "ירושלים / הר החוצבים" בבסיס הפכה ל"ירושלים"; סימניית הר החוצבים נמצאת בפרויקט.
- תמ״א 42 – כבישים רשומה ב־layers.json כמועמדת (status=candidate), לא נכללת.
- הנתונים זהים ל־v2 (הורדה מ־data.gov.il ב־14.10.2026). העיצוב זהה ל־v2.

## v2 – 2026-10-14 (לפני מבנה הגרסאות)
- נוסף כביש 22 (ירושלים) מ־OpenStreetMap לקבוצת הר החוצבים. קובץ בדרייב: 17AAA1CC4PfBhyv6VGwsREZM_8rCKWeQ_. נבנה ע״י legacy/build_v2.py.

## v1 – 2026-10-14
- גרסה ראשונה: 19 שכבות (חצב + הר החוצבים). הקובץ הועבר לסל באישור אסף אחרי v2.
