# About Teloce-Py

Teloce-Py is the Python implementation of the Teloce `.vel` component compiler. It compiles a component into browser JavaScript and CSS while leaving HTTP, authentication, databases, and deployment to your Python application.

The project is useful when a team wants reactive browser interfaces but does not want to add a Node-based frontend toolchain.

Teloce-Py is not a Python-to-JavaScript language and it does not run Python in
the browser. Scripts inside `.vel` files are JavaScript component scripts. The
Python compiler parses the SFC, validates its structure, generates browser
assets, and leaves your server framework in control of the application.

The intended application loop is:

```text
edit static/js/App.vel -> python app.py -> open the browser -> call Python APIs
```

For larger projects, use `teloce dev` during development and `teloce build` in
CI. See [Getting started](getting-started.md), [CLI](cli.md), and the
[real-world examples](real-world-examples.md).
