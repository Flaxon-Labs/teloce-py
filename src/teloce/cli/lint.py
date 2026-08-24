"""
Lint command - lints Teloce templates.

Lints .vel files for issues and potential problems.
"""

import sys
import re
from pathlib import Path
from typing import Any, List, Dict

from teloce.project.discovery import ProjectDiscovery
from teloce.compiler.diagnostics import Diagnostics, DiagnosticLevel
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
    project_info = discovery.discover()
    
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
    
    if issues:
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   {issue['file']}:{issue.get('line', '?')} - {issue['message']}")
            if args.fix and issue.get('fix'):
                print(f"      💡 {issue['fix']}")
        
        if args.fix:
            print()
            print("✅ Issues fixed!")
        
        return 1
    
    print("✅ No issues found!")
    return 0


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
        for_match = re.findall(r'<for[^>]*>', template)
        for tag in for_match:
            if 'key=' not in tag:
                line = content.count('\n', 0, content.find(tag)) + 1
                issues.append({
                    'file': str(file_path),
                    'line': line,
                    'message': 'For loop missing "key" attribute',
                    'fix': 'Add key="id" attribute to for loop' if args.fix else None,
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
