from pathlib import Path

from flask import Flask, jsonify, render_template, request

from teloce.build import build_project


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

# Editable-mode workflow: the checked-out Teloce compiler builds the app.
# Always rebuild this diagnostic example from the editable compiler. The build
# manifest tracks source files, but not compiler implementation changes; a
# clean build prevents an old generated runtime from masking compiler fixes.
build_project(ROOT, out_dir=DIST, options={"dev": True, "clean": True, "source_maps": True})

app = Flask(
    __name__,
    static_folder=str(DIST / "static"),
    template_folder=str(ROOT / "templates"),
)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

photos = [
    {"id": 1, "title": "Quiet morning", "category": "Nature", "image": "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=80", "likes": 24},
    {"id": 2, "title": "City geometry", "category": "Urban", "image": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=900&q=80", "likes": 18},
    {"id": 3, "title": "Blue horizon", "category": "Travel", "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80", "likes": 31},
    {"id": 4, "title": "Warm studio", "category": "Design", "image": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80", "likes": 12},
]

@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/photos")
def list_photos():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "All")
    result = [
        photo for photo in photos
        if (not query or query in photo["title"].lower() or query in photo["category"].lower())
        and (category == "All" or photo["category"] == category)
    ]
    return jsonify({"photos": result})


@app.post("/api/photos/<int:photo_id>/like")
def like_photo(photo_id: int):
    photo = next((item for item in photos if item["id"] == photo_id), None)
    if photo is None:
        return jsonify({"error": "Photo not found"}), 404
    photo["likes"] += 1
    return jsonify({"id": photo_id, "likes": photo["likes"]})


if __name__ == "__main__":
    # The compiler writes generated assets while Flask is starting.  The
    # watchdog reloader sees those writes and can restart the process during
    # a browser load, leaving the gallery on its boot screen.  Keep debug
    # exceptions enabled without allowing the reloader to interrupt the app.
    app.run(host="127.0.0.1", port=5050, debug=True, use_reloader=False)
