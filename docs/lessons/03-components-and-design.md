# Lesson 3: reusable components and fast design

The fastest `.vel` projects are designed as systems rather than pages. Establish a small visual language first:

- spacing scale
- color and semantic status tokens
- typography scale
- button and input variants
- card/panel rules
- responsive breakpoints
- focus and keyboard states

Then build components around user actions:

```text
AppShell
  Navigation
  WindowManager
  DashboardCard
  DataTable
  FormField
  Dialog
  EmptyState
  Toast
```

## A useful component contract

Every reusable component should document:

- props it accepts
- events it emits
- slots it supports
- loading, empty, error, and success states
- keyboard behavior
- responsive behavior

## Example component

```html
<template>
  <article class="stat-card">
    <span class="label">{{ label }}</span>
    <strong>{{ value }}</strong>
    <small v-if="hint">{{ hint }}</small>
  </article>
</template>

<script>
export default {
  props: { label: String, value: [String, Number], hint: String }
};
</script>
```

Use the component repeatedly instead of copying markup. This makes redesigns much faster: changing one component updates every screen that uses it.

## Responsive design

Test at phone, tablet, laptop, and wide desktop sizes. Use flexible grids, avoid fixed widths, ensure controls have touch-sized targets, and hide decorative elements before hiding core functionality. A `.vel` application should remain useful when the viewport is narrow, not merely shrink the desktop layout.

## Accessibility

Use semantic elements, labels, keyboard focus, visible focus states, sufficient contrast, and useful error messages. A fast development tool is only effective when real users can operate what it generates.
