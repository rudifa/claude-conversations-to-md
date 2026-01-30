#! python

import json
import os
import re
import argparse
from typing import List, Dict, Any


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitizes a string to be used as a valid filename.

    Args:
        filename: The string to sanitize
        max_length: Maximum length of the resulting filename (default: 100)

    Returns:
        A sanitized filename safe for use on most filesystems
    """
    clean = re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')
    return clean[:max_length]


def _should_skip_conversation(title: str, messages: List[Dict[str, Any]]) -> bool:
    """Check if a conversation should be skipped."""
    if not messages:
        print(f"Skipping conversation '{title}' as it has no messages.")
        return True

    if not title and not any(message.get('text', '').strip() for message in messages):
        print(f"Skipping conversation '{title}' as it has no title and no messages.")
        return True

    return False


def _handle_existing_file(md_filename: str, title: str, overwrite: bool, dry_run: bool) -> bool:
    """
    Handle existing file logic.
    Returns True if processing should continue, False if should skip.
    """
    if not os.path.exists(md_filename):
        return True

    if not overwrite:
        if dry_run:
            print(f"[DRY RUN] Would skip existing file: {md_filename}")
        else:
            print(f"Skipping '{title}' - file already exists: {md_filename}")
        return False

    if dry_run:
        print(f"[DRY RUN] Would overwrite existing file: {md_filename}")

    return True


def _write_markdown_content(md_file, title: str, messages: List[Dict[str, Any]]) -> None:
    """Write the markdown content for a conversation."""
    md_file.write(f"# {title}\n\n")

    for message in messages:
        sender = message.get('sender', 'Unknown')
        text = message.get('text', '').strip()

        # Apply pattern modification to the text
        text = check_and_modify_text(text)

        if sender == 'human':
            md_file.write("**You:**\n\n")
        else:  # assistant
            md_file.write("**Assistant:**\n\n")

        md_file.write(f"{text}\n\n---\n\n")


def json_to_markdown(json_file_path: str, output_dir: str, overwrite: bool = False, dry_run: bool = False) -> None:
    """
    Parses a JSON file of conversations and converts each conversation
    into a separate Markdown file.

    Args:
        json_file_path: Path to the input JSON file
        output_dir: Directory where Markdown files will be saved
        overwrite: If True, overwrite existing files; if False, skip them
        dry_run: If True, show what would be done without writing files
    """
    if dry_run:
        print(f"[DRY RUN] Would create output directory: {output_dir}")
    elif not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(
            f"Error: Could not decode JSON from '{json_file_path}'. Please check the file format.")
        return

    for i, conversation in enumerate(conversations):
        title = conversation.get('name', f'conversation_{i+1}')
        messages = conversation.get('chat_messages', [])

        if _should_skip_conversation(title, messages):
            continue

        filename = sanitize_filename(title)
        md_filename = os.path.join(output_dir, f"{filename}.md")

        if not _handle_existing_file(md_filename, title, overwrite, dry_run):
            continue

        if dry_run:
            print(f"[DRY RUN] Would create: {md_filename}")
            continue

        with open(md_filename, 'w', encoding='utf-8') as md_file:
            _write_markdown_content(md_file, title, messages)

        print(f"Successfully created Markdown for '{title}' at '{md_filename}'")


def check_and_modify_text(text: str) -> str:
    """
    Check if text contains the specific pattern and modify it by inserting
    a newline before the last newline in the pattern.

    The pattern matches a numbered list item followed by a bullet point:
        **1. "Some Title"**
        - Bullet item

    This fix adds an extra newline to ensure proper Markdown rendering:
        **1. "Some Title"**

        - Bullet item

    This prevents the bullet point from being visually merged with the
    numbered list item header in Markdown renderers.
    """
    # Regex pattern: \n**\d+. "any chars except quotes"**\n-
    pattern = r'\n\*\*(\d+)\. \"([^"]+)\"\*\*\n- '

    # Count matches first for reporting
    matches = re.findall(pattern, text)
    if matches:
        # Use re.sub to replace all occurrences
        # The replacement function preserves the number and content
        def replacement(match):
            number = match.group(1)
            content = match.group(2)
            return f'\n**{number}. "{content}"**\n\n- '

        result = re.sub(pattern, replacement, text)
        return result
    else:
        return text


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Convert Claude conversations JSON file to Markdown format',
        prog='convert_conversations.py'
    )
    parser.add_argument(
        'input_file',
        help='Path to the JSON file containing conversations'
    )
    parser.add_argument(
        '-o', '--output',
        default='markdown_conversations',
        help='Output directory for Markdown files (default: markdown_conversations)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing Markdown files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without writing files'
    )

    args = parser.parse_args()

    # Convert JSON to Markdown
    json_to_markdown(
        args.input_file,
        args.output,
        overwrite=args.overwrite,
        dry_run=args.dry_run
    )

    print("\nScript finished.")
