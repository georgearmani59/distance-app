import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")

GOOGLE_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")


# ---------- Serve the PWA ----------

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.static_folder, "manifest.json")


@app.route("/service-worker.js")
def service_worker():
    # Must be served from root scope for the PWA to control the whole app
    return send_from_directory(app.static_folder, "service-worker.js")


# ---------- API ----------

@app.route("/api/distance", methods=["POST"])
def get_distance():
    if not GOOGLE_API_KEY:
        return jsonify({"error": "השרת עדיין לא הוגדר עם מפתח Google Maps API"}), 503

    data = request.get_json(silent=True) or {}
    origin = (data.get("origin") or "").strip()
    destination = (data.get("destination") or "").strip()

    if not origin or not destination:
        return jsonify({"error": "חסרה כתובת מוצא או יעד"}), 400

    try:
        res = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={
                "origins": origin,
                "destinations": destination,
                "units": "metric",
                "key": GOOGLE_API_KEY,
            },
            timeout=10,
        )
        res.raise_for_status()
    except requests.RequestException:
        return jsonify({"error": "שגיאת תקשורת מול Google Maps"}), 502

    result = res.json()

    if result.get("status") != "OK":
        return jsonify({"error": f"Google Maps החזיר שגיאה: {result.get('status')}"}), 502

    try:
        element = result["rows"][0]["elements"][0]
    except (KeyError, IndexError):
        return jsonify({"error": "תשובה לא תקינה מ-Google Maps"}), 502

    if element.get("status") != "OK":
        return jsonify({"error": "לא נמצא מסלול נסיעה בין הכתובות"}), 404

    km = element["distance"]["value"] / 1000
    return jsonify({
        "km": round(km, 1),
        "duration": element["duration"]["text"],
        "origin_resolved": result["origin_addresses"][0],
        "destination_resolved": result["destination_addresses"][0],
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "api_key_configured": bool(GOOGLE_API_KEY)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
