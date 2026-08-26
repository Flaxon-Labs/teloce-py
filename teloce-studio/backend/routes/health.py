"""Health and capability endpoints."""


def register_health(app):
    @app.get("/api/health")
    async def health():
        return {"ok": True, "service": "teloce-studio", "capabilities": ["vel-editor", "flaxon-generation", "pwa"]}
