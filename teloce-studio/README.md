# Teloce Studio

Teloce Studio is the planned visual no-code/low-code editor for generating real Flaxon applications with Teloce `.vel` components.

This directory currently contains the project structure and architecture boundary. Editor behavior, code generation, preview execution, and deployment integrations will be implemented in later phases.

## Planned source of truth

The editor project model describes pages, components, bindings, styles, routes, and backend resources. Generated `.vel`, Python, CSS, and configuration files remain ordinary editable project files.

## Planned local workflow

```text
create project -> visually edit -> generate .vel and Flaxon files -> run real preview -> export or deploy
```

See `docs/architecture.md`, `docs/roadmap.md`, and `docs/project-format.md`.
