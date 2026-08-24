# Flaxon network operations dashboard

This example follows Flaxon's async application style: a `Flaxon` app, Jinax-rendered HTML, JSON routes, and a WebSocket endpoint for room events. The inventory is simulated so the example is safe to run locally.

```bash
python -m pip install -r requirements.txt
python build.py
flaxon run app:app --reload
```

Flaxon versions may expose different runner flags; use `flaxon run --help` for the installed release.
