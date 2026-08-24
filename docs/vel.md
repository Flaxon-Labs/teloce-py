# The `.vel` file format

`.vel` files are Teloce Single File Components. They are source files, not Python templates and not files that the browser should receive directly. The compiler transforms them into browser assets.

Use `App.vel` as the entry component, compile it before the server starts, and mount `App.js` from the HTML page.

The file extension is only the source format. Browsers should receive the
generated `.js` and `.css` assets, not the original `.vel` file. Keep source
files in the project and generated files in `dist/` or another ignored output
directory.
