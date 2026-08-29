# Teloce Gallery

A small real-world gallery application for testing editable Teloce-Py. It
uses multiple `.vel` files under `static/js/`, imported components, scoped CSS,
reactive search/filtering, keyed lists, Flask JSON endpoints, and a real
like/update flow.

## Run from the repository checkout

From the Teloce-Py repository root:

```bash
python -m pip install -e .
python examples/teloce-gallery/app.py
```

Open `http://127.0.0.1:5050`. `app.py` compiles the `.vel` source before
starting Flask, so no separate frontend command is required.
