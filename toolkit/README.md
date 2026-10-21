# Mobility Sense – ערכת מפת הבסיס ב־GeoLibre

הערכה מנהלת מפת בסיס אחת לכל הפרויקטים, עם גרסאות לעיצוב, לשכבות ולבסיס עצמו. שום קובץ לא נדרס: כל שינוי יוצר גרסה חדשה, והגרסה הקודמת נשארת.

## שלושה דברים, לכל אחד גרסה משלו

| מה | איפה | גרסה |
|---|---|---|
| **עיצוב**: צבעים, עוביים, קיים מול מתוכנן, תוויות, מקרא, קבוצות | `style/style.json` (עותק עבודה), `style/versions/style_s1.json` (קפוא) | `s1`, `s2`, ... |
| **שכבות**: כל שכבה עם מקור, תאריך, גודל ומיקום אחסון | `layers/layers.json` + `data/layers/<id>/<id>_<YYYY-MM>.geojson` | `2026-10`, `2026-11`, ... |
| **בסיס** = עיצוב + גרסה מוצמדת לכל שכבה | `base/v3/manifest.json`, יומן ב־`base/CHANGELOG.md` | `v3`, `v4`, ... |
| **פרויקט** = בסיס מוצמד + שכבות הפרויקט + סימנייה + שינויי עיצוב מקומיים | `projects/<slug>/project.json` | `p1`, `p2`, ... |

**אחסון:** שכבה עד 512KB נכנסת גם לגיטהאב (`toolkit/`). שכבות כבדות (נת"צ, שבילי אופניים, אופנידן, מסילות) נמצאות רק בדרייב, בתיקיות חצב, ומזהה הקובץ שלהן רשום ב־`layers.json`. הקובץ המלא של כל בסיס או פרויקט (בערך 25MB) עולה לדרייב כקובץ חדש עם שם מגורסה. העותק הקל לרשת (פחות מ־3.3MB) עולה לגיטהאב.

**קישור הלחיצה האחת** מציג את הבסיס יחד עם הפרויקטים הפעילים (ההגדרה ב־`publish/web_root.json`). שם הקובץ בגיטהאב קבוע (`mobility-sense-base.geolibre.json`), ולכן הקישור לא משתנה.

## שינוי עיצוב
1. עורכים את `style/style.json`, למשל צבע ב־`palette` או עובי קו ב־`layers.<id>.width`, ומעלים את `style_version` (מ־s1 ל־s2).
2. `python scripts/release_style.py`: מקפיא את s2.
3. `python scripts/make_base.py v4 --note "עיצוב חדש"`: בסיס חדש עם העיצוב החדש ואותן שכבות. נרשם ביומן.
4. `python scripts/build_base.py v4`, ואחר כך העלאה (ראו "פרסום").
5. הפרויקטים נשארים על הבסיס הקודם עד שמשדרגים אותם (ראו למטה).

שינוי עיצוב שנוגע רק לפרויקט אחד לא נכנס לבסיס: כותבים אותו ב־`style_overrides` שבקובץ `project.json` של הפרויקט.

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
- ב־GeoLibre אין קו מקווקו. מתוכנן מסומן בגוון בהיר עם עיגולים לאורך הקו.
- העותק לרשת מוחלק בערך 5 מטרים, עם 5 ספרות אחרי הנקודה ופחות שדות בחלונות המידע. בשכבות אופניים ונת"צ מתוכננים מקטעים עם תכונות זהות מאוחדים. לעבודה מדויקת משתמשים בקובץ המלא מהדרייב.
- תמ"א 42 (כבישים, 2020) רשומה כמועמדת ולא נכנסת לבסיס עד שמאשרים.
- כביש 22 (ירושלים) נלקח מ־OpenStreetMap, ענף 4 בו חלקי. אין לו שכבה רשמית.

תלויות: `pip install -r requirements.txt` (shapely, geopandas, pyproj). על המחשב: `/workspace/.gisvenv/bin/python`.
