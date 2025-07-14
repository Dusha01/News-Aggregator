import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from html import escape
import time
import re
from datetime import datetime

MEDUZA_BASE = 'https://meduza.io'
MEDUZA_RSS = f'{MEDUZA_BASE}/rss/all'
MEDUZA_API = f'{MEDUZA_BASE}/api/v3/'
TIMEOUT = 60
RETRIES = 5
MAX_NEWS = 10 


def clean_html(raw_html):
    cleanTag = re.compile(r'<(?!\/?(b|strong|i|em|u|ins|s|strike|del|a|code|pre)(\s|>|\/)[^>]*>).*?>')
    cleanText = re.sub(cleanTag, '', raw_html)
    cleanText = re.sub(r'\n{3,}', '\n\n', cleanText)
    return cleanText.strip()


def get_with_retry(url, retries=RETRIES):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            if attempt == retries - 1:
                raise
            print(f"Попытка {attempt + 1} из {retries} не удалась. Ошибка: {str(e)}")
            time.sleep(2)
    return None


def format_news_item(title, pub_date, description, url):
    try:
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        pub_date_str = pub_date.strftime("%d.%m.%Y %H:%M")
    except:
        pub_date_str = pub_date
    
    clean_description = clean_html(description)
    if len(clean_description) > 3000:
        clean_description = clean_description[:3000] + "..."
    
    return (
        f"<b>{escape(title)}</b>\n"
        f"<i>{escape(pub_date_str)}</i>\n\n"
        f"{clean_description}\n\n"
        f"<a href='{escape(url)}'>Читать полностью</a>"
    )


def get_latest_news():
    try:
        rss_response = get_with_retry(MEDUZA_RSS)
        if rss_response is None:
            raise Exception("Не удалось получить RSS-ленту")
        
        try:
            root = ET.fromstring(rss_response.content)
        except ET.ParseError as e:
            raise Exception(f"Ошибка парсинга XML: {str(e)}")
        
        news_items = []
        items = root.findall('.//item')[:MAX_NEWS]
        
        for item in items:
            try:
                title = item.find('title').text if item.find('title') is not None else "Без заголовка"
                link = item.find('link').text if item.find('link') is not None else MEDUZA_BASE
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Дата неизвестна"
                
                api_path = link.replace(MEDUZA_BASE, '').strip('/')
                api_url = urljoin(MEDUZA_API, api_path)
                api_response = get_with_retry(api_url)
                
                if api_response is not None:
                    try:
                        article_data = api_response.json()
                        body = article_data.get('root', {}).get('content', {}).get('body', '')
                        body = body.replace('src="/image/', f'src="{MEDUZA_BASE}/image/')
                    except:
                        body = "Не удалось загрузить полный текст статьи"
                else:
                    body = item.find('description').text if item.find('description') is not None else "Описание недоступно"
                
                news_items.append({
                    'title': title,
                    'url': link,
                    'pub_date': pub_date,
                    'description': body
                })
                
            except Exception as e:
                print(f"Ошибка при обработке статьи: {str(e)}")
                continue
        
        return news_items
    
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        return None