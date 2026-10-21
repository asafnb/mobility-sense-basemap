# Mobility Sense – ערכת מפת הבסיס ב־GeoLibre

הערכה מנהלת מפת בסיס אחת לכל הפרויקטים, עם גרסאות לעיצוב, לשכבות ולבסיס עצמו. שום קובץ לא נדרס: כל שינוי יוצר גרסה חדשה, והגרסה הקודמת נשארת.

## שלושה דברים, לכל אחד גרסה משלו

| מה | איפה | גרסה |
|---|---|---|
| **עיצוב**: צבעים, עוביים, קיים/בביצוע/מתוכנן, תוויות, מקרא, קבוצות, סדר ציור | `style/style.json` (עותק עבודה), `style/versions/style_s2.0.json` (קפוא), `style/releases/<גרסה>/` (לפני/אחרי) | `s1.0`, `s2.0`, `s2.1`, ... |
| **שכבות**: כל שכבה עם מקור, תאריך, גודל ומיקום אחסון | `layers/layers.json` + `data/layers/<id>/<id>_<YYYY-MM>.geojson` | `2026-10`, `2026-11`, ... |
| **בסיס** = עיצוב + גרסה מוצמדת לכל שכבה | `base/v3/manifest.json`, יומן ב־`base/CHANGELOG.md` | `v3`, `v4`, ... |
| **פרויקט** = בסיס מוצמד + שכבות הפרויקט + סימנייה + שינויי עיצוב מקומיים | `projects/<slug>/project.json` | `p1`, `p2`, ... |

**אחסון:** שכבה עד 512KB נכנסת גם לגיטהאב (`toolkit/`). שכבות כבדות (נת"צ, שבילי אופניים, אופנידן, מסילות) נמצאות רק בדרייב, בתיקיות חצב, ומזהה הקובץ שלהן רשום ב־`layers.json`. הקובץ המלא של כל בסיס או פרויקט (בערך 25MB) עולה לדרייב כקובץ חדש עם שם מגורסה. העותק הקל לרשת (פחות מ־3.3MB) עולה לגיטהאב.

**קישור הלחיצה האחת** מציג את הבסיס יחד עם הפרויקטים הפעילים (ההגדרה ב־`publish/web_root.json`). שם הקובץ בגיטהאב קבוע (`mobility-sense-base.geolibre.json`), ולכן הקישור לא משתנה.

## קידוד הסטטוס (מ־s2.0, לפי סקירת Carto)
- **קיים** = קו רציף. **בביצוע** = קו חלול (שכבת צבע ומעליה ליבה לבנה). **מתוכנן** = קו מקווקו (ריבועים לבנים לאורך הקו). בוטל ומוקפא לא מוצגים.
- ב־GeoLibre אין `dasharray`, ולכן המקווקו נוצר מ־`lineDecoration: square` בלבן. תחבורה מתוכננת מוצגת מזום 10, ומתחת לזה בגרסה ארצית דקה (`*_nat`).
- **שכבה נגזרת**: רשומה ב־`style.json` עם `"source": "<id>"` משתמשת באותם נתונים ובאותה גרסה כמו שכבת המקור, עם `filter` וסגנון משלה (`lrt_line__constr`, `lrt_line__constr_core`, ...). בפרויקט עושים את זה עם `"derived_from": "<id>"`.
- סדר הציור קבוע ב־`layer_stack_bottom_to_top`: מתוכנן מתחת לקיים, ושכבות הפרויקט מעל הכול. המקרא נקבע ב־`legend.order` (מלמעלה למטה) וב־`legend.customEntries`, ושכבות עזר מוסתרות ממנו (`"legend": false`).

## שינוי עיצוב
1. עורכים את `style/style.json` ומעלים את `style_version` לפי הכלל `s<major>.<minor>`:
   - **minor** (s2.0 ← s2.1): צבע, עובי או תווית, בלי שינוי במזהי השכבות.
   - **major** (s2.x ← s3.0): שכבה חדשה, פיצול לשכבות נגזרות או שינוי במבנה. `s1` הישנה = `s1.0`.
2. `python scripts/release_style.py`: מקפיא את הגרסה. גרסה שכבר שוחררה לא נדרסת.
3. `python scripts/make_base.py v5 --note "..." --credit "..."`: בסיס חדש עם העיצוב החדש ואותן שכבות. נרשם ביומן.
4. `python scripts/build_base.py v5`, ואחר כך פרויקט לדוגמה או showcase.
5. **לפני/אחרי בכל שחרור עיצוב:** `python scripts/render_release.py s2.1 --before dist/<קודם>.web.geolibre.json --after dist/<חדש>.web.geolibre.json`
   - מרנדר ארבעה מבטים (ארצי, תל אביב, ירושלים, הר החוצבים) ב־GeoLibre Web האמיתי, ושומר `style/releases/<גרסה>/*_compare.png`. את הנתיבים מוסיפים ל־CHANGELOG.
   - צריך: google-chrome ו־playwright-core (`/workspace/geolibre-render`), ו־Pillow (ב־python של המערכת).
6. העלאה (ראו "פרסום"). הפרויקטים נשארים על הבסיס הקודם עד שמשדרגים אותם.

## שינויי עיצוב בפרויקט (`style_overrides`), כללים נאכפים
- על שכבת **בסיס** מותר לשנות רק `visible`, `width`, `label` (מפתחות תווית קיימים), `extra.minZoom` ו־`extra.maxZoom`.
- **אסור** לשנות צבע, פלטה, `categorized`, `filter`, `planned` או `lineDecoration*`. זה קידוד הסטטוס, והוא צריך להיות זהה בכל הפרויקטים. הבנייה נכשלת עם הודעה.
- מזהה שכבה לא מוכר או מפתח לא מוכר נדחים (קודם שגיאת כתיב נוספה בשקט).
- רשימות (`vectorRules`, `filter`, `customEntries.items`) מוחלפות בשלמותן, לא ממוזגות. שימו לב: בשכבות עם טווחי זום (rule-based), `width` לא משפיע, כי העובי בא מ־`vectorRules`.
- כמה פרויקטים יחד: האחרון בשורת הפקודה גובר, ומודפסת אזהרה על התנגשות.
- שכבות של הפרויקט עצמו חופשיות, אבל צבעים צריכים להיות טוקנים מה־palette (`@PROJ_ROAD`, `@PROJ_POI`, `@PROJ_CO`). צבע hex מקבל אזהרה.

## עדכון שכבה מהבדיקה החודשית של חצב
1. `python scripts/check_hatzav.py`: בודק מול data.gov.il אילו שכבות התעדכנו. לא מוריד ולא כותב כלום.
2. אם יש שינוי: `python scripts/check_hatzav.py --apply`, או לשכבה בודדת: `python scripts/add_layer_version.py nataz_kayam --fetch`.
   נוצר קובץ חדש כמו `nataz_kayam_2026-11.geojson` ליד הקודם, ונרשם סיכום השינוי (כמה ישויות נוספו או הוסרו).
3. `python scripts/publish.py plan layers`: השכבות החדשות עולות לדרייב לתיקיית החצב המתאימה, ואחר כך `publish.py record layer ...`.
4. `python scripts/make_base.py v4`: הבסיס החדש לוקח את הגרסה החדשה של כל שכבה. יומן השינויים נכתב אוטומטית.
5. `python scripts/build_base.py v4` ופרסום. אחר כך אסף מחליט אילו פרויקטים לשדרג.

שכבה מקובץ ידני (shapefile zip או GeoJSON): `python scripts/add_layer_version.py <id> --file path.zip`.
הוספת שכבה חדשה לבסיס: `make_base.py v4 --add tma42_roads`. הסרה: `--remove <id>`. הצמדה לגרסה ישנה: `--pin nataz_kayam=2026-10`.

## שדרוג פרויקט לבסיס חדש
1. `python scripts/upgrade_project.py har-hotzvim v4`
   - ה־`project.json` הקודם נשמר ב־`projects/har-hotzvim/history/`.
   - `project_version` עולה (מ־p1 ל־p2), ושכבות הפרויקט ושינויי העיצוב שלו נשארים כמו שהם.
   - נבנה קובץ חדש: `dist/har-hotzvim_p2__base_v4.geolibre`. הקובץ הקודם לא נמחק.
2. העלאה לדרייב כקובץ חדש. אם משהו לא נראה טוב, חוזרים לקובץ הקודם בדרייב.

## פרויקט חדש
`python scripts/new_project.py tlv-north "צפון תל אביב" --center 34.80,32.11 --zoom 14 --bbox 34.76,32.08,34.84,32.14`
נוצרת התיקייה `projects/tlv-north/`. שמים בה שכבות ב־`layers/<id>_<YYYY-MM>.geojson` ומוסיפים אותן לרשימה `layers` בקובץ `project.json` (באותו מבנה כמו בהר החוצבים). בונים עם `python scripts/build_project.py tlv-north`. הסוכן פותח לפרויקט תיקייה בדרייב תחת חצב/פרויקטים.

## פרסום
`python scripts/publish.py plan base v4` (או `plan project <slug>`, `plan showcase`, `plan layers`) מדפיס בדיוק מה עולה ולאן. את ההעלאה עצמה עושה הסוכן דרך החיבורים לדרייב ולגיטהאב, כי אין על המחשב סיסמאות. אחרי ההעלאה, `publish.py record ...` רושם את מזהה הקובץ במניפסט.
- דרייב: תמיד קובץ חדש עם שם מגורסה. לא מעבירים לסל ולא דורסים.
- גיטהאב: `python scripts/build_project.py --showcase` ואחר כך עדכון `mobility-sense-base.geolibre.json`, וגם `toolkit/` (`python scripts/export_toolkit.py`).

## מגבלות
- ב־GeoLibre אין קו מקווקו אמיתי. מתוכנן = ריבועים לבנים שחותכים את הקו, ובמקומות שבהם קווים חוצים הם חותכים גם את הקו שמתחת. המקרא לא מראה מקווקו או קו חלול, ולכן הסטטוס כתוב בכותרות.
- המקטע "איך לקרוא את הקווים" (`custom:status`) לא מופיע בראש המקרא ב־web (נבדק ברינדור). GeoLibre Desktop והדפסה לא נבדקו.
- בעותק לרשת, שכבה עם `filter` מחזיקה רק את הישויות שעוברות את המסנן, וזה מה שמשאיר אותו מתחת ל־3.3MB למרות השכבות הנגזרות.
- העותק לרשת מוחלק בערך 5 מטרים, עם 5 ספרות אחרי הנקודה ופחות שדות בחלונות המידע. בשכבות אופניים ונת"צ מתוכננים מקטעים עם תכונות זהות מאוחדים. לעבודה מדויקת משתמשים בקובץ המלא מהדרייב.
- תמ"א 42 (כבישים, 2020) רשומה כמועמדת ולא נכנסת לבסיס עד שמאשרים.
- כביש 22 (ירושלים) נלקח מ־OpenStreetMap, ענף 4 בו חלקי. אין לו שכבה רשמית.

תלויות: `pip install -r requirements.txt` (shapely, geopandas, pyproj). על המחשב: `/workspace/.gisvenv/bin/python`.
