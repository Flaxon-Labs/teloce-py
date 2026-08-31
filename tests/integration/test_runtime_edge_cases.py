from teloce.compiler.compiler import compile
from teloce.sfc.parser import parse_sfc


def test_loop_event_handlers_preserve_iteration_scope():
    source = '''
<template>
  <button v-for="item in items" :key="item.id" @click="choose(item)">{{ item.name }}</button>
</template>
<script>
export default {
  data() { return { items: [{ id: 1, name: "One" }] }; },
  methods: { choose(item) { this.selected = item.id; } }
};
</script>
'''
    result = compile(source, "LoopEvents.vel")
    assert result["success"]
    assert "data-teloce-loop-scope" in result["code"]
    assert "eventScope" in result["code"]
    assert "loopScopes.set" in result["code"]
    assert 'JSON.parse(element.getAttribute("data-teloce-loop-scope")' not in result["code"]


def test_generated_components_wrap_nested_objects_and_arrays_reactively():
    result = compile(
        '<template><p>{{ user.name }} {{ items.length }}</p></template>'
        '<script>export default { data() { return { user: { name: "A" }, items: [] }; } };</script>',
        "NestedReactivity.vel",
    )
    assert result["success"]
    assert "const __reactiveCache = new WeakMap()" in result["code"]
    assert "deleteProperty" in result["code"]


def test_html_void_elements_do_not_corrupt_the_template_ast():
    result = compile(
        '<template><label>Name<input name="name"><br><img src="/logo.svg"></label></template>',
        "VoidElements.vel",
    )
    assert result["success"]


def test_sfc_section_tags_inside_script_strings_are_not_sections():
    component = parse_sfc(
        '''
<template><p>Hello</p></template>
<script>
export default { data() { return { example: "<template>not a section</template>" }; } };
</script>
''',
        "EmbeddedTags.vel",
    )
    assert component is not None
