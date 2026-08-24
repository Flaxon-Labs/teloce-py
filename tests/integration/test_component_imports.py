"""Production-style nested `.vel` component build tests."""

import subprocess
import tempfile
from pathlib import Path

from teloce.build.builder import Builder
from teloce.build.bundler import BundleError, ModuleBundler


PARENT = '''
<template><section><Child /></section></template>
<script>
import Child from "./components/Child.vel";
export default { name: "Parent", components: { Child } };
</script>
'''

CHILD = '''
<template><article class="child">{{ message }}</article></template>
<script>export default { data() { return { message: "Loaded child" }; } };</script>
<style scoped>.child { color: purple; }</style>
'''


def test_nested_vel_components_are_resolved_and_mounted():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parent = root / "static" / "js" / "App.vel"
        child = root / "static" / "js" / "components" / "Child.vel"
        child.parent.mkdir(parents=True)
        parent.write_text(PARENT, encoding="utf-8")
        child.write_text(CHILD, encoding="utf-8")

        result = Builder({"dev": True}).build(root)
        assert result["failed"] == 0, result["errors"]
        assert result["compiled"] == 2
        assert result["dependencies"]["static/js/App.vel"] == ["static/js/components/Child.vel"]
        manifest = (root / "dist" / "manifest.json").read_text(encoding="utf-8")
        assert "static/js/components/Child.vel" in manifest

        parent_js = root / "dist" / "static" / "js" / "App.js"
        child_js = root / "dist" / "static" / "js" / "components" / "Child.js"
        parent_code = parent_js.read_text(encoding="utf-8")
        assert 'import Child from "./components/Child.js";' in parent_code
        assert '"Child": Child' in parent_code
        assert "child.mount(element, __readProps(element, state))" in parent_code
        assert child_js.exists()

        for generated in (parent_js, child_js):
            checked = subprocess.run(["node", "--check", str(generated)], capture_output=True, text=True)
            assert checked.returncode == 0, checked.stderr


def test_missing_vel_component_import_fails_the_build():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "static" / "js" / "App.vel"
        source.parent.mkdir(parents=True)
        source.write_text(PARENT, encoding="utf-8")

        result = Builder().build(root)
        assert result["failed"] == 1
        assert result["compiled"] == 0
        assert "Component import not found" in result["errors"][0]["error"]


def test_production_build_can_clean_and_hash_assets():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "static" / "js" / "App.vel"
        source.parent.mkdir(parents=True)
        source.write_text("<template><div>Release</div></template>", encoding="utf-8")
        stale = root / "dist" / "old.js"
        stale.parent.mkdir(parents=True)
        stale.write_text("stale", encoding="utf-8")

        result = Builder({"clean": True, "hash_assets": True, "minify": True}).build(root)
        assert result["failed"] == 0, result["errors"]
        assert not stale.exists()
        generated = list((root / "dist" / "static" / "js").glob("App.*.js"))
        assert len(generated) == 1
        assert generated[0].stem.startswith("App.")


def test_hash_assets_fingerprints_static_files_and_rewrites_dev_entrypoint():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "static" / "js" / "App.vel"
        source.parent.mkdir(parents=True)
        (root / "static" / "images").mkdir(parents=True)
        (root / "static" / "images" / "logo.svg").write_text("<svg/>", encoding="utf-8")
        source.write_text("<template><div>Release</div></template>", encoding="utf-8")
        (root / "templates").mkdir()
        (root / "templates" / "index.html").write_text(
            '<img src="/static/images/logo.svg"><script type="module" src="/static/js/App.js"></script>',
            encoding="utf-8",
        )

        result = Builder({"dev": True, "hash_assets": True}).build(root)
        assert result["failed"] == 0, result["errors"]
        image = next((root / "dist" / "static" / "images").glob("logo.*.svg"))
        generated = next((root / "dist" / "static" / "js").glob("App.*.js"))
        html = (root / "dist" / "index.html").read_text(encoding="utf-8")
        assert image.name in html
        assert generated.name in html
        assert result["asset_map"]["static/images/logo.svg"].endswith(image.name)


def test_build_writes_valid_source_maps_when_enabled():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "static" / "js" / "App.vel"
        source.parent.mkdir(parents=True)
        source.write_text("<template><div>Release</div></template>", encoding="utf-8")

        result = Builder({"source_maps": True}).build(root)
        assert result["failed"] == 0, result["errors"]
        source_map = root / "dist" / "static" / "js" / "App.js.map"
        assert source_map.exists()
        assert '"version": 3' in source_map.read_text(encoding="utf-8")
        assert "sourceMappingURL=App.js.map" in (root / "dist" / "static" / "js" / "App.js").read_text(encoding="utf-8")


def test_component_props_slots_events_and_dynamic_components_compile():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parent = root / "static" / "js" / "App.vel"
        child = root / "static" / "js" / "components" / "Child.vel"
        parent.parent.mkdir(parents=True)
        child.parent.mkdir(parents=True)
        parent.write_text('''
<template>
  <Child title="Hello" :value="count" @save="onSave"><strong>Slot content</strong></Child>
  <component :is="activeComponent" />
</template>
<script>
import Child from "./components/Child.vel";
export default { data() { return { count: 1, activeComponent: "Child" }; }, methods: { onSave() {} } };
</script>
''', encoding="utf-8")
        child.write_text('''
<template><article><h2>{{ title }}</h2><slot /></article></template>
<script>
export default { props: ["title", "value"], methods: { save() { this.$emit("save", this.value); } } };
</script>
''', encoding="utf-8")

        result = Builder({"dev": True}).build(root)
        assert result["failed"] == 0, result["errors"]
        code = (root / "dist" / "static" / "js" / "App.js").read_text(encoding="utf-8")
        assert "data-teloce-is" in code
        assert "__slots" in code
        assert "teloce:${name}" in code
        checked = subprocess.run(
            ["node", "--check", str(root / "dist" / "static" / "js" / "App.js")],
            capture_output=True,
            text=True,
        )
        assert checked.returncode == 0, checked.stderr


def test_named_slots_and_child_prop_updates_are_emitted():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parent = root / "static" / "js" / "App.vel"
        child = root / "static" / "js" / "components" / "Child.vel"
        parent.parent.mkdir(parents=True)
        child.parent.mkdir(parents=True)
        parent.write_text('''<template><Child :title="title"><strong slot="heading">Heading</strong></Child></template><script>import Child from "./components/Child.vel"; export default { data() { return { title: "One" }; }, components: { Child } };</script>''', encoding="utf-8")
        child.write_text('''<template><article><slot name="heading"></slot><h1>{{ title }}</h1></article></template><script>export default { props: { title: { type: String, required: true } } };</script>''', encoding="utf-8")
        result = Builder({"dev": True}).build(root)
        assert result["failed"] == 0, result["errors"]
        code = (root / "dist" / "static" / "js" / "App.js").read_text(encoding="utf-8")
        assert "updateProps" in code
        assert "__slots" in code


def test_production_bundle_resolves_nested_components_and_is_valid_js():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parent = root / "static" / "js" / "App.vel"
        child = root / "static" / "js" / "components" / "Child.vel"
        child.parent.mkdir(parents=True)
        parent.write_text('<template><Child /></template><script>import Child from "./components/Child.vel"; export default {};</script>', encoding="utf-8")
        child.write_text('<template><p>Bundled</p></template>', encoding="utf-8")
        result = Builder({"bundle": True, "source_maps": False}).build(root)
        assert result["failed"] == 0, result["errors"]
        bundle = root / "dist" / "static" / "js" / "App.bundle.js"
        assert bundle.exists()
        checked = subprocess.run(["node", "--check", str(bundle)], capture_output=True, text=True)
        assert checked.returncode == 0, checked.stderr


def test_bundler_supports_namespace_imports_and_reports_escape_errors():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "entry.js").write_text('import * as helper from "./helper.js"; export default helper;', encoding="utf-8")
        (root / "helper.js").write_text('export const value = 1;', encoding="utf-8")
        bundle = ModuleBundler(root).bundle("entry.js")
        assert "const helper = __teloce_modules['helper.js'];" in bundle.read_text(encoding="utf-8")

        (root / "escape.js").write_text('import value from "../outside.js"; export default value;', encoding="utf-8")
        try:
            ModuleBundler(root).bundle("escape.js")
        except BundleError as error:
            assert "escapes output directory" in str(error)
        else:
            raise AssertionError("expected an actionable BundleError")

        (root / "external.js").write_text('import runtime from "some-runtime"; export default runtime;', encoding="utf-8")
        try:
            ModuleBundler(root).bundle("external.js")
        except BundleError as error:
            assert "External import" in str(error)
        else:
            raise AssertionError("expected an external-import BundleError")


def test_named_vel_imports_preserve_named_import_syntax():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        parent = root / "static" / "js" / "App.vel"
        child = root / "static" / "js" / "components" / "Child.vel"
        child.parent.mkdir(parents=True)
        parent.write_text(
            '<template><Alias /></template><script>import { Button as Alias } from "./components/Child.vel"; export default {};</script>',
            encoding="utf-8",
        )
        child.write_text(
            '<template><p>Named</p></template><script>export const Button = {}; export default {};</script>',
            encoding="utf-8",
        )
        result = Builder({"source_maps": False}).build(root)
        assert result["failed"] == 0, result["errors"]
        parent_code = (root / "dist" / "static" / "js" / "App.js").read_text(encoding="utf-8")
        assert 'import { Button as Alias } from "./components/Child.js";' in parent_code
