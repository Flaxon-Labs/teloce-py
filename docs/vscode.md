# VS Code extension

The upstream Teloce repository contains a VS Code extension package for `.vel` files. Its documented features include syntax highlighting, diagnostics, autocomplete, hover information, formatting, snippets, symbol support, and debugger integration.

Install it from the VS Code Extensions panel by searching for **Teloce**, or install a locally built package:

```bash
code --install-extension teloce-vscode.vsix
```

The source, commands, settings, and packaging instructions are maintained in the [Teloce VS Code extension package](https://github.com/aldanedev-create/telonce/tree/main/packages/vscode-extension). The extension improves authoring; Teloce-Py performs compilation and does not require the extension at runtime.

## Recommended setup

Open the Python project root in VS Code, install the extension, and create
`static/js/App.vel`. Use the extension for authoring and `python app.py` or
`teloce dev` in the integrated terminal for compilation. The extension does
not need to be installed on production servers.

The upstream extension documents formatting, validation, and opening the
debugger. In this Python repository, `teloce debug` starts the local diagnostics
dashboard described in [CLI](cli.md). Configure formatting and validation in
VS Code settings, then keep compiler and browser tests in CI because editor
diagnostics are not a replacement for a release build.
