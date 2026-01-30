#! python

import json
import argparse
import re
from typing import List, Optional

def filter_conversations_by_uuid(input_file: str, output_file: str, uuids_to_keep: List[str]) -> None:
    """
    Loads conversations from a JSON file, filters them by a list of UUIDs,
    and saves the result to a new JSON file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_conversations = json.load(f)
    except FileNotFoundError:
        print(f"Error: The input file '{input_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'.")
        return

    # Use a set for efficient lookup
    uuid_set = set(uuids_to_keep)

    # Filter conversations based on the provided UUIDs
    filtered_conversations = [
        conv for conv in all_conversations if conv.get('uuid') in uuid_set
    ]

    if not filtered_conversations:
        print("Warning: No conversations found with the specified UUIDs.")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_conversations, f, indent=2, ensure_ascii=False)
        print(f"Successfully filtered {len(filtered_conversations)} conversations and saved to '{output_file}'.")
    except IOError as e:
        print(f"Error writing to file '{output_file}': {e}")


def filter_conversations_by_name(input_file: str, output_file: str, name_pattern: str) -> None:
    """
    Loads conversations from a JSON file, filters them by a name pattern (regex),
    and saves the result to a new JSON file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_conversations = json.load(f)
    except FileNotFoundError:
        print(f"Error: The input file '{input_file}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'.")
        return

    try:
        pattern = re.compile(name_pattern, re.IGNORECASE)
    except re.error as e:
        print(f"Error: Invalid regex pattern '{name_pattern}': {e}")
        return

    # Filter conversations based on the name pattern
    filtered_conversations = [
        conv for conv in all_conversations
        if pattern.search(conv.get('name', ''))
    ]

    if not filtered_conversations:
        print("Warning: No conversations found matching the pattern.")
        return

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_conversations, f, indent=2, ensure_ascii=False)
        print(f"Successfully filtered {len(filtered_conversations)} conversations and saved to '{output_file}'.")
    except IOError as e:
        print(f"Error writing to file '{output_file}': {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Filter Claude conversations by UUID or name pattern',
        prog='filter_conversations.py'
    )
    parser.add_argument(
        'input_file',
        help='Path to the input JSON file containing conversations'
    )
    parser.add_argument(
        'output_file',
        help='Path to the output JSON file'
    )

    # Create a mutually exclusive group for filtering options
    filter_group = parser.add_mutually_exclusive_group(required=True)
    filter_group.add_argument(
        '--uuids',
        nargs='+',
        help='Filter by UUIDs (space-separated list)'
    )
    filter_group.add_argument(
        '--name-pattern',
        help='Filter by name using regex pattern (case-insensitive)'
    )

    args = parser.parse_args()

    if args.uuids:
        filter_conversations_by_uuid(args.input_file, args.output_file, args.uuids)
    elif args.name_pattern:
        filter_conversations_by_name(args.input_file, args.output_file, args.name_pattern)
