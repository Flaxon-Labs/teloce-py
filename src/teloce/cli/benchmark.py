"""Compiler benchmark command."""

from __future__ import annotations

import json
import time
import tracemalloc
from pathlib import Path
from typing import Any

from teloce.compiler.compiler import compile_file
from teloce.project.scanner import ProjectScanner


def benchmark_project(root: str | Path, iterations: int = 1) -> dict[str, Any]:
    """Compile every project component repeatedly and return measurements."""
    root_path = Path(root).resolve()
    files = ProjectScanner().scan(root_path)
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    tracemalloc.start()
    started = time.perf_counter()
    failures: list[dict[str, str]] = []
    compiled = 0
    for _ in range(iterations):
        for path in files:
            result = compile_file(path, source_maps=False)
            if result.get("success"):
                compiled += 1
            else:
                failures.append({"file": str(path), "diagnostics": str(result.get("diagnostics"))})
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "root": str(root_path),
        "files": len(files),
        "iterations": iterations,
        "compiled": compiled,
        "failed": len(failures),
        "failures": failures,
        "seconds": elapsed,
        "milliseconds_per_file": (elapsed * 1000 / compiled) if compiled else 0,
        "files_per_second": (compiled / elapsed) if elapsed else 0,
        "peak_memory_bytes": peak,
    }


def benchmark_command(args: Any) -> int:
    result = benchmark_project(args.root, args.iterations)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Teloce Benchmark")
        print(f"Files: {result['files']}  Iterations: {result['iterations']}")
        print(f"Compiled: {result['compiled']}  Failed: {result['failed']}")
        print(f"Time: {result['seconds']:.4f}s ({result['milliseconds_per_file']:.3f} ms/file)")
        print(f"Throughput: {result['files_per_second']:.2f} files/s")
        print(f"Peak memory: {result['peak_memory_bytes']} bytes")
        for failure in result["failures"]:
            print(f"ERROR {failure['file']}: {failure['diagnostics']}")
    return 1 if result["failed"] else 0
