"""
File watcher - watches for file changes.

Monitors files and directories for changes during development.
"""

import os
import time
import fnmatch
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, Set
from dataclasses import dataclass
from enum import Enum, auto


class WatchEventType(Enum):
    """Types of watch events."""
    ADDED = auto()
    MODIFIED = auto()
    DELETED = auto()
    MOVED = auto()


@dataclass
class WatchEvent:
    """A file watch event."""
    type: WatchEventType
    path: str
    old_path: Optional[str] = None


class FileWatcher:
    """
    Watches files and directories for changes.
    
    Monitors .vel files and triggers rebuilds on changes.
    """
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        self.options = options or {}
        self.watch_paths: List[Path] = []
        self.ignore_patterns: List[str] = [
            'node_modules',
            '.git',
            '__pycache__',
            'dist',
            'build',
            '.venv',
            'venv',
            '*.pyc',
        ]
        self.handlers: List[Callable] = []
        self._running = False
        self._file_hashes: Dict[str, str] = {}
        self._last_event_times: Dict[str, float] = {}
        self._pending_events: Dict[str, WatchEvent] = {}
        self._debounce_delay = self.options.get('debounce', 300) / 1000.0
        self.watch_extensions = set(self.options.get('extensions', {'.vel', '.html', '.css', '.js', '.json'}))
    
    def add_path(self, path: str | Path) -> None:
        """
        Add a path to watch.
        
        Args:
            path: The path to watch.
        """
        self.watch_paths.append(Path(path))
    
    def add_ignore_pattern(self, pattern: str) -> None:
        """Add an ignore pattern."""
        self.ignore_patterns.append(pattern)
    
    def on_change(self, handler: Callable) -> None:
        """Register a change handler."""
        self.handlers.append(handler)
    
    def start(self) -> None:
        """Start watching for changes."""
        self._running = True
        self._file_hashes = self._get_file_hashes()
        
        while self._running:
            time.sleep(0.5)
            self._check_for_changes()
    
    def stop(self) -> None:
        """Stop watching."""
        self._running = False
    
    def _check_for_changes(self) -> None:
        """Check for file changes."""
        current_hashes = self._get_file_hashes()
        
        # Check for added/modified files
        for path, hash_val in current_hashes.items():
            if path not in self._file_hashes:
                self._trigger_event(WatchEventType.ADDED, path)
            elif self._file_hashes[path] != hash_val:
                self._trigger_event(WatchEventType.MODIFIED, path)
        
        # Check for deleted files
        for path in self._file_hashes:
            if path not in current_hashes:
                self._trigger_event(WatchEventType.DELETED, path)
        
        self._file_hashes = current_hashes
        now = time.time()
        for path, event in list(self._pending_events.items()):
            if now - self._last_event_times.get(path, now) >= self._debounce_delay:
                self._pending_events.pop(path, None)
                for handler in self.handlers:
                    handler(event)
    
    def _get_file_hashes(self) -> Dict[str, str]:
        """Get hashes of all watched files."""
        import hashlib
        
        hashes = {}
        
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
            
            if watch_path.is_dir():
                for file_path in watch_path.rglob('*'):
                    if file_path.is_file() and self._should_watch(file_path):
                        hashes[str(file_path)] = self._hash_file(file_path)
            else:
                if self._should_watch(watch_path):
                    hashes[str(watch_path)] = self._hash_file(watch_path)
        
        return hashes
    
    def _hash_file(self, file_path: Path) -> str:
        """Get the hash of a file."""
        import hashlib
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ''
    
    def _should_watch(self, file_path: Path) -> bool:
        """Check if a file should be watched."""
        # Check ignore patterns
        str_path = str(file_path)
        path_parts = set(file_path.parts)
        for pattern in self.ignore_patterns:
            if pattern in path_parts or fnmatch.fnmatch(file_path.name, pattern) or fnmatch.fnmatch(str_path, pattern):
                return False
        
        # Check extension
        if file_path.suffix.lower() in self.watch_extensions:
            return True
        
        return False
    
    def _trigger_event(self, event_type: WatchEventType, path: str) -> None:
        """Trigger a watch event."""
        event = WatchEvent(type=event_type, path=path)
        
        # Debounce per path, so a burst of edits does not lose unrelated files.
        current_time = time.time()
        last_time = self._last_event_times.get(path)
        if last_time is not None and current_time - last_time < self._debounce_delay:
            self._pending_events[path] = event
            self._last_event_times[path] = current_time
            return

        self._last_event_times[path] = current_time
        self._pending_events.pop(path, None)
        
        for handler in self.handlers:
            handler(event)
