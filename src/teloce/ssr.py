"""Server-side rendering helpers using Flaxon's Jinax engine.

Teloce keeps browser directives in the emitted module, while this adapter
translates the server-safe subset into Jinax/Jinja syntax. It never executes
component JavaScript on the server; values and actions must be supplied by the
Python host application.
"""

from __future__ import annotations

import re
import inspect
from typing import Any, Mapping


def to_jinax_template(template: str) -> str:
    """Translate safe Teloce server directives to Jinax template syntax."""
    result = str(template)
    result = re.sub(r'\s+v-if="([^"]+)"', r' data-teloce-if="\1"', result)
    # Convert common element-level v-if blocks while preserving the element.
    result = re.sub(
        r'<([A-Za-z][\w:-]*)([^>]*?)data-teloce-if="([^"]+)"([^>]*)>([\s\S]*?)</\1>',
        r'{% if \3 %}<\1\2\4>\5</\1>{% endif %}', result,
    )
    result = re.sub(r'\s+v-for="(?:\(([^)]+)\)|([^\s]+))\s+(?:in|of)\s+([^\"]+)"',
                    lambda match: f' data-teloce-for="{match.group(1) or match.group(2)}|{match.group(3).strip()}"', result)
    result = re.sub(
        r'<([A-Za-z][\w:-]*)([^>]*?)data-teloce-for="([^|]+)\|([^\"]+)"([^>]*)>([\s\S]*?)</\1>',
        r'{% for \3 in \4 %}<\1\2\5>\6</\1>{% endfor %}', result,
    )
    # Event handlers are browser-only. Drop them from SSR output.
    result = re.sub(r'\s+(?:@[\w.-]+|v-on:[\w.-]+)="[^"]*"', '', result)
    result = re.sub(r'\s+v-(?:bind|model|show|text|html)(?::[\w-]+)?="[^"]*"', '', result)
    result = re.sub(r'\s+data-teloce-(?:if|for)="[^"]*"', '', result)
    result = re.sub(r'\s+>', '>', result)
    return result


async def render_ssr(
    template: str,
    context: Mapping[str, Any] | None = None,
    *,
    engine: Any | None = None,
) -> str:
    """Render a Teloce template through Flaxon's Jinax engine.

    ``template`` is the contents of a ``<template>`` section, not a complete
    ``.vel`` file. Jinax is imported lazily so Teloce remains usable without
    Flaxon installed.
    """
    if engine is None:
        try:
            from flaxon.jinax import Jinax
        except ImportError as exc:  # pragma: no cover - depends on optional host
            raise RuntimeError(
                "SSR requires a Jinax/Jinja-compatible engine; pass engine=... "
                "or install flaxon-framework"
            ) from exc
        engine = Jinax(template_directory=".")
    values = dict(context or {})
    translated = to_jinax_template(template)
    environment = getattr(engine, "environment", engine)
    if hasattr(environment, "from_string"):
        compiled = environment.from_string(translated)
        if hasattr(compiled, "render_async") and getattr(environment, "is_async", False):
            result = compiled.render_async(**values)
        else:
            result = compiled.render(**values)
    elif hasattr(engine, "render"):
        result = engine.render(translated, values)
    else:
        raise TypeError("SSR engine must provide from_string() or render()")
    if inspect.isawaitable(result):
        result = await result
    return str(result)
