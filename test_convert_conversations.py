#!/usr/bin/env python3

import unittest
import json
import os
import tempfile
import shutil
from convert_conversations import (
    sanitize_filename,
    check_and_modify_text,
    json_to_markdown,
    _should_skip_conversation,
    _handle_existing_file
)


class TestSanitizeFilename(unittest.TestCase):
    """Test cases for sanitize_filename function."""

    def test_basic_sanitization(self):
        """Test basic filename sanitization."""
        self.assertEqual(sanitize_filename("Hello World"), "Hello_World")

    def test_remove_special_characters(self):
        """Test removal of special characters."""
        self.assertEqual(sanitize_filename("Hello@World!"), "HelloWorld")
        self.assertEqual(sanitize_filename("Test/File\\Name"), "TestFileName")

    def test_preserve_hyphens(self):
        """Test that hyphens are preserved."""
        self.assertEqual(sanitize_filename("my-test-file"), "my-test-file")

    def test_strip_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        self.assertEqual(sanitize_filename("  spaced  "), "spaced")

    def test_max_length(self):
        """Test that filename is truncated to max_length."""
        long_name = "a" * 200
        result = sanitize_filename(long_name, max_length=50)
        self.assertEqual(len(result), 50)

    def test_empty_string(self):
        """Test empty string handling."""
        self.assertEqual(sanitize_filename(""), "")

    def test_unicode_removal(self):
        """Test that unicode characters are removed."""
        self.assertEqual(sanitize_filename("Hello🌍World"), "HelloWorld")


class TestCheckAndModifyText(unittest.TestCase):
    """Test cases for check_and_modify_text function."""

    def test_pattern_found_and_modified(self):
        """Test that the pattern is correctly identified and modified."""
        input_text = 'Some text\n**1. "Title Here"**\n- Item one'
        expected = 'Some text\n**1. "Title Here"**\n\n- Item one'
        result = check_and_modify_text(input_text)
        self.assertEqual(result, expected)

    def test_multiple_patterns(self):
        """Test modification of multiple patterns."""
        # Pattern requires a newline before it to match
        input_text = 'Text\n**1. "First"**\n- Item\n**2. "Second"**\n- Item'
        result = check_and_modify_text(input_text)
        # Should have two extra newlines added
        self.assertIn('**1. "First"**\n\n- ', result)
        self.assertIn('**2. "Second"**\n\n- ', result)

    def test_no_pattern_unchanged(self):
        """Test that text without pattern is unchanged."""
        input_text = "Just some regular text without the pattern"
        result = check_and_modify_text(input_text)
        self.assertEqual(result, input_text)

    def test_similar_but_different_pattern(self):
        """Test that similar patterns don't match."""
        input_text = '**1. Title without quotes**\n- Item'
        result = check_and_modify_text(input_text)
        self.assertEqual(result, input_text)


class TestHelperFunctions(unittest.TestCase):
    """Test cases for helper functions."""

    def test_should_skip_empty_messages(self):
        """Test skipping conversations with no messages."""
        self.assertTrue(_should_skip_conversation("Test", []))

    def test_should_skip_no_content(self):
        """Test skipping conversations with no title and no message content."""
        messages = [{"text": "  "}, {"text": ""}]
        self.assertTrue(_should_skip_conversation("", messages))

    def test_should_not_skip_valid(self):
        """Test not skipping valid conversations."""
        messages = [{"text": "Hello"}]
        self.assertFalse(_should_skip_conversation("Title", messages))

    def test_handle_existing_file_no_overwrite(self):
        """Test that existing files are skipped when overwrite is False."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_file = tf.name
        try:
            result = _handle_existing_file(temp_file, "Test", overwrite=False, dry_run=False)
            self.assertFalse(result)
        finally:
            os.unlink(temp_file)

    def test_handle_existing_file_with_overwrite(self):
        """Test that existing files are processed when overwrite is True."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_file = tf.name
        try:
            result = _handle_existing_file(temp_file, "Test", overwrite=True, dry_run=False)
            self.assertTrue(result)
        finally:
            os.unlink(temp_file)

    def test_handle_nonexistent_file(self):
        """Test that nonexistent files return True."""
        result = _handle_existing_file("/nonexistent/file.md", "Test", overwrite=False, dry_run=False)
        self.assertTrue(result)


class TestJsonToMarkdown(unittest.TestCase):
    """Test cases for json_to_markdown function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        self.input_file = os.path.join(self.test_dir, "input.json")

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.test_dir)

    def test_basic_conversion(self):
        """Test basic JSON to Markdown conversion."""
        conversations = [
            {
                "name": "Test Conversation",
                "chat_messages": [
                    {"sender": "human", "text": "Hello"},
                    {"sender": "assistant", "text": "Hi there"}
                ]
            }
        ]

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)

        json_to_markdown(self.input_file, self.output_dir)

        # Check output file exists
        output_file = os.path.join(self.output_dir, "Test_Conversation.md")
        self.assertTrue(os.path.exists(output_file))

        # Check content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("# Test Conversation", content)
        self.assertIn("**You:**", content)
        self.assertIn("Hello", content)
        self.assertIn("**Assistant:**", content)
        self.assertIn("Hi there", content)

    def test_skip_empty_conversations(self):
        """Test that empty conversations are skipped."""
        conversations = [
            {
                "name": "Empty",
                "chat_messages": []
            },
            {
                "name": "Valid",
                "chat_messages": [{"sender": "human", "text": "Hi"}]
            }
        ]

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)

        json_to_markdown(self.input_file, self.output_dir)

        # Only one file should be created
        files = os.listdir(self.output_dir)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], "Valid.md")

    def test_dry_run_no_files_created(self):
        """Test that dry-run mode doesn't create files."""
        conversations = [
            {
                "name": "Test",
                "chat_messages": [{"sender": "human", "text": "Hi"}]
            }
        ]

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)

        json_to_markdown(self.input_file, self.output_dir, dry_run=True)

        # No files should be created
        self.assertFalse(os.path.exists(self.output_dir))

    def test_overwrite_protection(self):
        """Test that existing files are not overwritten without overwrite flag."""
        conversations = [
            {
                "name": "Test",
                "chat_messages": [{"sender": "human", "text": "Hello"}]
            }
        ]

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)

        # First conversion
        json_to_markdown(self.input_file, self.output_dir)

        output_file = os.path.join(self.output_dir, "Test.md")

        # Modify the file
        with open(output_file, 'w') as f:
            f.write("Modified content")

        # Second conversion without overwrite
        json_to_markdown(self.input_file, self.output_dir, overwrite=False)

        # Content should still be modified
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Modified content")

    def test_overwrite_enabled(self):
        """Test that files are overwritten when overwrite=True."""
        conversations = [
            {
                "name": "Test",
                "chat_messages": [{"sender": "human", "text": "Hello"}]
            }
        ]

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)

        # First conversion
        json_to_markdown(self.input_file, self.output_dir)

        output_file = os.path.join(self.output_dir, "Test.md")

        # Modify the file
        with open(output_file, 'w') as f:
            f.write("Modified content")

        # Second conversion with overwrite
        json_to_markdown(self.input_file, self.output_dir, overwrite=True)

        # Content should be restored
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertIn("# Test", content)
        self.assertNotEqual(content, "Modified content")

    def test_missing_input_file(self):
        """Test handling of missing input file."""
        # Should not raise exception, just print error
        json_to_markdown("nonexistent.json", self.output_dir)
        # Output directory is created but should be empty
        self.assertTrue(os.path.exists(self.output_dir))
        self.assertEqual(len(os.listdir(self.output_dir)), 0)

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        with open(self.input_file, 'w') as f:
            f.write("not valid json{")

        json_to_markdown(self.input_file, self.output_dir)
        # Output directory is created but should be empty
        self.assertTrue(os.path.exists(self.output_dir))
        self.assertEqual(len(os.listdir(self.output_dir)), 0)

    def test_filename_sanitization_in_conversion(self):
        """Test that special characters in conversation names are sanitized."""
        conversations = [
            {
                "name": "Test/File\\Name*?",
                "chat_messages": [{"sender": "human", "text": "Hi"}]
            }
        ]

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)

        json_to_markdown(self.input_file, self.output_dir)

        # Check that file was created with sanitized name
        files = os.listdir(self.output_dir)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], "TestFileName.md")


if __name__ == '__main__':
    unittest.main()
