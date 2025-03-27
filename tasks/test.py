import unittest
from unittest.mock import patch
import json
from rss_reader import rss_parser  # Assuming your main file is named rss_parser.py

class TestRSSParser(unittest.TestCase):
    def setUp(self):
        # Sample RSS feed for testing
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Sample RSS Feed</title>
        <link>https://example.com</link>
        <description>A sample RSS feed for testing</description>
        <language>en-us</language>
        <lastBuildDate>Mon, 01 Jan 2024 12:00:00 GMT</lastBuildDate>
        <pubDate>Mon, 01 Jan 2024 11:00:00 GMT</pubDate>
        <managingEditor>editor@example.com</managingEditor>
        <category>Technology</category>
        <category>News</category>
        <item>
            <title>First Article</title>
            <author>John Doe</author>
            <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
            <link>https://example.com/article1</link>
            <category>Tech News</category>
            <description>This is the first article description.</description>
        </item>
        <item>
            <title>Second Article</title>
            <author>Jane Smith</author>
            <pubDate>Mon, 01 Jan 2024 09:00:00 GMT</pubDate>
            <link>https://example.com/article2</link>
            <category>General</category>
            <description>This is the second article description.</description>
        </item>
    </channel>
</rss>'''

    def test_text_output(self):
        """Test regular text output format"""
        result = rss_parser(self.sample_xml)
        self.assertIsInstance(result, list)
        self.assertTrue(any('Feed: Sample RSS Feed' in line for line in result))
        self.assertTrue(any('First Article' in line for line in result))
        self.assertTrue(any('Second Article' in line for line in result))

    def test_json_output(self):
        """Test JSON output format"""
        result = rss_parser(self.sample_xml, json=True)
        self.assertEqual(len(result), 1)  # JSON output should be a single string
        parsed_json = json.loads(result[0])
        self.assertEqual(parsed_json['title'], 'Sample RSS Feed')
        self.assertEqual(len(parsed_json['items']), 2)

    def test_limit(self):
        """Test limit parameter"""
        result = rss_parser(self.sample_xml, limit=1)
        # Count number of items by counting "Title:" occurrences
        titles = sum(1 for line in result if line.startswith('Title:'))
        self.assertEqual(titles, 1)

    def test_invalid_xml(self):
        """Test handling of invalid XML"""
        invalid_xml = '<invalid>xml</invalid>'
        with self.assertRaises(ValueError):
            rss_parser(invalid_xml)

    def test_missing_required_fields(self):
        """Test handling of RSS feed with missing required fields"""
        minimal_xml = '''<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <title>Minimal Feed</title>
                <link>https://example.com</link>
                <description>Minimal description</description>
            </channel>
        </rss>'''
        result = rss_parser(minimal_xml)
        self.assertIsInstance(result, list)
        self.assertTrue(any('Feed: Minimal Feed' in line for line in result))

if __name__ == '__main__':
    unittest.main()