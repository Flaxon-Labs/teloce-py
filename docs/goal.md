# Project goal

The goal is a dependable Python-first path from a `.vel` component to a working browser application:

```bash
python app.py
```

Developers should be able to keep their preferred Python framework while sharing a consistent component language and runtime contract with npm Teloce.

## Success criteria

A successful application should allow a developer to:

1. create `static/js/App.vel`;
2. write a template, component script, and optional scoped CSS;
3. run `python app.py` during development;
4. see the generated interface in a browser;
5. call real Python APIs from event handlers;
6. split the interface into imported components;
7. run tests against compiled assets;
8. build deterministic production output in CI.

The project does not aim to hide the browser/server boundary. It aims to make
that boundary simple, explicit, and productive for Python developers.
