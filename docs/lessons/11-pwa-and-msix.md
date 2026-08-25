# Lesson 11: turn a Teloce-Py app into a PWA and MSIX

This lesson shows how to take a compiled `.vel` application from “works in the browser” to an installable PWA and a PWABuilder Windows package.

## 1. Add the manifest

Create `public/manifest.webmanifest` with stable identity, display settings, icons, and screenshots:

```json
{
  "name": "My Teloce App",
  "short_name": "Teloce App",
  "id": "/?app=my-teloce-app",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "landscape",
  "theme_color": "#101827",
  "background_color": "#0b1220",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "screenshots": [
    { "src": "/screenshots/desktop.png", "sizes": "1280x720", "type": "image/png", "form_factor": "wide" },
    { "src": "/screenshots/mobile.png", "sizes": "390x844", "type": "image/png", "form_factor": "narrow" }
  ]
}
```

The file dimensions must match the metadata. A file called `icon-192.png` must really be `192×192`.

## 2. Register the service worker

Keep the worker at the site root so it can control the complete application:

```html
<script>
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js", { scope: "/" });
    });
  }
</script>
```

The worker should cache the offline shell and generated assets, handle failed navigations with an offline page, and use a new cache name when the shell changes.

## 3. Test the PWA before packaging

Check these URLs on the deployed HTTPS site:

```text
/manifest.webmanifest  -> 200 and valid JSON
/sw.js                  -> 200 JavaScript
/offline.html           -> 200 HTML
/icons/icon-192.png     -> 192×192 PNG
/icons/icon-512.png     -> 512×512 PNG
```

Then use browser developer tools to confirm the service worker is activated and controls `/`.

## 4. Run PWABuilder

1. Deploy the app to a public HTTPS URL.
2. Open [PWABuilder](https://www.pwabuilder.com/).
3. Enter the deployed URL.
4. Resolve service-worker, manifest, icon, and screenshot warnings.
5. Choose **Package for Stores**.
6. Choose **Microsoft Store**.
7. Enter the identity reserved for your Microsoft Partner Center app.
8. Generate the package.
9. Download the package ZIP and keep the `.msix`, `.msixbundle`, certificate, and install script together.

The identity must match the values reserved for the Windows Store listing. Do not invent a publisher identity for a store submission.

## 5. Test the generated package

Test the sideload package on a clean Windows machine. Run the generated installation script if PWABuilder provides one, or install the package using the supported Windows app installer flow. Confirm:

- The app opens in standalone mode.
- The start URL loads over HTTPS.
- The icon and display name are correct.
- Service-worker offline behavior still works.
- External embedded apps and permissions behave as expected.
- The package identity matches the intended Store listing.

## 6. Release discipline

Create a new frontend build whenever `.vel` source or runtime code changes. Increment the PWA cache name when cached shell assets change. Generate a new MSIX package from the deployed release artifact, not from an uncommitted local folder.

Documentation-only lesson changes do not require a new Teloce-Py release. Publish a new package version when compiler, runtime, CLI, or supported behavior changes.

