# Compiler configuration reference

`teloce create` can generate `teloce.config.json`. A minimal configuration is:

```json
{
  "source": "static/js",
  "out_dir": "dist",
  "entry": "App.vel",
  "mode": "development",
  "source_map": true,
  "hash_assets": false,
  "minify": false,
  "bundle": false,
  "lazy_components": []
}
```

Development favors readable output and HMR. Production should use hashed
assets, deterministic output, private source maps when needed, and optional
esbuild for symbol-level tree-shaking and code splitting.

Generated output may include JavaScript, CSS, source maps, a manifest, shared
runtime files, lazy chunks, and a size report. Deploy the complete output set;
copying only the entry module causes lazy imports and runtime files to 404.

Recommended release command:

```bash
teloce build --out-dir dist --source-map --hash-assets --bundle --report
```

The built-in optimizer understands Teloce component imports and filters. It is
not a replacement for a complete JavaScript bundler's whole-program symbol
analysis; enable esbuild when that guarantee is required.
