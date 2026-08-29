from teloce.compiler.compiler import Compiler


def test_generated_safe_runtime_blocks_prototype_escape_paths():
    result = Compiler({'dev': False, 'source_maps': False}).compile(
        '<template><button @click="__proto__.polluted = true">Run</button></template>'
        '<script>export default { data() { return {}; } };</script>',
        'Security.vel',
    )
    assert result['success']
    assert 'blocked' in result['code'] or '__proto__' in result['code']
    assert 'Function(' not in result['code']
    assert '__legacyEvaluate' not in result['code']


def test_standalone_runtime_contains_safe_assignment_guard():
    source = open('src/teloce/runtime/standalone.js', encoding='utf-8').read()
    assert 'prototype' in source and 'blocked' in source
    assert 'Function(' not in source
    assert 'allowRawHtml: false' in source
    assert 'sanitizeHtml' in source


def test_dynamic_html_is_sanitized_by_default():
    result = Compiler({'dev': False, 'source_maps': False}).compile(
        '<template><article v-html="content"></article></template>'
        '<script>export default { data() { return { content: "<img src=javascript:alert(1) onerror=alert(2)>" }; } };</script>',
        'HtmlSecurity.vel',
    )
    assert result['success']
    assert '__sanitizeHtml' in result['code']
    assert 'element.innerHTML = __sanitizeHtml(value)' in result['code']
