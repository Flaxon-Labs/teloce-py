# FastAPI CMS

This example is an async CMS editor. FastAPI owns the JSON API, while Teloce owns the list, editor state, and browser events.

```bash
python -m pip install -r requirements.txt
python build.py
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`. Content is in memory for easy experimentation.
