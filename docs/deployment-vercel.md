# Deploying Teloce applications to Vercel

Vercel can host Teloce frontends and Python serverless routes, but each
request must finish within the platform limits. Compile `.vel` files during
the build; never compile them on every request.

## Build configuration

```json
{
  "buildCommand": "teloce build --out-dir dist --hash-assets --source-map",
  "rewrites": [
    { "source": "/assets/(.*)", "destination": "/dist/assets/$1" }
  ]
}
```

Adjust the destination to the actual static directory. Verify every rewrite:
Vercel routes requests using the rewritten destination path, so an overly broad
rewrite can send an asset request to a Python application route.

## Deployment checklist

1. Pin Python and Teloce versions.
2. Run the Teloce build in Vercel's build step.
3. Confirm the entry module, CSS, manifest, and every lazy chunk return HTTP 200.
4. Configure production environment variables in Vercel, not in Git.
5. Use Neon or another hosted database; do not rely on local SQLite in a
   serverless deployment.
6. Keep crawler and video-processing jobs outside the request path. Use a
   queue, scheduled worker, or external job service.
7. Test health, API response shape, navigation, refresh, and console errors.
8. Disable debug, HMR, and public diagnostics in production.

IndexedDB remains device-local browser storage. It is suitable for drafts,
history, and offline caches, not team synchronization or authoritative data.

## Framework mapping

Flask and FastAPI expose a serverless handler according to their Vercel
adapter. Django needs its normal WSGI/ASGI entrypoint and static configuration.
Flaxon needs its Vercel-compatible ASGI entrypoint and Jinax template setup.
The framework must serve the same generated asset paths tested locally.
