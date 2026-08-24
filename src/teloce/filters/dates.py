"""
Date filters for Teloce templates.

Provides filters for date manipulation and formatting.
"""

from typing import Any, Optional
from datetime import datetime, timedelta


class DateFilters:
    """Date filters for templates."""
    
    @staticmethod
    def date_format(value: Any, format_str: str = '%Y-%m-%d') -> str:
        """Format a date."""
        if value is None or value == '':
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        if isinstance(value, datetime):
            return value.strftime(format_str)
        return str(value)
    
    @staticmethod
    def time_ago(value: Any) -> str:
        """Get relative time ago."""
        if value is None or value == '':
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        if isinstance(value, datetime):
            now = datetime.now()
            diff = now - value
            
            seconds = diff.total_seconds()
            if seconds < 60:
                return 'just now'
            if seconds < 3600:
                minutes = int(seconds // 60)
                return f'{minutes}m ago'
            if seconds < 86400:
                hours = int(seconds // 3600)
                return f'{hours}h ago'
            if seconds < 604800:
                days = int(seconds // 86400)
                return f'{days}d ago'
            if seconds < 2592000:
                weeks = int(seconds // 604800)
                return f'{weeks}w ago'
            if seconds < 31536000:
                months = int(seconds // 2592000)
                return f'{months}mo ago'
            years = int(seconds // 31536000)
            return f'{years}y ago'
        return str(value)
    
    @staticmethod
    def date_from_iso(value: str) -> Optional[datetime]:
        """Parse a date from ISO format."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    
    @staticmethod
    def relative_time(value: Any) -> str:
        """Get relative time (past or future)."""
        if value is None or value == '':
            return ''
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        if isinstance(value, datetime):
            now = datetime.now()
            diff = now - value
            is_future = diff.total_seconds() < 0
            seconds = abs(diff.total_seconds())
            
            if seconds < 60:
                return 'just now' if not is_future else 'in a moment'
            if seconds < 3600:
                minutes = int(seconds // 60)
                if is_future:
                    return f'in {minutes}m'
                return f'{minutes}m ago'
            if seconds < 86400:
                hours = int(seconds // 3600)
                if is_future:
                    return f'in {hours}h'
                return f'{hours}h ago'
            if seconds < 604800:
                days = int(seconds // 86400)
                if is_future:
                    return f'in {days}d'
                return f'{days}d ago'
            if seconds < 2592000:
                weeks = int(seconds // 604800)
                if is_future:
                    return f'in {weeks}w'
                return f'{weeks}w ago'
            if seconds < 31536000:
                months = int(seconds // 2592000)
                if is_future:
                    return f'in {months}mo'
                return f'{months}mo ago'
            years = int(seconds // 31536000)
            if is_future:
                return f'in {years}y'
            return f'{years}y ago'
        return str(value)
    
    @staticmethod
    def get_all() -> dict:
        """Get all date filters."""
        return {
            'dateFormat': DateFilters.date_format,
            'timeAgo': DateFilters.time_ago,
            'dateFromISO': DateFilters.date_from_iso,
            'relativeTime': DateFilters.relative_time,
        }
    
    @staticmethod
    def get_description(name: str) -> str:
        """Get filter description."""
        descriptions = {
            'dateFormat': 'Format a date',
            'timeAgo': 'Get relative time ago',
            'dateFromISO': 'Parse a date from ISO format',
            'relativeTime': 'Get relative time (past or future)',
        }
        return descriptions.get(name, '')