# Django admin + Teloce dashboard

This small application demonstrates the intended split: Django owns the
database, authentication, permissions, and `/admin/`; Teloce compiles the
interactive staff dashboard in `static/js/AdminDashboard.vel`.

```bash
python -m pip install -r requirements.txt
python build.py
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`python build.py` produces minified, shared-runtime production assets. Use
`python build.py --dev` when browser source maps and readable generated output
are more useful than smaller files.

Open `http://127.0.0.1:8000/admin/` to create products and set their stock.
Then open `http://127.0.0.1:8000/`, sign in with the staff account, and the
compiled `.vel` dashboard loads the live inventory summary from Django.

The API and dashboard require a staff account. This is deliberate: hiding an
admin screen in browser code is not authorization. In production set a unique
`SECRET_KEY`, `DEBUG=False`, correct `ALLOWED_HOSTS`, HTTPS, secure cookies,
CSRF settings, and a real database before deployment.
