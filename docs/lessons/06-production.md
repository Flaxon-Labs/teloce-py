# Lesson 6: production delivery

## Development loop

```bash
teloce doctor --verbose
teloce lint --strict
teloce build --out-dir public
python app.py
```

Use the exact commands supported by your project configuration; the important principle is that source `.vel` files are compiled during development/build, while the server serves generated assets in production.

## Release checklist

- Pin and audit dependencies.
- Compile all `.vel` files in CI.
- Run compiler, API, and browser tests.
- Test mobile and desktop viewports.
- Check service-worker cache updates.
- Confirm source maps and useful production errors.
- Verify security headers and content-security policy.
- Set upload, request, and execution limits.
- Document browser support and CDN requirements.
- Publish a changelog and versioned release.

## PyPI version guidance

Documentation-only changes do not require a new PyPI version. Release a new version when the published compiler, runtime, CLI, package metadata, or supported behavior changes. Since this repository currently reports `0.2.0b1`, it is still a beta release. A coordinated compiler/runtime feature release should use the next version according to your policy, for example `0.2.0b2` for another beta or `0.2.0` when the release contract is stable and tested.

Do not upload a new version merely to make GitHub documentation available. Update the repository docs now; publish a new package only when users need new installable code or when you intentionally want a release containing the documentation in its distribution metadata.
