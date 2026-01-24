# Convert Claude conversation JSON files to Markdown format

## Input file

The script processes a JSON file obtained from Claude data export.

A sample file can be found here:

```
sample_conversations/conversations.json

```

## How to obtain the input file

In the dektop Claude app or in the web page, go to Settings -> Data Export and request a data export.
Once the export is ready, you will receive an email with a link to a zip file.
Download the file and unzip it.
The unzipped folder will contain a file named `conversations.json` which is the input file for this script.

## Convert conversations

To convert the conversations to Markdown format, run the following command:

```
convert_conversations.py path/to/conversations.json
```

The script will create a folder named `markdown_conversations` in the current directory, containing the converted Markdown files, one file per conversation.

## Limitations

This version of the script handles basic conversations between "You" and "Assistant" and ignores any attachments or metadata.
