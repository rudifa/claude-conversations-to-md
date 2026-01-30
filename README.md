# Convert Claude conversation JSON files to Markdown format

## Input file

The scripts process a JSON file obtained from Claude data export.

A sample file can be found here:

```
sample_conversations/conversations.json
```

## How to obtain the input file

In the desktop Claude app or in the web page, go to `Settings -> Data Export` and request a data export.
Once the export is ready, you will receive an email with a link to a zip file.
Download the file and unzip it.
The unzipped folder will contain a file named `conversations.json` which is the input file for these scripts.

## Filter conversations (optional)

To filter conversations by UUID or name pattern before converting:

```bash
# Filter by UUIDs
python filter_conversations.py input.json output.json --uuids <uuid1> <uuid2> ...

# Filter by name pattern (regex)
python filter_conversations.py input.json output.json --name-pattern "Python"
```

Use `python filter_conversations.py --help` for more options.

## Convert conversations

To convert conversations to Markdown format:

```bash
python convert_conversations.py path/to/conversations.json
```

This creates a `markdown_conversations` directory with one Markdown file per conversation. By default, existing files are not overwritten.

Use `python convert_conversations.py --help` for more options including custom output directory, overwrite mode, and dry-run.

## Running tests

```bash
# Run directly
./test_filter_conversations.py
./test_convert_conversations.py

# Or with pytest
python -m pytest test_filter_conversations.py test_convert_conversations.py -v
```

## Limitations

This version of the scripts handles basic conversations between "You" and "Assistant" and ignores any attachments or metadata.
