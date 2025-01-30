# You shouldn't change  name of function or their arguments
# but you can change content of the initial functions.
from argparse import ArgumentParser
from typing import List, Optional, Sequence
import requests
import xml.etree.ElementTree as ET
import json as JSON
from html import unescape
from datetime import datetime


class UnhandledException(Exception):
    pass


def parse_channel(channel: ET.Element) -> dict:
    """Parse channel element from RSS feed."""
    result = {
        'title': channel.find('title').text if channel.find('title') is not None else '',
        'link': channel.find('link').text if channel.find('link') is not None else '',
        'lastBuildDate': channel.find('lastBuildDate').text if channel.find('lastBuildDate') is not None else '',
        'pubDate': channel.find('pubDate').text if channel.find('pubDate') is not None else '',
        'language': channel.find('language').text if channel.find('language') is not None else '',
        'categories': [cat.text for cat in channel.findall('category')],
        'managingEditor': channel.find('managingEditor').text if channel.find('managingEditor') is not None else '',
        'description': channel.find('description').text if channel.find('description') is not None else '',
        'items': []
    }
    return result


def parse_item(item: ET.Element) -> dict:
    """Parse item element from RSS feed."""
    return {
        'title': item.find('title').text if item.find('title') is not None else '',
        'author': item.find('author').text if item.find('author') is not None else '',
        'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
        'link': item.find('link').text if item.find('link') is not None else '',
        'categories': [cat.text for cat in item.findall('category')],
        'description': item.find('description').text if item.find('description') is not None else ''
    }


def format_text_output(data: dict) -> List[str]:
    """Format RSS data as text output."""
    output = []

    # Channel information
    output.extend([
        f"Feed: {unescape(data['title'])}",
        f"Link: {data['link']}",
    ])

    if data['lastBuildDate']:
        output.append(f"Last Build Date: {data['lastBuildDate']}")
    if data['pubDate']:
        output.append(f"Publish Date: {data['pubDate']}")
    if data['language']:
        output.append(f"Language: {data['language']}")
    if data['categories']:
        output.append(f"Categories: {', '.join(data['categories'])}")
    if data['managingEditor']:
        output.append(f"Editor: {data['managingEditor']}")
    if data['description']:
        output.append(f"Description: {unescape(data['description'])}")

    output.append("")  # Empty line between channel and items

    # Items
    for item in data['items']:
        item_output = []
        if item['title']:
            item_output.append(f"Title: {unescape(item['title'])}")
        if item['author']:
            item_output.append(f"Author: {item['author']}")
        if item['pubDate']:
            item_output.append(f"Published: {item['pubDate']}")
        if item['link']:
            item_output.append(f"Link: {item['link']}")
        if item['categories']:
            item_output.append(f"Categories: {', '.join(item['categories'])}")

        output.extend(item_output)
        if item['description']:
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
