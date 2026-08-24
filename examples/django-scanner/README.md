# Django defensive web scanner

This example checks a user-supplied HTTP(S) URL for basic response metadata and security headers. It is intentionally defensive and bounded; do not expose it publicly without authentication, SSRF protection, rate limits, egress controls, and a queue.

```bash
python -m pip install -r requirements.txt
python build.py
python manage.py runserver
```

Open `http://127.0.0.1:8000` and scan a site you own.
