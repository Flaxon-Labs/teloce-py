# Lesson 8: FastAPI CMS with imported .vel components

FastAPI owns the async API and Teloce owns the browser CMS. A .vel import is a frontend dependency, not a Python import.

## App.vel and component import

static/js/components/PageCard.vel:

    <template><button @click="$emit('select', page)"><strong>{{ page.title }}</strong><small>{{ page.slug }}</small></button></template>
    <script>export default { props: { page: Object }, emits: ["select"] };</script>

static/js/App.vel:

    <template>
      <main><h1>FastAPI CMS</h1><p v-if="error">{{ error }}</p>
        <PageCard v-for="page in pages" :key="page.slug" :page="page" @select="select" />
        <section v-if="selected"><input v-model="selected.title" /><textarea v-model="selected.body"></textarea><button @click="save">Save</button><span v-if="saved">Saved</span></section>
      </main>
    </template>
    <script>
    import PageCard from "./components/PageCard.vel";
    export default { components: { PageCard }, data() { return { pages: [], selected: null, saved: false, error: "" }; },
      mounted() { this.load(); }, methods: {
        async load() { this.pages = await fetch("/api/pages").then(r => r.json()); },
        select(page) { this.selected = { ...page }; this.saved = false; },
        async save() { const response = await fetch("/api/pages/" + this.selected.slug, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(this.selected) }); if (!response.ok) throw new Error("Save failed"); this.selected = await response.json(); this.saved = true; }
      }
    };
    </script>

The builder follows the relative import and emits the imported component. Do not use a server filesystem path in a browser import.

## FastAPI host

    from pathlib import Path
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from starlette.requests import Request

    ROOT = Path(__file__).parent
    app = FastAPI(title="Teloce CMS")
    pages = {"home": {"slug": "home", "title": "Welcome", "body": "Edit me."}}
    app.mount("/static", StaticFiles(directory=ROOT / "dist" / "static"), name="static")
    templates = Jinja2Templates(directory=ROOT / "templates")

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/pages")
    async def list_pages():
        return list(pages.values())

    @app.put("/api/pages/{slug}")
    async def update_page(slug: str, payload: dict):
        if slug not in pages:
            raise HTTPException(404, "Page not found")
        pages[slug].update(title=str(payload.get("title", "")), body=str(payload.get("body", "")))
        return pages[slug]

templates/index.html:

    <div id="app"></div>
    <script type="module">import { mount } from "{{ url_for('static', path='js/App.js') }}"; mount("#app");</script>

Run `pip install fastapi uvicorn jinja2 teloce-py`, then `teloce doctor --verbose`, `teloce lint --strict`, `teloce build --out-dir dist`, and `uvicorn app:app --reload`. In production validate bodies with Pydantic, authenticate CMS writes, configure CORS deliberately, and deploy behind a managed ASGI server.
