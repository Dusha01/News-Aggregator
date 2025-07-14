# Meduza News Parser

A Python script that fetches and displays the latest news articles from Meduza.io (a Russian-language news outlet) in both console and HTML-formatted output.

## Features

- Fetches latest news from Meduza's RSS feed
- Retrieves full article content via Meduza API
- Cleans HTML tags while preserving basic formatting
- Provides colored console output
- Formats news for HTML display (e.g., for Telegram bots)
- Includes retry logic for failed requests
- Configurable maximum number of news items

## Requirements

- Python 3.6+
- Required packages:
  - `requests`
  - `colorama`

Install dependencies with:
```bash
pip install requests colorama
```

## Usage


1) Run the script directly:
```bash
python NewsGet.py
```
2) To integrate in your project:
```bash
from NewsGet import get_latest_news, format_news_item

news = get_latest_news()
for item in news:
    formatted = format_news_item(
        item['title'],
        item['pub_date'],
        item['description'],
        item['url']
    )
    # Use formatted HTML output
```

## Configuration


Edit these constants in the script to customize behavior:
```bash
MEDUZA_BASE = 'https://meduza.io'  # Base URL
MEDUZA_RSS = f'{MEDUZA_BASE}/rss/all'  # RSS feed URL
MEDUZA_API = f'{MEDUZA_BASE}/api/v3/'  # API endpoint
TIMEOUT = 60  # Request timeout in seconds
RETRIES = 5  # Number of retry attempts
MAX_NEWS = 10  # Maximum news items to fetch
```

## Output Formats

1) Console Output:
    Color-coded using Colorama
    Properly wrapped text (80 chars width)
    Cleaned HTML tags
2)HTML Format (via format_news_item):
  Preserves basic HTML tags (bold, italic, links)
  Escapes special characters
  Includes publication date and read-more link
