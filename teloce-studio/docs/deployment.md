# Teloce Studio deployment

## Local

```powershell
cd teloce-studio
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ..
python build.py
python -m flaxon run app:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`. Studio stores projects in `workspace/` by default. Set `TELOCE_STUDIO_WORKSPACE` to use a different directory.

## Vercel

Set the project root to `teloce-studio`. The repository includes `vercel.json`, `api/index.py`, a build command, static output, and API rewrites. Persistent project storage requires an external database or object store; the default filesystem workspace is suitable for local development and ephemeral preview work, not multi-user production persistence.

## PWA and MSIX

Deploy over HTTPS, then submit the public URL to PWABuilder. The app includes a manifest, install icon, service worker, offline page, scope, orientation, shortcut, and standalone display settings. PWABuilder-generated MSIX identity, certificate, publisher, and Store metadata must be supplied by the publisher during packaging.
