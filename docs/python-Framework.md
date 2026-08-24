# Python framework support

Teloce is framework-agnostic at runtime. Flask, FastAPI, Django, and Flaxon need only:

1. a build step for `.vel` files;
2. a static-file route for generated JavaScript/CSS;
3. an HTML template containing a mount point.

See [framework integration](frameworks.md) and the four complete examples.

## Integration contract

Every framework integration needs:

```text
1. build .vel files
2. serve dist/static or another generated asset directory
3. render <div id="app"></div>
4. load the generated App.js module
5. expose backend data through authenticated APIs
```

Flask can use `python app.py`; FastAPI commonly uses `uvicorn`; Django uses
`manage.py runserver`; Flaxon can use its runner or an ASGI server. The
frontend component does not depend on which server performed the response.
