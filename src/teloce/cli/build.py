"""
Build command - builds for production.

Builds the project for production deployment.
"""

import sys
from pathlib import Path
from typing import Any

from teloce.project.discovery import ProjectDiscovery
from teloce.project.configuration import ProjectConfiguration
from teloce.build.builder import Builder


def build_command(args: Any) -> int:
    """
    Build for production.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        Exit code.
    """
    print("📦 Teloce Build")
    print("=" * 40)
    
    # Discover project
    discovery = ProjectDiscovery()
    project_info = discovery.discover()
    
    print(f"📁 Project: {discovery.get_project_name()}")
    
    # Load configuration
    config = ProjectConfiguration()
    config.load()
    
    # Get build config
    build_config = config.get_build_config()
    out_dir = args.out_dir or build_config.get('out_dir', 'dist')
    minify = args.minify or (not args.no_minify and build_config.get('minify', False))
    source_map = args.source_map or build_config.get('source_maps', False)
    clean = not getattr(args, 'no_clean', False) and build_config.get('clean', True)
    
    print(f"📂 Output: {out_dir}")
    print(f"⚡ Minify: {'Yes' if minify else 'No'}")
    print(f"🗺️  Source Maps: {'Yes' if source_map else 'No'}")
    print()
    
    # Build
    builder = Builder({
        'minify': minify,
        'source_maps': source_map,
        'dev': False,
        'clean': clean,
        'hash_assets': getattr(args, 'hash_assets', False),
        'bundle': getattr(args, 'bundle', False),
        'bundle_entry': getattr(args, 'entry', None),
    })
    
    result = builder.build(discovery.root_dir, out_dir)
    
    # Print results
    print("✅ Build complete!")
    print()
    print(f"📊 Statistics:")
    print(f"   Total files: {result['total']}")
    print(f"   Compiled: {result['compiled']}")
    print(f"   Failed: {result['failed']}")
    print(f"   Assets copied: {result.get('assets_copied', 0)}")
    print(f"   Duration: {result['duration']:.2f}s")
    
    if result['errors']:
        print()
        print("❌ Errors:")
        for error in result['errors']:
            print(f"   {error['file']}: {error['error']}")
        return 1
    
    return 0
