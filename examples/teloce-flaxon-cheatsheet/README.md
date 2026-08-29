# Teloce + Flaxon Cheatsheet

A real, server-rendered documentation app with 40 `.vel` components. It is intentionally built with readable Teloce syntax so it can be used as a compiler stress fixture and as a copy/paste learning project.

## Local development

```powershell
python -m pip install -r requirements.txt
python build.py
python -m flaxon run app:app --reload
```

Open `http://127.0.0.1:8000`. The build fails loudly if any `.vel` component has a compiler error.

The example pins `teloce-py==0.2.0b2`, which is the latest published PyPI pre-release at the time of writing. If you are developing against this repository in editable mode, install the repository instead with `python -m pip install -e ../..`.

## Vercel

Set the project root to this directory and use:

- Build command: `python build.py`
- Output directory: `dist`
- Install command: `pip install -r requirements.txt`

The `api/index.py` entrypoint exposes the Flaxon ASGI application. Vercel deployments are stateless; this app intentionally has no login or database because it is documentation and compiler demonstration content.

## What this proves

- Multiple `.vel` files can be imported into another `.vel` file.
- HTML, CSS, events, conditions, loops, filters, and reactive state compile together.
- Flaxon can serve Jinax HTML and Teloce-generated browser modules in one application.
- The same project can be checked with `teloce build`, `node --check`, and browser tests.
