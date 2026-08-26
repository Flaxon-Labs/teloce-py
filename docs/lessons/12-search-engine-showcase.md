# Lesson 12: Build a small search engine with `.vel`

PySeek is a real reference application built with imported `.vel` files, Flaxon routes, a crawler, PostgreSQL full-text search, IndexedDB history, and Vercel deployment. It proves that `.vel` can power a data-heavy tool, not only a landing page.

## What it proves

- `.vel` imports scale into a component tree;
- Python owns crawling, ranking, storage, APIs, and background work;
- the browser layer handles forms, loading, empty states, loops, history, and responsive UI;
- SQLite can be used locally while Neon PostgreSQL provides production persistence;
- serverless functions can serve the UI and short bounded crawl jobs, but not replace a long-running crawler;
- browser tests are required because a successful compiler build cannot prove events, loops, caches, or API behavior.

## Architecture

```text
App.vel -> SearchShell.vel -> Header, SearchBar, SearchResults -> ResultCard
                         -> SearchHistory, CrawlStatus
Flaxon /api/search -> ranking service -> SQLite or Neon
Flaxon /api/cron/crawl -> robots-aware crawler -> index
```

## Copy-paste mini showcase

`static/js/SearchBox.vel`:

```html
<template>
  <form @submit="submit">
    <input v-model="localQuery" aria-label="Search" placeholder="Search" />
    <button>Search</button>
  </form>
</template>
<script>
export default {
  data() { return { localQuery: '' } },
  methods: { submit(event) { event.preventDefault(); this.$emit('search', this.localQuery) } }
}
</script>
```

`static/js/App.vel`:

```html
<script>
import SearchBox from './SearchBox.vel'
export default { data() { return { query: '', result: null, error: '' } }, methods: {
  async search(value) {
    this.query = value.trim(); this.error = ''; this.result = null
    if (!this.query) return
    const response = await fetch('/api/search?q=' + encodeURIComponent(this.query))
    const data = await response.json()
    if (!response.ok || !data.ok) { this.error = data.error || 'Search failed'; return }
    this.result = data.results[0] || null
  }
} }
</script>
<template>
  <main><h1>Mini PySeek</h1><SearchBox @search="search" />
    <p v-if="error">{{ error }}</p>
    <p v-if="query && !result && !error">No result for {{ query }}</p>
    <article v-if="result"><a :href="result.url">{{ result.title }}</a><p v-html="result.snippet"></p></article>
  </main>
</template>
```

`app.py`:

```python
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, template_folder=str(ROOT / 'templates'))

@app.get('/')
def home(): return render_template('index.html', title='Mini PySeek')

@app.get('/api/search')
def search():
    query = request.args.get('q', '').strip().lower()
    pages = [{'title': 'Python', 'url': 'https://python.org', 'snippet': 'Python documentation'}]
    results = [p for p in pages if query and query in (p['title'] + ' ' + p['snippet']).lower()]
    return jsonify(ok=True, query=query, results=results, total=len(results))

if __name__ == '__main__':
    build_project(ROOT, options={'dev': True, 'source_maps': True})
    app.run(debug=True, port=5000)
```

`templates/index.html`:

```html
<!doctype html><html><head><meta charset="utf-8"><title>{{ title }}</title></head>
<body><div id="app"></div><script type="module">import { mount } from '/static/js/App.js'; mount('#app')</script></body></html>
```

Run it:

```bash
pip install teloce-py Flask
python app.py
```

This is a learning index. A production version needs normalized URLs, robots.txt checks, crawl limits, retries, ranking, rate limits, observability, a real database, and browser end-to-end tests. Study the complete PySeek project for those pieces.

## Exercises

1. Split the result card into another imported `.vel` file.
2. Store history in IndexedDB.
3. Replace the list with Neon PostgreSQL full-text search.
4. Add loading and empty states and test them with Playwright.
5. Deploy to Vercel and test `/api/health`, `/api/stats`, and `/api/search` independently before testing the UI.
