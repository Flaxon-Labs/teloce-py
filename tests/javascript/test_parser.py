import pytest

from teloce.javascript.parser import (
    JavaScriptSyntaxError,
    parse_javascript,
    parse_javascript_language,
    tokenize_javascript,
)


def test_javascript_tokenizer_preserves_locations_and_opaque_literals():
    tokens = tokenize_javascript('// ignored\nconst text = "{ not syntax }"; const fn = () => `hello ${name}`;')
    values = [token.value for token in tokens]
    assert values[:4] == ["const", "text", "=", '"{ not syntax }"']
    assert any(token.kind == "template" for token in tokens)
    assert tokens[0].line == 2
    assert tokens[0].column == 1


def test_javascript_tokenizer_handles_comments_and_operators():
    tokens = tokenize_javascript("let value = a?.b ?? 0; value += 1;")
    assert "?." in [token.value for token in tokens]
    assert "??" in [token.value for token in tokens]
    assert "+=" in [token.value for token in tokens]


def test_javascript_tokenizer_keeps_modern_numeric_literals_intact():
    tokens = tokenize_javascript("const a = 1e-3; const b = 0xFFn; const c = 0b1010_0001;")
    assert [token.value for token in tokens if token.kind == "number"] == [
        "1e-3", "0xFFn", "0b1010_0001"
    ]


def test_javascript_tokenizer_reports_unterminated_literals():
    with pytest.raises(JavaScriptSyntaxError):
        tokenize_javascript('const broken = "never ends')


def test_parser_separates_semicolon_free_module_declarations():
    program = parse_javascript('import First from "./First.vel"\nimport Second from "./Second.vel"')
    assert [node.kind for node in program.body] == ["ImportDeclaration", "ImportDeclaration"]


def test_parser_treats_regex_literals_as_opaque_tokens():
    program = parse_javascript('const match = /[{}\\/]+/giu.test(value);')
    assert len(program.body) == 1


def test_parser_keeps_division_as_operators():
    program = parse_javascript('const ratio = total / count;')
    assert len(program.body) == 1


def test_parser_accepts_hashbang():
    program = parse_javascript('#!/usr/bin/env node\nexport const ready = true;')
    assert program.body[0].kind == "ExportDeclaration"


def test_parser_exposes_source_located_language_declaration_nodes():
    program = parse_javascript(
        'const answer = 42\n'
        'function greet(name) { return `Hello ${name}`; }\n'
        'class Service {}\n'
        'answer + 1;'
    )
    assert [node.kind for node in program.body] == [
        "VariableDeclaration", "FunctionDeclaration", "ClassDeclaration", "ExpressionStatement"
    ]
    assert program.body[0].name == "answer"
    assert program.body[1].name == "greet"
    assert program.body[2].name == "Service"
    assert program.body[1].line == 2
    assert program.body[1].column == 1
    assert program.body[1].source.startswith("function greet")


def test_parser_does_not_split_continuation_after_assignment():
    program = parse_javascript("const value =\n  factory()\nconst next = 2")
    assert len(program.body) == 2
    assert program.body[0].source.startswith("const value")


def test_language_parser_builds_nested_expression_and_statement_nodes():
    program = parse_javascript_language(
        "const total = items.map(item => item.price).reduce((a, b) => a + b, 0);\n"
        "function show(value) { if (value) { return value; } return 0; }"
    )
    declaration, function = program.body
    assert declaration.kind == "VariableDeclaration"
    assert declaration.children[0].kind == "VariableDeclarator"
    assert declaration.children[0].children[0].kind in {"CallExpression", "MemberExpression"}
    assert function.kind == "FunctionDeclaration"
    assert function.name == "show"
    assert function.children[0].kind == "BlockStatement"
    assert function.children[0].children[0].kind == "IfStatement"
    assert function.children[0].children[0].children[1].kind == "BlockStatement"


def test_language_parser_handles_modern_spread_new_and_arrow_blocks():
    program = parse_javascript_language(
        "const copy = {...source, ready: true};\n"
        "const values = (...items) => { return new Set(items); };"
    )
    first, second = program.body
    assert first.children[0].children[0].kind == "ObjectExpression"
    assert second.children[0].children[0].kind == "ArrowFunctionExpression"
    assert second.children[0].children[0].children[1].kind == "BlockStatement"
    assert "new Set" in second.children[0].children[0].children[1].source


def test_language_parser_preserves_postfix_updates_and_module_boundaries():
    program = parse_javascript_language(
        "import value, * as api from './api.js'\n"
        "export { value };\n"
        "counter++;"
    )
    assert [node.kind for node in program.body] == [
        "ImportDeclaration", "ExportDeclaration", "ExpressionStatement"
    ]
    assert program.body[-1].children[0].kind == "UpdateExpression"


def test_language_parser_reports_mismatched_nested_delimiters_with_a_hint():
    with pytest.raises(JavaScriptSyntaxError, match="expected") as error:
        parse_javascript_language("const value = ({ broken: true ]);")
    assert error.value.token is not None
    assert error.value.suggestion
