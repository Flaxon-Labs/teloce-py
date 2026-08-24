# Development workflow

For a beginner-friendly workflow:

```bash
python app.py
```

`app.py` calls `build_project`, Flask/FastAPI/Django/Flaxon serves the page, and the browser loads the generated module. For larger teams, move compilation to `teloce dev` locally and `teloce build` in CI.

Recommended loop:

1. edit `static/js/App.vel`;
2. refresh or use development HMR;
3. exercise the real API route;
4. run unit and browser tests;
5. build immutable assets for deployment.

## Team workflow

Use `teloce doctor --verbose` when onboarding, `teloce lint --strict` in CI,
`teloce dev` for interactive development, and `teloce build --hash-assets
--bundle` for a release build. Test the Python API separately from browser
interactions, then run end-to-end tests against the compiled assets.

When a component fails, reduce it to the smallest `.vel` file, inspect the
compiler diagnostic, verify the network response, and check browser console
errors. Do not solve an authorization problem in the frontend.
