# Lesson 18: Build the Teloce Motion Lab showcase

The companion project [Teloce Motion Lab](https://teloce-showcase.vercel.app/) is a small, real Flask application that uses multiple `.vel` files, a generated router, scoped CSS, lifecycle hooks, and Three.js. Its source repository is [aldanedev-create/teloce-showcase](https://github.com/aldanedev-create/teloce-showcase).

The website proves a useful point: Teloce-Py is not limited to forms or static pages. A Python server can host a polished interactive experience while `.vel` components own the browser presentation and behavior.

## What the showcase proves

- Flask can remain the server entry point.
- Multiple `.vel` components can be compiled into browser modules.
- A Python route table can generate a client-side router.
- One HTML shell can mount the active route.
- Three.js can be imported and controlled from a `.vel` lifecycle.
- Scoped CSS can create separate visual systems for each page.
- `beforeUnmount` can stop animation frames, remove resize listeners, and dispose GPU resources.
- The same generated static-asset model is suitable for Vercel and other Python hosts.

## Copy-paste a minimal version

Create this structure:

```text
motion-demo/
├── app.py
├── build.py
├── templates/index.html
└── static/js/App.vel
```

`app.py`:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, template_folder=str(ROOT / 'templates'))

@app.get('/')
def home():
    return render_template('index.html', title='Motion demo')

if __name__ == '__main__':
    build_project(ROOT, options={'dev': True, 'source_maps': True})
    app.run(host='127.0.0.1', port=5000, debug=True)
```

`templates/index.html`:

```html
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{{ title }}</title></head>
  <body>
    <div id="app"></div>
    <script type="module">
      import { mount } from '/static/js/App.js'
      mount(document.querySelector('#app'))
    </script>
  </body>
</html>
```

`static/js/App.vel`:

```html
<script>
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js'

export default {
  data() { return { frame: 0 } },
  mounted() {
    const host = document.querySelector('#scene')
    this.scene = new THREE.Scene()
    this.camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, .1, 100)
    this.camera.position.z = 3
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    this.renderer.setSize(host.clientWidth, host.clientHeight)
    host.appendChild(this.renderer.domElement)
    this.mesh = new THREE.Mesh(new THREE.TorusKnotGeometry(.7, .2, 80, 12), new THREE.MeshStandardMaterial({ color: '#9b86ff' }))
    this.scene.add(this.mesh)
    this.scene.add(new THREE.AmbientLight('#ffffff', 1.5))
    this.animate = () => { this.frame = requestAnimationFrame(this.animate); this.mesh.rotation.y += .01; this.renderer.render(this.scene, this.camera) }
    this.animate()
  },
  beforeUnmount() { cancelAnimationFrame(this.frame); this.renderer?.dispose() }
}
</script>

<template><main><h1>Teloce Motion</h1><div id="scene"></div></main></template>

<style scoped>
main { min-height: 100vh; display: grid; place-items: center; background: #080b18; color: white; font-family: system-ui, sans-serif; }
#scene { width: min(80vw, 48rem); height: 28rem; }
</style>
```

Run it:

```bash
python -m pip install Flask teloce-py
python app.py
```

## Add a router and more pages

For the full showcase, `build.py` compiles the components and generates a router that imports `HomePage`, `TutorialPage`, and `PlaygroundPage`. The HTML shell mounts the router like this:

```html
<div id="app"></div>
<script type="module">
  import router from '/static/js/router.js'
  router.mount(document.querySelector('#app'))
</script>
```

Use hash routes for a simple serverless deployment:

```python
routes = [
    {'path': '/', 'component': 'HomePage'},
    {'path': '/tutorial', 'component': 'TutorialPage'},
    {'path': '/playground', 'component': 'PlaygroundPage'},
]
```

## Deploy the pattern

Keep `app.py` at the repository root, declare `Flask` and `teloce-py` in `requirements.txt`, and run `python build.py` as the Vercel build step. The showcase uses the same pattern. See the project's [README](https://github.com/aldanedev-create/teloce-showcase/blob/main/README.md) for local and Vercel commands.

For production Three.js work, pin the CDN version or bundle it, add a WebGL fallback, pause when the document is hidden, respect reduced-motion preferences, and dispose every resource during unmount.
