# Flask chat

This example is a small Flask chat client backed by JSON endpoints. It demonstrates keyed messages, `:model`, event modifiers, async browser requests, and a compiled `.vel` component.

```bash
python -m pip install -r requirements.txt
python build.py
python app.py
```

Open `http://127.0.0.1:5000`. Messages are in memory and reset when the process stops.
