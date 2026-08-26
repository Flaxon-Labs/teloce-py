# Flask host

This copy-pasteable example shows the normal framework-neutral integration: Flask renders the HTML shell and serves generated Teloce assets, while the `.vel` component owns browser interaction.

```bash
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> and <http://127.0.0.1:5000/api/health>.
