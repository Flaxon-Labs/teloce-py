"""Workspace asset import and management routes."""


def register_assets(app):
    @app.get("/api/assets")
    async def assets(request):
        return {"ok": True, "assets": [], "message": "Asset import is reserved for the workspace implementation."}
