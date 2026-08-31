"""
Lint command - lints Teloce templates.

Lints .vel files for issues and potential problems.
"""

import re
import copy
from pathlib import Path
from typing import Any, List, Dict

from teloce.project.discovery import ProjectDiscovery
from teloce.sfc.parser import SFCParser


def lint_command(args: Any) -> int:
    """
    Lint Teloce templates.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        Exit code.
    """
    print("📋 Teloce Lint")
    print("=" * 40)
    
    # Discover project
    discovery = ProjectDiscovery()
    discovery.discover()
    
    print(f"📁 Project: {discovery.get_project_name()}")
    
    # Find .vel files
    js_dir = discovery.get_js_dir()
    if not js_dir:
        print("❌ No JavaScript directory found")
        return 1
    
    vel_files = list(js_dir.rglob('*.vel'))
    print(f"📄 Found {len(vel_files)} .vel files")
    print()
    
    issues = []
    
    for vel_file in vel_files:
        file_issues = lint_file(vel_file, args)
        if file_issues:
            issues.extend(file_issues)
    
    if issues and args.fix:
        # Apply edits once per file, then run the linter again. This prevents
        # the CLI from claiming a suggestion was fixed when nothing changed.
        files = {Path(issue['file']) for issue in issues if issue.get('fix')}
        fixed = sum(1 for path in files if apply_lint_fixes(path, issues))
        verify_args = copy.copy(args)
        verify_args.fix = False
        remaining = []
        for vel_file in vel_files:
            remaining.extend(lint_file(vel_file, verify_args))
        if not remaining:
            print(f"✅ Fixed {fixed} file(s); no issues remain.")
            return 0
        issues = remaining
        print(f"⚠️  Applied fixes to {fixed} file(s); {len(issues)} issue(s) still require attention:")

    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   {issue['file']}:{issue.get('line', '?')} - {issue['message']}")
            if args.fix and issue.get('fix'):
                print(f"      💡 {issue['fix']}")
        return 1
    
    print("✅ No issues found!")
    return 0


def apply_lint_fixes(file_path: Path, issues: List[Dict[str, Any]]) -> bool:
    """Apply conservative, syntax-preserving fixes only."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except OSError:
        return False

    updated = content
    issue_messages = {
        issue.get('message', '') for issue in issues
        if issue.get('file') == str(file_path)
    }
    if 'Missing <script> section' in issue_messages and not re.search(
        r'<script(?:\s[^>]*)?>', updated, re.IGNORECASE
    ):
        updated = updated.rstrip() + "\n\n<script>\nexport default {};\n</script>\n"

    if 'For loop missing "key" attribute' in issue_messages:
        def add_index_key(match: re.Match[str]) -> str:
            tag = match.group(0)
            return tag if re.search(r'(?:^|\s)(?::|v-bind:)?key\s*=', tag, re.IGNORECASE) else tag[:-1] + ' key="index">'
        updated = re.sub(r'<for\b[^>]*>', add_index_key, updated, flags=re.IGNORECASE)

        def add_v_for_key(match: re.Match[str]) -> str:
            tag = match.group(0)
            if re.search(r'(?:^|\s)(?::|v-bind:)?key\s*=', tag, re.IGNORECASE):
                return tag
            return tag[:-1] + ' :key="index">'

        updated = re.sub(
            r'<(?!for\b)[A-Za-z][^>]*\bv-for\s*=\s*(?:"[^"]*"|\'[^\']*\')[^>]*>',
            add_v_for_key,
            updated,
            flags=re.IGNORECASE,
        )

    if any(message.startswith('Found ') and 'empty interpolations' in message for message in issue_messages):
        updated = re.sub(r'\{\{\s*\}\}', '', updated)

    if updated == content:
        return False
    file_path.write_text(updated, encoding='utf-8')
    return True


def lint_file(file_path: Path, args: Any) -> List[Dict[str, Any]]:
    """
    Lint a single .vel file.
    
    Args:
        file_path: The .vel file path.
        args: Command-line arguments.
        
    Returns:
        A list of issues.
    """
    issues = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return [{'file': str(file_path), 'message': 'Failed to read file'}]
    
    # Check for empty file
    if not content.strip():
        issues.append({
            'file': str(file_path),
            'line': 1,
            'message': 'File is empty',
        })
        return issues
    
    # Use the real SFC parser so lint and build agree on valid syntax.
    parser = SFCParser()
    if parser.parse(content, str(file_path)) is None:
        for message in parser.errors:
            issues.append({'file': str(file_path), 'message': message})
        return issues
    
    # Check for script section
    if not re.search(r'<script(?:\s[^>]*)?>', content, re.IGNORECASE):
        issues.append({
            'file': str(file_path),
            'line': 1,
            'message': 'Missing <script> section',
            'fix': 'Add a <script> section to your .vel file' if args.fix else None,
        })
    
    # Check for empty template
    if '<template></template>' in content:
        issues.append({
            'file': str(file_path),
            'line': content.count('\n', 0, content.find('<template>')) + 1,
            'message': 'Empty <template> section',
        })
    
    # Check for unclosed tags in template
    template_match = re.search(r'<template>([\s\S]*?)</template>', content)
    if template_match:
        template = template_match.group(1)
        
        # Check for for loops without key
        for_match = re.findall(r'<for\b[^>]*>', template, flags=re.IGNORECASE)
        for_match.extend(
            re.findall(
                r'<(?!for\b)[A-Za-z][^>]*\bv-for\s*=\s*(?:"[^"]*"|\'[^\']*\')[^>]*>',
                template,
                flags=re.IGNORECASE,
            )
        )
        for tag in for_match:
            if not re.search(r'(?:^|\s)(?::|v-bind:)?key\s*=', tag, re.IGNORECASE):
                line = content.count('\n', 0, content.find(tag)) + 1
                issues.append({
                    'file': str(file_path),
                    'line': line,
                    'message': 'For loop missing "key" attribute',
                    'fix': 'Add key="index" attribute to for loop' if args.fix else None,
                })
        
        # Check for empty interpolations
        interp_match = re.findall(r'\{\{\s*\}\}', template)
        if interp_match:
            issues.append({
                'file': str(file_path),
                'line': 1,
                'message': f'Found {len(interp_match)} empty interpolations',
                'fix': 'Add a variable inside {{ }}' if args.fix else None,
            })
    
    return issues
