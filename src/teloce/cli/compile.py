"""Compile one .vel component from the command line."""

import json
from pathlib import Path
from typing import Any

from teloce.compiler.compiler import compile_file


def compile_command(args: Any) -> int:
    source = Path(args.source)
    output = Path(args.output) if args.output else source.with_suffix('.js')
    result = compile_file(source, source_maps=args.source_map, dev=False)
    if not result.get('success'):
        print(json.dumps(result.get('diagnostics', {}), indent=2))
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.get('code', ''), encoding='utf-8')
    if result.get('css'):
        output.with_suffix('.css').write_text(result['css'], encoding='utf-8')
    if args.source_map and result.get('map'):
        output.with_suffix(output.suffix + '.map').write_text(
            json.dumps(result['map'], indent=2), encoding='utf-8'
        )
    print(f"Compiled {source} -> {output}")
    return 0
