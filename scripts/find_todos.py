#!/usr/bin/env python3
"""
Find TODO comments in the Universal Agent codebase.

This script scans the codebase for TODO comments and generates a report.
"""
import os
import re
import sys
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple


def find_todos_in_file(file_path: str) -> List[Tuple[int, str]]:
    """
    Find TODO comments in a file.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        List of tuples containing line number and TODO comment
    """
    todos = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            # Match any TODO comment (case insensitive)
            match = re.search(r'#\s*TODO\s*:?\s*(.*)|//\s*TODO\s*:?\s*(.*)|/\*\s*TODO\s*:?\s*(.*)\*/|<!--\s*TODO\s*:?\s*(.*)-->', line, re.IGNORECASE)
            if match:
                # Get the content of the TODO comment (first non-None group)
                todo_content = next((group for group in match.groups() if group is not None), "").strip()
                todos.append((i, todo_content))
    
    return todos


def find_todos_in_directory(directory: str, exclude_dirs: List[str] = None) -> Dict[str, List[Tuple[int, str]]]:
    """
    Find TODO comments in all files in a directory.
    
    Args:
        directory: Directory to check
        exclude_dirs: List of directories to exclude
        
    Returns:
        Dictionary of file paths and their TODO comments
    """
    if exclude_dirs is None:
        exclude_dirs = []
    
    # Add common directories to exclude
    exclude_dirs.extend(['.git', '.vscode', 'venv', 'node_modules', '__pycache__', '.env'])
    
    todos_by_file = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Only check files with these extensions
            extensions = ('.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.txt', '.html', '.css', '.json', '.yaml', '.yml')
            if not file.endswith(extensions):
                continue
            
            file_path = os.path.join(root, file)
            todos = find_todos_in_file(file_path)
            
            if todos:
                # Use relative path from the current directory
                rel_path = os.path.relpath(file_path, directory)
                todos_by_file[rel_path] = todos
    
    return todos_by_file


def create_report(todos_by_file: Dict[str, List[Tuple[int, str]]]) -> str:
    """
    Create a report of TODO comments.
    
    Args:
        todos_by_file: Dictionary of file paths and their TODO comments
        
    Returns:
        Report as string
    """
    if not todos_by_file:
        return "No TODO comments found."
    
    total_todos = sum(len(todos) for todos in todos_by_file.values())
    
    report = f"# TODO Comments Report\n\n"
    report += f"Found {total_todos} TODO comments in {len(todos_by_file)} files.\n\n"
    
    # Group by directory
    directories = defaultdict(list)
    for file_path, todos in sorted(todos_by_file.items()):
        directory = os.path.dirname(file_path) or '.'
        directories[directory].append((file_path, todos))
    
    # Generate report by directory
    for directory, files in sorted(directories.items()):
        report += f"## {directory}\n\n"
        
        for file_path, todos in sorted(files):
            report += f"### {os.path.basename(file_path)}\n\n"
            
            for line_num, todo in todos:
                report += f"- Line {line_num}: `{todo}`\n"
            
            report += "\n"
    
    return report


def create_issue_format(todos_by_file: Dict[str, List[Tuple[int, str]]]) -> str:
    """
    Create a TODO report in issue format.
    
    Args:
        todos_by_file: Dictionary of file paths and their TODO comments
        
    Returns:
        Issues in markdown format
    """
    if not todos_by_file:
        return "No TODO comments found."
    
    issues = []
    
    for file_path, todos in sorted(todos_by_file.items()):
        for line_num, todo in todos:
            issue_title = todo[:50] + ('...' if len(todo) > 50 else '')
            issue_body = f"Found in {file_path} at line {line_num}:\n\n```\n{todo}\n```"
            
            issues.append(f"## TODO: {issue_title}\n\n{issue_body}\n\n---\n")
    
    return "\n".join(issues)


def main():
    """Main function to find TODO comments."""
    parser = argparse.ArgumentParser(description='Find TODO comments in codebase')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to check (default: current directory)')
    parser.add_argument('--exclude', '-e', nargs='+', default=[], help='Directories to exclude')
    parser.add_argument('--output', '-o', help='Output file (default: print to stdout)')
    parser.add_argument('--issues', '-i', action='store_true', help='Format output as issues')
    args = parser.parse_args()
    
    print(f"Scanning directory: {args.directory}")
    todos_by_file = find_todos_in_directory(args.directory, args.exclude)
    
    if args.issues:
        report = create_issue_format(todos_by_file)
        output_file = args.output or "todo_issues.md"
    else:
        report = create_report(todos_by_file)
        output_file = args.output or "todo_report.md"
    
    if args.output:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report written to {output_file}")
    else:
        print(report)


if __name__ == '__main__':
    main()
