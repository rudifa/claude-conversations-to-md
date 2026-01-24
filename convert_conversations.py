#! python

import json
import os
import re
import argparse


def sanitize_filename(filename):
    """Sanitizes a string to be used as a valid filename."""
    return re.sub(r'[^\w\d\s-]', '', filename).strip().replace(' ', '_')


def json_to_markdown(json_file_path, output_dir):
    """
    Parses a JSON file of conversations and converts each conversation
    into a separate Markdown file.
    """
    if not os.path.exists(output_dir):
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

        if not messages:
            print(f"Skipping conversation '{title}' as it has no messages.")
            continue

        filename = sanitize_filename(title)
        md_filename = os.path.join(output_dir, f"{filename}.md")

        if not title and not any(message.get('text', '').strip() for message in messages):
            print(
                f"Skipping conversation '{title}' as it has no title and no messages.")
            continue

        with open(md_filename, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# {title}\n\n")

            for message in messages:
                sender = message.get('sender', 'Unknown')
                text = message.get('text', '').strip()

                # Apply pattern modification to the text
                text = check_and_modify_text(text)

                if sender == 'human':
                    md_file.write(f"**You:**\n\n")
                else:  # assistant
                    md_file.write(f"**Assistant:**\n\n")

                md_file.write(f"{text}\n\n---\n\n")

        print(
            f"Successfully created Markdown for '{title}' at '{md_filename}'")


def check_and_modify_text(text):
    """
    Check if text contains the specific pattern and modify it by inserting
    a newline before the last newline in the pattern.
    The pattern matches a numbered list item.
    The fix ensures adds a newline before the first sublist item.
    """
    import re

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

    args = parser.parse_args()

    # Use the provided input file
    json_file = args.input_file
    markdown_output_directory = 'markdown_conversations'

    # Step 1: Convert JSON to Markdown
    json_to_markdown(json_file, markdown_output_directory)

    print("\nScript finished.")
