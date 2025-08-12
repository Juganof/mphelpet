
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def scrape_marktplaats(keyword: str, limit: int = 30):
    """
    Scrapes PUBLIC search results (first page) from Marktplaats.
    Returns a list of dicts: title, price_raw, url, location (if found).
    """
    if not keyword:
        return []
    url = f"https://www.marktplaats.nl/l?q={quote(keyword)}"
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    listings = []
    for li in soup.select("li")[:300]:
        a = li.select_one("a[href*='/v/']")
        if not a:
            continue
        title_el = li.select_one("h3, h2")
        price_el = li.select_one("[class*='price'], .price, [data-testid='price']")
        location_el = li.select_one("[class*='location'], [data-testid='location']")

        if title_el:
            url_item = a.get("href")
            if url_item and url_item.startswith("/"):
                url_item = "https://www.marktplaats.nl" + url_item
            title = title_el.get_text(strip=True)
            price_text = price_el.get_text(strip=True) if price_el else ""
            location = location_el.get_text(strip=True) if location_el else ""

            if title and url_item:
                listings.append({
                    "title": title,
                    "price_raw": price_text,
                    "url": url_item,
                    "location": location,
                })
            if len(listings) >= limit:
                break
    return listings
