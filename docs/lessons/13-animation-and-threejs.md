# Lesson 13: CSS animation and Three.js in `.vel`

`.vel` files can own the complete browser feature: template, reactive state, JavaScript lifecycle, and component CSS. This lesson gives two copy-paste showcases.

## Showcase A: animated CSS component

Create `static/js/App.vel`:

```html
<template>
  <main class="animation-demo">
    <p class="eyebrow">Teloce-Py animation showcase</p>
    <h1>CSS animation inside a `.vel` file</h1>
    <button class="orb-button" @click="toggle">
      <span class="orb" :class="{ paused: !running }"></span>
      {{ running ? 'Pause animation' : 'Play animation' }}
    </button>
    <div class="bars" aria-label="Animated loading indicator">
      <i v-for="bar in bars" :key="bar" :style="{ animationDelay: bar * 0.08 + 's' }"></i>
    </div>
  </main>
</template>

<script>
export default {
  data() { return { running: true, bars: [1, 2, 3, 4, 5, 6] } },
  methods: { toggle() { this.running = !this.running } }
}
</script>

<style scoped>
.animation-demo { min-height: 100vh; display: grid; place-items: center; align-content: center; gap: 1.25rem; background: #0a1020; color: #eef2ff; font-family: system-ui, sans-serif; text-align: center; }
.eyebrow { color: #8dded0; letter-spacing: .16em; text-transform: uppercase; font-size: .72rem; }
.orb-button { border: 1px solid #53618b; border-radius: 999px; padding: .8rem 1.2rem; display: inline-flex; align-items: center; gap: .7rem; background: #151e38; color: inherit; cursor: pointer; }
.orb { width: 1rem; height: 1rem; border-radius: 50%; background: #8dded0; box-shadow: 0 0 1.4rem #8dded0; animation: pulse 1.2s ease-in-out infinite; }
.orb.paused { animation-play-state: paused; opacity: .45; }
.bars { height: 4rem; display: flex; align-items: end; gap: .35rem; }
.bars i { width: .5rem; height: 1rem; border-radius: .4rem; background: #b79cff; animation: bounce .9s ease-in-out infinite alternate; }
@keyframes pulse { 50% { transform: scale(1.5); opacity: .55; } }
@keyframes bounce { to { height: 3.5rem; background: #8dded0; } }
@media (prefers-reduced-motion: reduce) { .orb, .bars i { animation: none; } }
</style>
```

The `<style scoped>` block belongs to this component. Teloce scopes its selectors so `.orb` and `.bars` do not accidentally style another component. `@keyframes` remains available to the scoped rules. The `prefers-reduced-motion` rule is important for accessibility.

## Showcase B: Three.js scene in `.vel`

This example loads Three.js as a browser ES module from a CDN. For production, pin the version or install/bundle Three.js in your frontend build instead of relying on an unpinned URL.

Create `static/js/App.vel`:

```html
<script>
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.171.0/build/three.module.js'

export default {
  data() { return { rotating: true, frame: 0 } },
  mounted() {
    const host = document.getElementById('three-scene')
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color('#0b1020')
    this.camera = new THREE.PerspectiveCamera(45, host.clientWidth / host.clientHeight, 0.1, 100)
    this.camera.position.z = 3
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.setSize(host.clientWidth, host.clientHeight)
    host.appendChild(this.renderer.domElement)

    this.mesh = new THREE.Mesh(
      new THREE.TorusKnotGeometry(.72, .22, 96, 16),
      new THREE.MeshStandardMaterial({ color: '#a98cff', metalness: .35, roughness: .22 })
    )
    this.scene.add(this.mesh)
    this.scene.add(new THREE.AmbientLight('#b8c7ff', 1.4))
    const light = new THREE.PointLight('#69e2d0', 18, 10)
    light.position.set(2, 2, 3)
    this.scene.add(light)
    this.resize = () => { this.camera.aspect = host.clientWidth / host.clientHeight; this.camera.updateProjectionMatrix(); this.renderer.setSize(host.clientWidth, host.clientHeight) }
    window.addEventListener('resize', this.resize)
    this.animate = () => { this.frame = requestAnimationFrame(this.animate); if (this.rotating) { this.mesh.rotation.x += .006; this.mesh.rotation.y += .009 }; this.renderer.render(this.scene, this.camera) }
    this.animate()
  },
  beforeUnmount() {
    cancelAnimationFrame(this.frame)
    window.removeEventListener('resize', this.resize)
    this.mesh?.geometry.dispose(); this.mesh?.material.dispose(); this.renderer?.dispose()
  },
  methods: { toggle() { this.rotating = !this.rotating } }
}
</script>

<template>
  <main class="three-demo">
    <div id="three-scene" class="scene" aria-label="Interactive Three.js scene"></div>
    <button @click="toggle">{{ rotating ? 'Pause rotation' : 'Resume rotation' }}</button>
  </main>
</template>

<style scoped>
.three-demo { min-height: 100vh; display: grid; place-items: center; background: #070b16; padding: 2rem; }
.scene { width: min(80vw, 52rem); height: min(65vh, 34rem); min-height: 20rem; overflow: hidden; border: 1px solid #344264; border-radius: 1.25rem; box-shadow: 0 1rem 4rem #02040b; }
button { margin-top: -5rem; z-index: 1; border: 1px solid #6b72a4; border-radius: 999px; padding: .7rem 1rem; background: #171d35; color: white; cursor: pointer; }
</style>
```

The `.vel` lifecycle creates the scene after the host element exists, starts an animation loop, responds to resize, and disposes GPU resources in `beforeUnmount`. The Python framework only serves the page; Three.js runs in the browser.

## Host either example with Python

Use the same `app.py` pattern as the getting-started guide:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, template_folder=str(ROOT / 'templates'))

@app.get('/')
def home(): return render_template('index.html')

if __name__ == '__main__':
    build_project(ROOT, options={'dev': True, 'source_maps': True})
    app.run(debug=True, port=5000)
```

`templates/index.html`:

```html
<main id="app"></main>
<script type="module">import { mount } from '/static/js/App.js'; mount('#app')</script>
```

Run `python app.py`, then open `http://127.0.0.1:5000`.

## Production notes

- Pin the Three.js version and prefer a bundled dependency for reproducible builds.
- Test WebGL availability and show a useful fallback when WebGL is unavailable.
- Cap pixel ratio and dispose geometries, materials, textures, and renderers.
- Pause animation when the tab is hidden and respect reduced-motion preferences.
- Keep secrets and server-side data in Python; never put them in a browser component.
