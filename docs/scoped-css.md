# Scoped CSS

```html
<style scoped>
.card { padding: 1rem; }
</style>
```

The compiler adds a deterministic scope marker to component markup and selectors. This prevents `.card` in one component from unintentionally styling another component. Use global styles for resets and design tokens.

Scoped CSS is useful for component ownership, but it is not isolation from
untrusted content and it is not a security boundary. Global styles belong in a
global stylesheet. Prefer design tokens or CSS variables for values shared by
many components. Review generated CSS in production builds when using complex
selectors, animations, or third-party styles.
