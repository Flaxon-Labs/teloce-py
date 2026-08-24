"""Production SFC contract tests."""

from teloce.compiler.compiler import compile
from teloce.sfc.parser import SFCParser, parse_sfc_result


def test_sfc_block_attributes_multiple_styles_and_scope_marker():
    source = '''
<template lang="html"><div class="card"><span>Ready</span></div></template>
<script setup lang="ts">const message = "Ready";</script>
<style scoped>.card { color: red; }</style>
<style lang="css">span { font-weight: bold; }</style>
'''
    parser = SFCParser()
    component = parser.parse(source, "Card.vel")
    assert component is not None
    assert component.script.setup is True
    assert component.script.lang == "ts"
    assert component.style.lang == "css"
    assert component.style.scoped is True
    assert "font-weight" in component.style.css

    result = compile(source, "Card.vel")
    assert result["success"] is True
    assert "data-v-" in result["code"]
    assert "data-v-" in result["css"]


def test_sfc_parse_result_exposes_tooling_diagnostics():
    result = parse_sfc_result("<template><div>ok</div></template>", "Bare.vel")
    assert result["name"] == "Bare"
    assert result["component"] is not None
    assert result["diagnostics"]["errors"] == []
    assert any("script" in warning.lower() for warning in result["diagnostics"]["warnings"])


def test_duplicate_template_is_rejected():
    parser = SFCParser()
    component = parser.parse(
        "<template><div>a</div></template><template><div>b</div></template>",
        "Duplicate.vel",
    )
    assert component is None
    assert any("Only one <template>" in error for error in parser.errors)


def test_scoped_css_is_installed_by_the_generated_component():
    source = '''
<template><main class="shell"><h1>Hello</h1></main></template>
<style scoped>.shell { color: red; }</style>
'''
    result = compile(source, "Shell.vel")

    assert result["success"] is True
    # Markup and CSS must share the same scope contract.
    assert 'data-v-' in result["code"]
    assert 'data-v-' in result["css"]
    assert 'const __style =' in result["code"]
    assert 'data-teloce-style' in result["code"]


def test_inline_css_can_be_disabled_for_external_stylesheet_deployments():
    source = '''
<template><div class="shell">Hello</div></template>
<style scoped>.shell { color: red; }</style>
'''
    result = compile(source, "Shell.vel", inline_css=False)

    assert result["success"] is True
    assert 'const __style = ""' in result["code"]
    assert 'data-v-' in result["css"]


def test_css_modules_coordinate_template_names_and_css_selectors():
    source = '''
<template><div class="card title">Ready</div></template>
<style module>.card { color: red; } .title { font-weight: bold; }</style>
'''
    result = compile(source, "Card.vel")
    assert result["success"] is True
    assert "card__Card_" in result["code"]
    assert "title__Card_" in result["code"]
    assert "card__Card_" in result["css"]
    assert "title__Card_" in result["css"]


def test_multiple_style_blocks_keep_scoped_and_global_semantics():
    source = '''
<template><div class="local"><span>Ready</span></div></template>
<style scoped>.local { color: red; }</style>
<style>body { margin: 0; }</style>
'''
    result = compile(source, "Mixed.vel")
    assert result["success"] is True
    assert ".local[data-v-" in result["css"]
    assert "body { margin: 0 }" in result["css"]
    assert "body[data-v-" not in result["css"]


def test_sfc_sections_handle_nested_templates_quoted_attributes_and_script_strings():
    source = '''
<template data-label=">"><template><span>Ready</span></template></template>
<script>export default { data() { return { marker: "</script>" }; } };</script>
<style scoped>.ready { color: red; }</style>
'''
    parser = SFCParser()
    component = parser.parse(source, "Robust.vel")
    assert component is not None
    assert component.script.raw.endswith('"</script>" }; } };')
    assert "Ready" in repr(component.template)


def test_nested_prop_definitions_and_validators_are_preserved():
    source = '''
<template><div>{{ title }}</div></template>
<script>export default { props: { title: { type: String, required: true, validator: value => value.length > 0 }, count: { type: Number, default: 1 } } };</script>
'''
    component = SFCParser().parse(source, "Props.vel")
    assert component is not None
    assert component.script.props["title"]["required"] is True
    assert "value.length" in component.script.props["title"]["validator"]
    assert component.script.props["count"]["default"] == "1"
    result = compile(source, "Props.vel")
    assert result["success"] is True
    assert "validator" in result["code"]


def test_common_typescript_sfc_annotations_are_transpiled_to_valid_javascript():
    source = '''
<template><button @click="load">{{ count }}</button></template>
<script lang="ts">
interface User { id: number; }
export default { data(): any { return { count: 0 }; }, methods: {
  async load(id: string): Promise<void> { const next: number = id.length; this.count = next; }
} };
</script>
'''
    result = compile(source, "Typed.vel")
    assert result["success"] is True
    assert "async load(id)" in result["code"]
    assert "interface User" not in result["code"]


def test_module_level_javascript_is_preserved_without_local_component_imports():
    source = '''
<template><button @click="setMessage">{{ message }}</button></template>
<script>
const prefix = "Ready: ";
import Child from "./Child.vel";
export default {
  data() { return { message: "Waiting" }; },
  methods: { setMessage() { this.message = prefix + "done"; } }
};
</script>
'''
    result = compile(source, filename="App.vel", source_maps=False)
    assert result["success"]
    assert 'const prefix = "Ready: ";' in result["code"]
    assert "./Child.vel" not in result["code"]


def test_typescript_object_types_generics_and_const_assertions_are_removed_safely():
    source = '''
<template><button @click="load">{{ count }}</button></template>
<script lang="ts">
type User = { id: number; name: string };
const defaults = { count: 0 } as const;
export default {
  data(): { count: number } { return defaults; },
  methods: { async load<T extends string>(value: T): Promise<void> { this.count = value.length; } }
};
</script>
'''
    result = compile(source, "AdvancedTyped.vel", source_maps=False)
    assert result["success"]
    assert "type User" not in result["code"]
    assert "as const" not in result["code"]
    assert "async load(value)" in result["code"]


def test_simple_typescript_enums_are_lowered_to_runtime_objects():
    source = '''
<template><div>{{ status }}</div></template>
<script lang="ts">
enum Status { Idle, Ready = "ready" }
export default { data() { return { status: Status.Ready }; } };
</script>
'''
    result = compile(source, "Enum.vel", source_maps=False)
    assert result["success"]
    assert "const Status = {Idle: 0, Ready: \"ready\"};" in result["code"] or "const Status = {Idle: 0, Ready: 'ready'};" in result["code"]
    assert "enum Status" not in result["code"]
