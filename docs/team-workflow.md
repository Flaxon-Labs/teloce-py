# Team workflow

Teloce works well in a normal Git-based team workflow.

1. Create a branch for a page, component, API, or compiler change.
2. Keep `.vel` source, templates, Python code, and tests in the same pull request when they change together.
3. Give each page one entry component and put reusable UI in `static/js/components/`.
4. Run `python build.py` and `python -m pytest -q` before review.
5. Review generated output as a build artifact; do not hand-edit `dist/` to fix source problems.
6. Deploy a preview from the branch and test navigation, API failures, mobile layout, and a clean browser profile.
7. Merge only after the production build succeeds.

IndexedDB autosave is local to one browser profile. It protects an individual user's draft, but it is not team synchronization. For real collaboration, store project documents and revisions on the server, identify users, authorize project access, detect stale revisions, and merge or reject conflicting updates. Do not put deployment tokens or database credentials in `.vel`, browser storage, or generated JavaScript.

## Suggested ownership

- UI team: `.vel`, component styles, templates, accessibility, browser tests.
- Python team: routes, schemas, database, authorization, jobs, and integrations.
- Platform team: build pipeline, hosting, static asset caching, observability, and secrets.

Use small commits and document any change to the project model or generated file contract. This keeps visual-editor output reviewable and makes rollback possible.

