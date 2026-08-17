# מחשבון מרחק נסיעה — PWA

אפליקציה פשוטה: כתובת מוצא קבועה + כתובת יעד → מרחק נסיעה בק"מ (דרך Google Distance Matrix API).

## מבנה הפרויקט

```
distance-app/
├── app.py                  # שרת Flask + endpoint /api/distance
├── requirements.txt
├── .env.example            # להעתיק ל-.env ולמלא מפתח API
└── static/
    ├── index.html           # הממשק (PWA)
    ├── manifest.json
    ├── service-worker.js
    └── icons/
```

## הרצה מקומית

```bash
cd distance-app
python3 -m venv venv
source venv/bin/activate        # ב-Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# פתחו את .env והדביקו את GOOGLE_MAPS_API_KEY

export $(cat .env | xargs)      # טוען את משתני הסביבה (Linux/Mac)
python app.py
```

האתר יעלה על `http://localhost:5000`.

## מה שנשאר לעשות — המפתח בלבד

הכל בנוי ומוכן. הדבר היחיד שחסר כדי שהחישוב יעבוד בפועל:

1. ליצור מפתח API ב-Google Cloud Console (Distance Matrix API מופעל)
2. להכניס אותו למשתנה `GOOGLE_MAPS_API_KEY` בשרת (בקובץ `.env` מקומית, או במשתני הסביבה של שירות האחסון בענן)

בלי מפתח, השרת עולה ורץ כרגיל, אבל `/api/distance` יחזיר הודעה ברורה שהשרת עדיין לא מוגדר (קוד 503) — לא קריסה.

## פריסה לשרת (דוגמה כללית)

כל שירות שתומך ב-Python + משתני סביבה יעבוד (Render, Railway, PythonAnywhere, VPS עם gunicorn וכו'). הרצה בפרודקשן:

```bash
gunicorn -w 2 -b 0.0.0.0:$PORT app:app
```

חשוב להגדיר את `GOOGLE_MAPS_API_KEY` כמשתנה סביבה בהגדרות השירות — לא לשים אותו בקוד ולא להעלות את `.env` ל-git.

## התקנה כ-PWA

לאחר שהאתר עולה בדפדפן (בנייד או בדסקטופ), אפשר "להוסיף למסך הבית" / "התקן אפליקציה" — ה-`manifest.json` וה-`service-worker.js` כבר מוכנים לכך.
