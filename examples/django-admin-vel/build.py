import argparse
from pathlib import Path

from teloce.build import build_project


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the Django admin dashboard assets.")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Keep readable output and source maps for local browser debugging.",
    )
    args = parser.parse_args()
    project = Path(__file__).resolve().parent
    result = build_project(
        project,
        options={
            "static_dir": "static",
            "dev": args.dev,
            "source_maps": args.dev,
            "minify": not args.dev,
            "shared_runtime": True,
            "tree_shake": True,
        },
    )
    if result["failed"]:
        raise SystemExit(f"Build failed: {result['errors']}")
    print(f"Compiled {result['compiled']} component(s); runtime: {result.get('runtime', 'embedded')}")
