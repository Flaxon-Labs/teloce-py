"""CSS module name generation shared by stylesheet and template emitters."""

from __future__ import annotations

import hashlib
import re
from typing import Dict


class CSSModules:
    _class_pattern = re.compile(r"\.(-?[A-Za-z_][\w-]*)")

    @classmethod
    def mapping(cls, css: str, component_name: str) -> Dict[str, str]:
        names = []
        for match in cls._class_pattern.finditer(css or ""):
            name = match.group(1)
            if name not in names:
                names.append(name)
        digest = hashlib.sha1(component_name.encode("utf-8")).hexdigest()[:6]
        return {name: f"{name}__{component_name}_{digest}" for name in names}

    @classmethod
    def transform_css(cls, css: str, component_name: str) -> tuple[str, Dict[str, str]]:
        mapping = cls.mapping(css, component_name)
        transformed = cls._class_pattern.sub(
            lambda match: "." + mapping.get(match.group(1), match.group(1)),
            css,
        )
        return transformed, mapping
