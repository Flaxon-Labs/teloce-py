"""
Dev command - starts the development server.

Starts a development server with hot reload and HMR.
"""

import sys
from pathlib import Path
from typing import Any, Dict

from teloce.project.discovery import ProjectDiscovery
from teloce.project.configuration import ProjectConfiguration
from teloce.watcher.watcher import FileWatcher, WatchEventType
from teloce.build.builder import Builder
from teloce.cli.server import start_dev_server


def dev_command(args: Any) -> int:
    """
    Start the development server.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        Exit code.
    """
    print("🐛 Teloce Development Server")
    print("=" * 40)
    
    # Discover project
    discovery = ProjectDiscovery()
    project_info = discovery.discover()
    
    print(f"📁 Project: {discovery.get_project_name()}")
    print(f"📂 Root: {discovery.root_dir}")
    
    # Load configuration
    config = ProjectConfiguration()
    config.load()
    
    # Get dev server config
    server_config = config.get_server_config()
    port = args.port or server_config.get('port', 5173)
    host = args.host or server_config.get('host', 'localhost')
    hmr = not args.no_hmr and server_config.get('hmr', True)
    
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔄 HMR: {'Enabled' if hmr else 'Disabled'}")
    print()
    
    # Build initially
    print("📦 Building project...")
    builder = Builder({'dev': True, 'source_maps': True, 'clean': True})
    builder.build(discovery.root_dir, discovery.root_dir / 'dist')
    server = start_dev_server(host, port, discovery.root_dir / 'dist', proxy_target=getattr(args, 'proxy', None), hmr=hmr)
    
    # Set up watcher
    if hmr:
        print("👀 Watching for changes...")
        watcher = FileWatcher()
        
        # Watch .vel files
        js_dir = discovery.get_js_dir()
        if js_dir:
            watcher.add_path(js_dir)
        
        # Watch templates
        templates_dir = discovery.get_templates_dir()
        if templates_dir:
            watcher.add_path(templates_dir)
        
        def on_change(event):
            print(f"📝 File changed: {event.path}")
            builder.build(discovery.root_dir, discovery.root_dir / 'dist')
            server.notify_reload()
            print("✅ Rebuild complete")
        
        watcher.on_change(on_change)
    
    print()
    print("✅ Development server started!")
    print(f"📍 http://{host}:{port}")
    print()
    print("Press Ctrl+C to stop")
    
    try:
        # Start watcher
        if hmr:
            watcher.start()
        else:
            # Keep running
            import time
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
        print("\n🛑 Server stopped")
    
    return 0
