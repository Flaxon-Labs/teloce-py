# Errors and diagnostics

Compiler errors identify the source file and the failing phase when possible. Common causes are mismatched template tags, invalid component structure, unresolved local imports, malformed directives, and unsupported script syntax.

When debugging:

1. run `teloce build` or call `compile_file` for one component;
2. read the diagnostic before inspecting generated code;
3. validate the smallest failing component;
4. run browser tests for event, loop, and router behavior.

## Common diagnostics

| Problem | Likely cause | Check |
|---|---|---|
| Missing mount output | HTML selector or generated asset path is wrong | Browser network tab and mount point |
| Mismatched closing tag | Invalid SFC template structure | Pair every non-void tag |
| Import cannot be resolved | Incorrect relative path or unsupported external import | Build from the entry component |
| UI does not update | State was not changed through reactive data/signal | Confirm the event and state value |
| API works but UI is empty | Response shape differs from the expression | Inspect network response JSON |
| Styles do not apply | Wrong output path or selector scope | Inspect generated CSS and DOM marker |

Compiler diagnostics are not a substitute for server logs or browser console
errors. Capture both when reporting an issue.
