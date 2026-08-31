from pathlib import Path
from types import SimpleNamespace

from teloce.cli.lint import apply_lint_fixes, lint_file


def test_lint_fix_writes_safe_repairs_and_relint_passes(tmp_path: Path):
    component = tmp_path / "App.vel"
    component.write_text(
        '''<template>
<for item in items>
  <p>Rows</p>
</for>
</template>
''',
        encoding="utf-8",
    )
    args = SimpleNamespace(fix=False, strict=False)
    issues = lint_file(component, args)
    assert len(issues) == 2
    assert apply_lint_fixes(component, issues) is True
    assert lint_file(component, args) == []
    content = component.read_text(encoding="utf-8")
    assert 'key="index"' in content
    assert "export default {};" in content


def test_lint_fix_does_not_modify_parser_errors(tmp_path: Path):
    component = tmp_path / "Broken.vel"
    original = "<template><div></template>"
    component.write_text(original, encoding="utf-8")
    issues = lint_file(component, SimpleNamespace(fix=True, strict=False))
    assert issues
    assert apply_lint_fixes(component, issues) is False
    assert component.read_text(encoding="utf-8") == original


def test_lint_does_not_treat_form_as_legacy_for_loop(tmp_path: Path):
    component = tmp_path / "Form.vel"
    component.write_text(
        '<template><form @submit.prevent="save"><button>Save</button></form></template>'
        '<script>export default { methods: { save() {} } };</script>',
        encoding="utf-8",
    )
    issues = lint_file(component, SimpleNamespace(fix=False, strict=True))
    assert not any(issue["message"] == 'For loop missing "key" attribute' for issue in issues)


def test_lint_recognizes_bound_keys_on_v_for(tmp_path: Path):
    component = tmp_path / "List.vel"
    component.write_text(
        '<template><ul><li v-for="item in items" :key="item.id">'
        '{{ item.name }}</li></ul></template><script>export default {};</script>',
        encoding="utf-8",
    )
    assert lint_file(component, SimpleNamespace(fix=False, strict=True)) == []
