# Flaxon runtime notebook

This is a small notebook application using Flaxon, Jinax, the standalone Teloce browser runtime, and explicit Teloce signals. It intentionally has no `.vel` file: it demonstrates how to add Teloce behavior to server-rendered HTML first. The runtime handles `v-if`, `v-for`, interpolation, events, and reactive browser state; signals drive the save-status effect.

## Run it

```bash
python -m pip install -r requirements.txt
python build.py
python -m flaxon run app:app --reload
```

Open <http://127.0.0.1:8000>. Check <http://127.0.0.1:8000/api/health> for the Flaxon API health response.

The notebook stores notes in browser memory for clarity. A production version should use IndexedDB for offline storage or a Python database/API for durable multi-user data. `signals.js` and its `scheduler.js` dependency are copied into `dist/` during the build.
