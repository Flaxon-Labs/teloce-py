# Multiple HTML files with `.vel`

A multi-page Python application can use a separate HTML shell and `.vel` entry point for each page.

```text
templates/
├── index.html
└── admin.html
static/js/
├── App.vel
└── admin/Admin.vel
```

`templates/index.html`:

```html
<div id="app"></div>
<script type="module" src="/static/js/App.js"></script>
```

`templates/admin.html`:

```html
<div id="admin-app"></div>
<script type="module" src="/static/js/admin/Admin.js"></script>
```

The compiler discovers both `.vel` files. Each entry point can import shared components:

```js
import StatusCard from "../components/StatusCard.vel";
```

Flask can render the pages with two routes:

```python
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/admin")
def admin():
    return render_template("admin.html")
```

FastAPI uses `Jinja2Templates`, Django uses `render(request, "admin.html")`, and Flaxon uses `request.render("admin.html", context)`. Keep page authorization in those Python routes; hiding an admin link in `.vel` is not access control.

