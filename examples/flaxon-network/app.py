from pathlib import Path
from flaxon import Flaxon
from flaxon.jinax import Jinax

ROOT = Path(__file__).parent
app = Flaxon("teloce-network", debug=True)
app.use_templates(Jinax(str(ROOT / "templates"), auto_reload=True))
devices = [{"name": "gateway", "address": "192.0.2.1", "status": "online"}, {"name": "worker-01", "address": "192.0.2.20", "status": "online"}]

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
