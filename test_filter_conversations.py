#!/usr/bin/env python3

import unittest
import json
import os
import tempfile
import shutil
from filter_conversations import filter_conversations_by_uuid, filter_conversations_by_name


class TestFilterConversations(unittest.TestCase):
    """Test cases for filter_conversations.py"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.test_conversations = [
            {
                "uuid": "uuid-1",
                "name": "Python Tutorial",
                "chat_messages": [{"sender": "human", "text": "Hello"}]
            },
            {
                "uuid": "uuid-2",
                "name": "JavaScript Guide",
                "chat_messages": [{"sender": "human", "text": "Hi"}]
            },
            {
                "uuid": "uuid-3",
                "name": "Python Advanced Topics",
                "chat_messages": [{"sender": "human", "text": "Hey"}]
            },
            {
                "uuid": "uuid-4",
                "name": "Ruby Programming",
                "chat_messages": [{"sender": "human", "text": "Greetings"}]
            }
        ]
        self.input_file = os.path.join(self.test_dir, "input.json")
        self.output_file = os.path.join(self.test_dir, "output.json")

        # Write test data
        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_conversations, f)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir)

    def test_filter_by_single_uuid(self):
        """Test filtering by a single UUID."""
        filter_conversations_by_uuid(self.input_file, self.output_file, ["uuid-1"])

        with open(self.output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uuid"], "uuid-1")
        self.assertEqual(result[0]["name"], "Python Tutorial")

    def test_filter_by_multiple_uuids(self):
        """Test filtering by multiple UUIDs."""
        filter_conversations_by_uuid(self.input_file, self.output_file, ["uuid-1", "uuid-3"])

        with open(self.output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(len(result), 2)
        uuids = [conv["uuid"] for conv in result]
        self.assertIn("uuid-1", uuids)
        self.assertIn("uuid-3", uuids)

    def test_filter_by_nonexistent_uuid(self):
        """Test filtering by UUID that doesn't exist."""
        filter_conversations_by_uuid(self.input_file, self.output_file, ["uuid-999"])

        # Should not create output file when no matches
        self.assertFalse(os.path.exists(self.output_file))

    def test_filter_by_name_pattern_simple(self):
        """Test filtering by simple name pattern."""
        filter_conversations_by_name(self.input_file, self.output_file, "Python")

        with open(self.output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(len(result), 2)
        names = [conv["name"] for conv in result]
        self.assertIn("Python Tutorial", names)
        self.assertIn("Python Advanced Topics", names)

    def test_filter_by_name_pattern_case_insensitive(self):
        """Test that name pattern filtering is case-insensitive."""
        filter_conversations_by_name(self.input_file, self.output_file, "python")

        with open(self.output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(len(result), 2)

    def test_filter_by_name_pattern_regex(self):
        """Test filtering by regex pattern."""
        filter_conversations_by_name(self.input_file, self.output_file, "^Python")

        with open(self.output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        self.assertEqual(len(result), 2)

    def test_filter_by_name_pattern_no_match(self):
        """Test filtering by pattern with no matches."""
        filter_conversations_by_name(self.input_file, self.output_file, "NonExistent")

        # Should not create output file when no matches
        self.assertFalse(os.path.exists(self.output_file))

    def test_filter_missing_input_file(self):
        """Test behavior with missing input file."""
        filter_conversations_by_uuid("nonexistent.json", self.output_file, ["uuid-1"])

        # Should not create output file
        self.assertFalse(os.path.exists(self.output_file))

    def test_filter_invalid_json(self):
        """Test behavior with invalid JSON input."""
        invalid_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("not valid json{")

        filter_conversations_by_uuid(invalid_file, self.output_file, ["uuid-1"])

        # Should not create output file
        self.assertFalse(os.path.exists(self.output_file))

    def test_filter_preserves_structure(self):
        """Test that filtering preserves conversation structure."""
        filter_conversations_by_uuid(self.input_file, self.output_file, ["uuid-2"])

        with open(self.output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)

        original = self.test_conversations[1]
        filtered = result[0]

        self.assertEqual(filtered["uuid"], original["uuid"])
        self.assertEqual(filtered["name"], original["name"])
        self.assertEqual(filtered["chat_messages"], original["chat_messages"])


if __name__ == '__main__':
    unittest.main()
