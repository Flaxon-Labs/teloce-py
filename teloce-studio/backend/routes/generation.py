"""Code-generation and generated-file inspection routes."""

from flaxon.http.request import Request
from flaxon.http.response import Response
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from backend.services.generation_service import generate_project
from backend.services.project_service import get_project


def register_generation(app):
    @app.post("/api/projects/<project_id>/generate")
    async def generate(request: Request, project_id: str):
        try:
            return generate_project(get_project(project_id))
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}

    @app.get("/api/projects/<project_id>/export")
    async def export_project(request: Request, project_id: str):
        try:
            model = get_project(project_id)
            generate_project(model)
            from backend.services.project_service import _project_dir
            root = _project_dir(project_id)
            stream = BytesIO()
            with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
                for path in sorted(root.rglob("*")):
                    if path.is_file(): archive.write(path, path.relative_to(root).as_posix())
            return Response(stream.getvalue(), headers={"content-disposition": f"attachment; filename={project_id}.zip"}, media_type="application/zip")
        except FileNotFoundError:
            return {"ok": False, "error": "Project not found"}
