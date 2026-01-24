import json

def filter_conversations_by_uuid(input_file, output_file, uuids_to_keep):
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


if __name__ == '__main__':
    input_json_file = 'sample_conversations/conversations.json'
    output_json_file = 'sample_conversations/conversations-2.json'
    
    # The UUIDs you want to extract
    target_uuids = [
        "0921dcc8-826a-400e-b626-2899af1f4298",
        "8e4076a8-19e7-4c4d-9947-9f1164cbaadd"
    ]

    filter_conversations_by_uuid(input_json_file, output_json_file, target_uuids)