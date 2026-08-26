# Teloce Studio architecture

The editor is a Flaxon-hosted application. Its browser UI is authored in `.vel` files. The backend owns project persistence, safe workspace access, code generation, compiler diagnostics, preview lifecycle, export, and deployment configuration.

The project model is metadata; generated `.vel`, Python, CSS, and configuration files are the portable source artifacts.
