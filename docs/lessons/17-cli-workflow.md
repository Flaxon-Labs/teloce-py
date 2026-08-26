# Lesson 17: The Teloce CLI workflow

The CLI gives teams a repeatable way to create, inspect, develop, validate, and build `.vel` applications.

## Install and inspect

```bash
python -m pip install --upgrade teloce-py
teloce --version
teloce --help
teloce doctor --verbose
```

Run these commands from the project root. `doctor` is useful when a project works on one machine but not another because it reports Python, Teloce, discovered files, directories, and configuration.

## Create a project

```bash
teloce create motion-app --template flask
cd motion-app
python app.py
```

The generated Flask application should contain an HTML mount point and a build call. The essential pattern is:

```python
from pathlib import Path
from flask import Flask, render_template
from teloce.build import build_project

ROOT = Path(__file__).parent
app = Flask(__name__, template_folder=str(ROOT / 'templates'))

@app.get('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    build_project(ROOT, options={'dev': True, 'source_maps': True})
    app.run(debug=True, port=5000)
```

## Daily development commands

```bash
teloce dev
teloce watch
teloce dev --port 5173 --proxy http://127.0.0.1:5000
```

Use `dev` for the integrated development workflow. Use `watch` when the Python server is managed separately. Use `--no-hmr` when a browser extension, proxy, or framework integration conflicts with hot reload.

## Validate before committing

```bash
teloce lint --strict
teloce build --out-dir dist --source-map
teloce doctor --verbose
```

Treat lint errors as CI failures. Keep generated output out of source control when the deployment platform can run the build. If your host cannot run Python during deployment, commit or upload the generated output according to that host's rules.

## Debug a real application

```bash
teloce debug --no-open
```

The dashboard runs locally, reports discovered components and diagnostics, and exposes JSON endpoints. It is a development inspector, not a public monitoring system. Do not expose it to the internet without authentication and access controls.

## CI example

```yaml
name: validate-teloce
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e .
      - run: teloce doctor --verbose
      - run: teloce lint --strict
      - run: teloce build --out-dir dist --source-map
```

## Command reference

| Goal | Command |
|---|---|
| Create an app | `teloce create my-app --template flask` |
| Develop | `teloce dev` |
| Watch files | `teloce watch` |
| Build production assets | `teloce build --out-dir dist --hash-assets --bundle` |
| Diagnose setup | `teloce doctor --verbose` |
| Validate components | `teloce lint --strict` |
| Open diagnostics dashboard | `teloce debug` |
| Benchmark compilation | `teloce benchmark . --json` |

