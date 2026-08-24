"""
Debug command - opens the debugger dashboard.

Opens the human-friendly debugger dashboard.
"""

import sys
import webbrowser
from typing import Any

from teloce.project.discovery import ProjectDiscovery
from teloce.project.configuration import ProjectConfiguration
from teloce.debug.dashboard import DebuggerDashboard


def debug_command(args: Any) -> int:
    """
    Open the debugger dashboard.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        Exit code.
    """
    print("🐛 Teloce Debugger")
    print("=" * 40)
    
    # Discover project
    discovery = ProjectDiscovery()
    project_info = discovery.discover()
    
    print(f"📁 Project: {discovery.get_project_name()}")
    
    # Load configuration
    config = ProjectConfiguration()
    config.load()
    
    # Get debugger config
    debug_config = config.get('debugger', {})
    port = args.port or debug_config.get('port', 9000)
    host = args.host or debug_config.get('host', 'localhost')
    open_browser = not args.no_open and debug_config.get('open', True)
    
    dashboard = DebuggerDashboard(discovery.root_dir, host=host, port=port)
    dashboard.start()
    url = dashboard.url
    
    print(f"📍 Debugger URL: {url}")
    print()
    
    # Open browser
    if open_browser:
        print("🌐 Opening browser...")
        webbrowser.open(url)
    
    print()
    print("🔧 Debugger features:")
    print("   - Project and environment information")
    print("   - Discovered .vel component list")
    print("   - Live compiler diagnostics")
    print("   - Error and warning counts")
    print("   - Refreshable local dashboard")
    print()
    print("Press Ctrl+C to stop")
    
    try:
        # Keep the local dashboard alive until interrupted.
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dashboard.close()
        print("\n🛑 Debugger stopped")
    
    return 0
