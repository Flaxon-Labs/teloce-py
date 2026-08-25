# Lesson 5: build an OS-style simulation

An OS simulation is a desktop metaphor implemented in the browser. It is not an operating-system kernel. It is a web application with a desktop surface, application windows, local storage, and a consistent interaction model.

## Core architecture

```text
Desktop shell
  wallpaper and desktop icons
  launcher / command palette
  task dock
  window manager
    app windows
      file explorer
      terminal or Python workspace
      media studio
      network monitor
      settings
```

## Window state

Represent each window with stable state:

```js
{
  id: "study",
  title: "Study Workspace",
  open: true,
  minimized: false,
  maximized: false,
  x: 120,
  y: 80,
  width: 760,
  height: 520,
  zIndex: 4
}
```

Use one manager for open, close, focus, minimize, maximize, and restore. Persist only safe UI preferences such as wallpaper and window positions. Do not put secrets in local storage.

## Files and local-first data

IndexedDB is appropriate for notes, imported files, media metadata, and offline drafts. Add export/import backup because browser storage can be cleared. Put size limits on files and show users whether data is local or uploaded.

## Application examples

- File Explorer reads the IndexedDB file store.
- Python Workspace sends code to a bounded Web Worker.
- Video Studio imports local media and exports browser-supported WebM.
- Network Pulse measures a real request to a server endpoint.
- Security Scanner calls a permission-restricted Python service.
- Study Workspace combines notes, recordings, and student files.

## Making it feel like your own product

Do not copy another operating system's branding or assets. Choose an original design language: Flaxon uses spatial cards, teal/orange accents, a launcher palette, and a compact dock. A coherent identity is more valuable than imitating a familiar product pixel-for-pixel.

## Build order

1. Shell and responsive layout.
2. Window manager and focus rules.
3. One complete application, such as Files.
4. Persistence and backup.
5. Keyboard shortcuts and accessibility.
6. PWA offline behavior.
7. Real integrations and security boundaries.
8. Browser end-to-end tests at multiple viewport sizes.
