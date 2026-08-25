# Lesson 7: Django, admin, and imported .vel components

Django owns models, migrations, authentication, permissions, CSRF, URLs, and the real /admin/ system. Teloce owns the browser UI compiled from .vel files.

## Setup

    pip install django teloce-py
    django-admin startproject portal .
    python manage.py startapp content

Add content to INSTALLED_APPS, configure STATIC_URL and STATICFILES_DIRS, and create static/js/components and templates.

## Model and admin

    # content/models.py
    from django.db import models
    class Page(models.Model):
        slug = models.SlugField(unique=True)
        title = models.CharField(max_length=160)
        body = models.TextField()
        published = models.BooleanField(default=False)
        updated_at = models.DateTimeField(auto_now=True)

    # content/admin.py
    from django.contrib import admin
    from .models import Page
    @admin.register(Page)
    class PageAdmin(admin.ModelAdmin):
        list_display = ("title", "slug", "published", "updated_at")
        list_filter = ("published",)
        search_fields = ("title", "slug", "body")

Run python manage.py makemigrations, migrate, and createsuperuser. The admin is at /admin/. Never put credentials or privileged operations in a .vel file.

## Import another .vel

static/js/components/PageCard.vel:

    <template><article><h2>{{ page.title }}</h2><p>{{ page.body }}</p><button @click="$emit('select', page)">Edit</button></article></template>
    <script>export default { props: { page: Object }, emits: ["select"] };</script>

static/js/App.vel imports and registers it:

    <template>
      <main><h1>Content portal</h1><p v-if="error">{{ error }}</p>
        <PageCard v-for="page in pages" :key="page.id" :page="page" @select="edit" />
        <form v-if="selected" @submit.prevent="save"><input v-model="selected.title" /><textarea v-model="selected.body"></textarea><button>Save</button></form>
      </main>
    </template>
    <script>
    import PageCard from "./components/PageCard.vel";
    export default { components: { PageCard }, data() { return { pages: [], selected: null, error: "" }; }, methods: {
      async load() { this.pages = await fetch("/api/pages").then(r => r.json()); },
      edit(page) { this.selected = { ...page }; },
      async save() { await fetch("/api/pages/" + this.selected.slug, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(this.selected) }); await this.load(); }
    }, mounted() { this.load(); } };
    </script>

The relative import is resolved by Teloce's dependency graph. The original <for>, <if>, and @click API remains compatible with v-for, v-if, and @click aliases.

## Django endpoint and mount

    def pages(request):
        return JsonResponse(list(Page.objects.filter(published=True).values()), safe=False)

    @require_http_methods(["PUT"])
    def update_page(request, slug):
        page = get_object_or_404(Page, slug=slug)
        data = json.loads(request.body or "{}")
        page.title, page.body = str(data.get("title", page.title)), str(data.get("body", page.body))
        page.save(update_fields=["title", "body", "updated_at"])
        return JsonResponse({"id": page.id, "slug": page.slug, "title": page.title, "body": page.body})

Add routes for /, /api/pages, /api/pages/<slug>, and /admin/. Use Django CSRF tokens for browser writes.

    {% load static %}<div id="app"></div>
    <script type="module">import { mount } from "{% static 'js/App.js' %}"; mount("#app");</script>

Build with teloce check . and teloce build . --out-dir dist, then run python manage.py runserver. In production use collectstatic, a production WSGI/ASGI server, and protected admin authorization.
