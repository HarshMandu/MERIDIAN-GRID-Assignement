"""Best-effort public-page scraper for the five assessment targets.

Respect each site's terms and robots policies. No login, CAPTCHA bypass, or access-control
circumvention is attempted. Website markup may change; failed extraction is recorded.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

OUT = Path("output")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AssessmentResearchBot/1.0; +https://example.org/bot)"}
TIMEOUT = 20

TARGETS = {
    "indeed": {
        "url": "https://www.indeed.com/jobs?q=python+developer&l=Mumbai",
        "fields": "job title and company name",
    },
    "glassdoor": {
        "url": "https://www.glassdoor.com/Reviews/index.htm",
        "fields": "public company review title and star rating",
    },
    "zillow": {
        "url": "https://www.zillow.com/homes/for_sale/",
        "fields": "listing price and address",
    },
    "g2": {
        "url": "https://www.g2.com/categories/endpoint-detection-and-response",
        "fields": "product name and star rating",
    },
    "stockx": {
        "url": "https://stockx.com/nike-air-force-1-low-white-white",
        "fields": "current market price",
    },
}

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def parse_items(site: str, soup: BeautifulSoup) -> list[dict]:
    items = []
    if site == "indeed":
        # Selectors are intentionally broad and guarded; Indeed markup changes frequently.
        cards = soup.select('[data-testid="slider_item"], [data-testid="jobsearch-ResultsList"] li, .job_seen_beacon')
        for card in cards:
            title = card.select_one('[data-testid="job-title"], h2 a, h2')
            company = card.select_one('[data-testid="company-name"], [data-testid="companyName"], .companyName')
            if title and company:
                items.append({"job_title": clean(title.get_text(" ")), "company_name": clean(company.get_text(" "))})
    elif site == "glassdoor":
        for card in soup.select('[data-test="review"], .review, article')[:30]:
            title = card.select_one('[data-test="review-title"], .review-title, h2, h3')
            rating = card.select_one('[data-test="review-rating"], [aria-label*="out of 5"], .rating')
            if title or rating:
                items.append({"review_title": clean(title.get_text(" ")) if title else None,
                              "star_rating": clean(rating.get("aria-label", rating.get_text(" "))) if rating else None})
    elif site == "zillow":
        for card in soup.select('[data-test="property-card"], article, li')[:30]:
            price = card.select_one('[data-test="property-card-price"], [data-testid="price"], .StyledPropertyCardDataArea-c11n-8-109-3__sc-yipmu-0')
            address = card.select_one('address, [data-test="property-card-addr"], [data-testid="address"]')
            if price or address:
                items.append({"listing_price": clean(price.get_text(" ")) if price else None,
                              "address": clean(address.get_text(" ")) if address else None})
    elif site == "g2":
        for card in soup.select('[data-testid*="product"], .product-listing, article')[:30]:
            name = card.select_one('h3, h2, [data-testid*="product-name"]')
            rating = card.select_one('[aria-label*="star"], [aria-label*="rating"], .star-rating')
            if name or rating:
                items.append({"product_name": clean(name.get_text(" ")) if name else None,
                              "star_rating": clean(rating.get("aria-label", rating.get_text(" "))) if rating else None})
    elif site == "stockx":
        # JSON-LD is often more stable than visual classes.
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or script.get_text())
                candidates = data if isinstance(data, list) else [data]
                for obj in candidates:
                    if isinstance(obj, dict) and obj.get("@type") in ("Product", ["Product"]):
                        offers = obj.get("offers", {})
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        items.append({"product_name": obj.get("name"),
                                      "current_market_price": offers.get("price") if isinstance(offers, dict) else None,
                                      "currency": offers.get("priceCurrency") if isinstance(offers, dict) else None})
            except (json.JSONDecodeError, TypeError):
                continue
    return items

def scrape(site: str, config: dict) -> dict:
    result = {
        "source": site, "url": config["url"],
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "requested_fields": config["fields"], "items": [], "errors": []
    }
    try:
        response = requests.get(config["url"], headers=HEADERS, timeout=TIMEOUT)
        result["http_status"] = response.status_code
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        result["items"] = parse_items(site, soup)
        if not result["items"]:
            result["errors"].append("No matching records extracted; page markup may have changed or content may require JavaScript/access.")
    except requests.RequestException as exc:
        result["errors"].append(f"Fetch failed: {type(exc).__name__}: {exc}")
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for site, config in TARGETS.items():
        data = scrape(site, config)
        path = OUT / f"{site}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {path} ({len(data['items'])} item(s), {len(data['errors'])} warning(s))")

if __name__ == "__main__":
    main()
