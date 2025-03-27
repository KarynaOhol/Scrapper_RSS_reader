
from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as ET
import json as JSON
from html import unescape
from datetime import datetime


class UnhandledException(Exception):
    pass


def parse_channel(channel: ET.Element, json_output: bool = False) -> dict:
    """Parse channel element from RSS feed."""
    result = {}

    # Required fields
    for field in ['title', 'link', 'description']:
        elem = channel.find(field)
        if elem is not None and elem.text:
            result[field] = elem.text

    # Optional fields - only include if present and json_output is False
    if not json_output:
        optional_fields = {
            'lastBuildDate': 'lastBuildDate',
            'pubDate': 'pubDate',
            'language': 'language',
            'managingEditor': 'managingEditor'
        }

        for field, key in optional_fields.items():
            elem = channel.find(field)
            if elem is not None and elem.text:
                result[key] = elem.text
            else:
                result[key] = ''

        # Handle categories
        categories = channel.findall('category')
        result['categories'] = [cat.text for cat in categories] if categories else []
    else:
        # For JSON output, only include non-empty optional fields
        optional_fields = {
            'lastBuildDate': 'lastBuildDate',
            'pubDate': 'pubDate',
            'language': 'language',
            'managingEditor': 'managingEditor',
            'category': 'categories'
        }

        for field, key in optional_fields.items():
            if field == 'category':
                categories = channel.findall(field)
                if categories:
                    result[key] = [cat.text for cat in categories]
            else:
                elem = channel.find(field)
                if elem is not None and elem.text:
                    result[key] = elem.text

    result['items'] = []
    return result


def parse_item(item: ET.Element, json_output: bool = False) -> dict:
    """Parse item element from RSS feed."""
    result = {}

    # Handle all possible fields
    fields = {
        'title': 'title',
        'author': 'author',
        'pubDate': 'pubDate',
        'link': 'link',
        'description': 'description'
    }

    for field, key in fields.items():
        elem = item.find(field)
        if elem is not None and elem.text:
            result[key] = elem.text
        elif not json_output:  # Include empty fields only for text output
            result[key] = ''

    # Handle categories
    categories = item.findall('category')
    if categories or not json_output:
        result['categories'] = [cat.text for cat in categories]

    return result


def format_text_output(data: dict) -> List[str]:
    """Format RSS data as text output."""
    output = []

    # Channel information
    if data.get('title'):
        output.append(f"Feed: {unescape(data['title'])}")
    if data.get('link'):
        output.append(f"Link: {data['link']}")
    if data.get('lastBuildDate'):
        output.append(f"Last Build Date: {data['lastBuildDate']}")
    if data.get('pubDate'):
        output.append(f"Publish Date: {data['pubDate']}")
    if data.get('language'):
        output.append(f"Language: {data['language']}")
    if data.get('categories'):
        output.append(f"Categories: {', '.join(data['categories'])}")
    if data.get('managingEditor'):
        output.append(f"Editor: {data['managingEditor']}")
    if data.get('description'):
        output.append(f"Description: {unescape(data['description'])}")

    if data.get('items'):
        output.append("")  # Empty line between channel and items

    # Items
    for item in data['items']:
        item_output = []
        if item.get('title'):
            item_output.append(f"Title: {unescape(item['title'])}")
        if item.get('author'):
            item_output.append(f"Author: {item['author']}")
        if item.get('pubDate'):
            item_output.append(f"Published: {item['pubDate']}")
        if item.get('link'):
            item_output.append(f"Link: {item['link']}")
        if item.get('categories'):
            item_output.append(f"Categories: {', '.join(item['categories'])}")

        output.extend(item_output)
        if item.get('description'):
            output.append("")  # Empty line before description
            output.append(unescape(item['description']))
        output.append("")  # Empty line between items

    return output


def rss_parser(
        xml: str,
        limit: Optional[int] = None,
        json: bool = False,
) -> List[str]:
    """
    RSS parser.

    Args:
        xml: XML document as a string.
        limit: Number of the news to return. if None, returns all news.
        json: If True, format output as JSON.

    Returns:
        List of strings.
        Which then can be printed to stdout or written to file as a separate lines.

    Examples:
        >>> xml = '<rss><channel><title>Some RSS Channel</title><link>https://some.rss.com</link><description>Some RSS Channel</description></channel></rss>'
        >>> rss_parser(xml)
        ["Feed: Some RSS Channel",
        "Link: https://some.rss.com"]
        >>> print("\\n".join(rss_parser(xmls)))
        Feed: Some RSS Channel
        Link: https://some.rss.com
    """
    try:
        root = ET.fromstring(xml)
        channel = root.find('channel')
        if channel is None:
            raise ValueError("Invalid RSS feed: no channel element found")

        # Parse channel and items
        data = parse_channel(channel)
        items = channel.findall('item')

        # Apply limit if specified
        if limit is not None:
            items = items[:limit]

        # Parse items
        data['items'] = [parse_item(item) for item in items]

        if json:
            # Return JSON formatted output
            return [JSON.dumps(data, indent=2, ensure_ascii=False)]
        else:
            # Return text formatted output
            return format_text_output(data)

    except ET.ParseError as e:
        raise ValueError(f"Invalid XML document: {str(e)}")
    except Exception as e:
        raise UnhandledException(f"Unexpected error: {str(e)}")


def main(argv: Optional[Sequence] = None):
    """
    The main function of your task.
    """
    parser = ArgumentParser(
        prog="rss_reader",
        description="Pure Python command-line RSS reader.",
    )
    parser.add_argument("source", help="RSS URL", type=str, nargs="?")
    parser.add_argument(
        "--json", help="Print result as JSON in stdout", action="store_true"
    )
    parser.add_argument(
        "--limit", help="Limit news topics if this parameter provided", type=int
    )
    args = parser.parse_args(argv)

    if not args.source:
        parser.error("RSS URL is required")

    try:
        response = requests.get(args.source)
        response.raise_for_status()  # Raise an exception for bad status codes
        xml = response.text

        print("\n".join(rss_parser(xml, args.limit, args.json)))
        return 0
    except requests.RequestException as e:
        raise UnhandledException(f"Failed to fetch RSS feed: {str(e)}")
    except Exception as e:
        raise UnhandledException(e)


if __name__ == "__main__":
    main()
