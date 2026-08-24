# Migrating from npm Teloce

Copy the existing `.vel` files into the Python project's static source tree and build one entry component first:

```bash
teloce build --out-dir dist --source-map
```

The original API is preserved. `@click`, `:class`, `:show`, `:model`, `<if>`, and `<for>` remain valid. The Python implementation additionally accepts `v-if`, `v-for`, `v-on`, `v-bind`, `v-model`, `v-show`, `v-text`, and `v-html`.

Most component-level code transfers unchanged. Node-only build plugins do not: port their transformation to a Python compiler plugin or move the behavior into a browser runtime plugin. Verify behavior in a browser, especially keyed lists, slots, router navigation, custom directives, and filters.

The goal is source-level compatibility, but no compiler can promise compatibility with an arbitrary third-party plugin without testing that plugin's contract.

## Migration checklist

- inventory npm plugins and separate Node-only code from browser code;
- move the entry `.vel` component and its local imports;
- replace npm API calls with Python framework endpoints where appropriate;
- compare original and generated behavior in a real browser;
- test keyed lists, forms, event modifiers, conditions, slots, scoped CSS,
  filters, plugins, and router navigation;
- keep the upstream VS Code extension for `.vel` authoring;
- pin the Python compiler version after the migration passes.
