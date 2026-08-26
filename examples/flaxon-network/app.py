import mimetypes
from pathlib import Path
from flaxon import Flaxon
from flaxon.http.response import Response
from flaxon.jinax import Jinax

ROOT = Path(__file__).resolve().parent
DIST = (ROOT / "dist").resolve()
app = Flaxon("teloce-network", debug=True)
app.use_templates(Jinax(str(ROOT / "templates"), auto_reload=True))
devices = [{"name": "gateway", "address": "192.0.2.1", "status": "online"}, {"name": "worker-01", "address": "192.0.2.20", "status": "online"}]


def register_assets() -> None:
    """Expose only generated files below dist as browser assets."""
    if not DIST.exists():
        return
    for path in DIST.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(DIST).as_posix()
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"

        async def serve_asset(request, file_path=path, content_type=media_type):
            return Response(file_path.read_bytes(), media_type=content_type)

        app.get(f"/assets/{relative}")(serve_asset)


register_assets()

@app.get("/")
async def home(request):
    return await request.render("index.html", {})

@app.get("/api/devices")
async def list_devices():
    return {"devices": devices}

@app.post("/api/devices/<name>/check")
async def check_device(name: str):
    for device in devices:
        if device["name"] == name:
            return {"name": name, "status": device["status"], "checked": True}
    return {"name": name, "status": "unknown", "checked": False}

@app.websocket("/ws/events/<room_id>")
async def events(socket, room_id: str):
    await socket.accept()
    await socket.join(room_id)
    await socket.broadcast_json(room_id, {"type": "dashboard-connected", "room": room_id})
