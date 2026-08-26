# Flaxon + Jinax + Teloce

This example is a real asynchronous Flaxon host. Jinax renders the HTML shell, Flaxon serves the API, and the compiled `.vel` module provides browser behavior.

```bash
python -m pip install -r requirements.txt
python build.py
flaxon run app:app --reload
```

Open <http://127.0.0.1:8000>. The app also exposes `/api/health`. Run `flaxon run --help` if your installed Flaxon release uses a different runner flag.
