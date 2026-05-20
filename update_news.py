#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
 বাংলা ভয়েস | Bangla Voice — Automatic News Updater
====================================================================
This script pulls the latest news from FREE Bangla / Bangladesh
RSS feeds and writes them into `news.json`, which the website reads.

HOW TO RUN
----------
1. Install Python 3 (https://www.python.org/downloads/)
2. Install the one dependency:
       pip install feedparser
3. Run it:
       python update_news.py
4. It creates / overwrites `news.json` next to itself.
   Put news.json in the SAME folder as your index.html and the
   site will instantly show the fresh news.

AUTOMATE IT (free, runs daily on its own)
-----------------------------------------
See the included `.github/workflows/update-news.yml` — push this
project to a free GitHub repo and GitHub Actions will run this
script every day and publish the site for free via GitHub Pages.

You do NOT need to edit any news by hand. Add or remove feeds in
the FEEDS list below to control your sources.
====================================================================
"""

import json
import re
import html
import sys
import datetime
import hashlib
from urllib.request import Request, urlopen

try:
    import feedparser
except ImportError:
    print("ERROR: feedparser is not installed.\n"
          "Run:  pip install feedparser\n")
    sys.exit(1)

# ────────────────────────────────────────────────────────────────
#  NEWS SOURCES  (all free public RSS feeds)
#  category -> the Bangla section label shown on the site
#  Add / remove freely. If a feed ever stops working it is skipped
#  automatically; the others keep working.
# ────────────────────────────────────────────────────────────────
FEEDS = [
    # ---- Bangladesh National / General ----
    {"name": "প্রথম আলো",        "en": "Prothom Alo",   "category": "জাতীয়",      "url": "https://www.prothomalo.com/feed/"},
    {"name": "বিডিনিউজ২৪",       "en": "bdnews24",      "category": "জাতীয়",      "url": "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true"},
    {"name": "বাংলা ট্রিবিউন",   "en": "Bangla Tribune","category": "জাতীয়",      "url": "https://www.banglatribune.com/feed"},
    {"name": "যুগান্তর",         "en": "Jugantor",      "category": "জাতীয়",      "url": "https://www.jugantor.com/feed/rss.xml"},
    {"name": "জাগো নিউজ",        "en": "Jagonews24",    "category": "জাতীয়",      "url": "https://www.jagonews24.com/rss/rss.xml"},
    {"name": "কালের কণ্ঠ",       "en": "Kaler Kantho",  "category": "জাতীয়",      "url": "https://www.kalerkantho.com/rss.xml"},
    {"name": "বাংলানিউজ২৪",      "en": "BanglaNews24",  "category": "জাতীয়",      "url": "https://www.banglanews24.com/rss/rss.xml"},
    {"name": "রাইজিংবিডি",       "en": "Risingbd",      "category": "জাতীয়",      "url": "https://www.risingbd.com/rss/rss.xml"},

    # ---- International (Bangla) ----
    {"name": "বিবিসি বাংলা",     "en": "BBC Bangla",    "category": "আন্তর্জাতিক", "url": "https://feeds.bbci.co.uk/bengali/rss.xml"},

    # ---- Category-specific feeds (optional examples) ----
    # bdnews24 sport / business widgets, prothomalo sections etc. can be added here.
]

# How many articles to keep total, and per source (keeps it balanced)
MAX_TOTAL = 60
MAX_PER_SOURCE = 12

USER_AGENT = "Mozilla/5.0 (BanglaVoiceBot/1.0; +https://example.com)"

BN_DIGITS = "০১২৩৪৫৬৭৮৯"


def to_bn_number(n):
    return "".join(BN_DIGITS[int(d)] if d.isdigit() else d for d in str(n))


def clean_html(raw):
    """Strip HTML tags and decode entities from a feed summary."""
    if not raw:
        return ""
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def first_image(entry):
    """Try several common RSS places to find an article image."""
    # media:content / media:thumbnail
    for key in ("media_content", "media_thumbnail"):
        media = entry.get(key)
        if media and isinstance(media, list) and media[0].get("url"):
            return media[0]["url"]
    # enclosures
    for enc in entry.get("enclosures", []):
        if enc.get("href") and str(enc.get("type", "")).startswith("image"):
            return enc["href"]
    # <img> inside summary/content
    blob = ""
    if entry.get("summary"):
        blob += entry["summary"]
    if entry.get("content"):
        try:
            blob += entry["content"][0].get("value", "")
        except Exception:
            pass
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', blob)
    if m:
        return m.group(1)
    return ""  # site will fall back to a placeholder


def parse_feed(url):
    """Fetch a feed with a browser-like header (some feeds block bots)."""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        data = urlopen(req, timeout=20).read()
        return feedparser.parse(data)
    except Exception:
        # feedparser can also fetch directly as a fallback
        try:
            return feedparser.parse(url)
        except Exception as e:
            print(f"   ! could not fetch: {e}")
            return None


def relative_time(published_struct):
    """Return a Bangla 'x hours ago' style string."""
    if not published_struct:
        return "এইমাত্র"
    try:
        pub = datetime.datetime(*published_struct[:6])
        delta = datetime.datetime.utcnow() - pub
        mins = int(delta.total_seconds() // 60)
        if mins < 1:
            return "এইমাত্র"
        if mins < 60:
            return f"{to_bn_number(mins)} মিনিট আগে"
        hours = mins // 60
        if hours < 24:
            return f"{to_bn_number(hours)} ঘণ্টা আগে"
        days = hours // 24
        return f"{to_bn_number(days)} দিন আগে"
    except Exception:
        return "এইমাত্র"


def make_id(link, title):
    return hashlib.md5((link or title).encode("utf-8")).hexdigest()[:12]


def main():
    print("=" * 60)
    print(" বাংলা ভয়েস — Fetching latest news ...")
    print("=" * 60)

    all_articles = []
    seen_links = set()

    for feed in FEEDS:
        print(f"-> {feed['en']} ({feed['category']})")
        parsed = parse_feed(feed["url"])
        if not parsed or not parsed.entries:
            print("   (no entries / unreachable — skipped)")
            continue

        count = 0
        for entry in parsed.entries:
            if count >= MAX_PER_SOURCE:
                break
            link = entry.get("link", "").strip()
            title = clean_html(entry.get("title", "")).strip()
            if not title or link in seen_links:
                continue
            seen_links.add(link)

            summary = clean_html(entry.get("summary", "")) or \
                clean_html(entry.get("description", ""))
            # Trim very long summaries for the card excerpt
            excerpt = summary[:240] + ("…" if len(summary) > 240 else "")

            published = entry.get("published_parsed") or entry.get("updated_parsed")
            iso = ""
            if published:
                try:
                    iso = datetime.datetime(*published[:6]).isoformat()
                except Exception:
                    iso = ""

            all_articles.append({
                "id": make_id(link, title),
                "title": title,
                "excerpt": excerpt,
                "body": summary,          # full available text from the feed
                "image": first_image(entry),
                "category": feed["category"],
                "source": feed["name"],
                "source_en": feed["en"],
                "source_url": link,        # link back to the original publisher
                "published": iso,
                "time_ago": relative_time(published),
            })
            count += 1
        print(f"   + {count} articles")

    # Sort newest first
    all_articles.sort(key=lambda a: a["published"] or "", reverse=True)
    all_articles = all_articles[:MAX_TOTAL]

    # Mark hero / featured items
    for i, a in enumerate(all_articles):
        a["featured"] = (i < 3)

    now = datetime.datetime.utcnow()
    out = {
        "site": "বাংলা ভয়েস | Bangla Voice",
        "generated_at": now.isoformat() + "Z",
        "generated_at_display": now.strftime("%d %b %Y, %H:%M UTC"),
        "count": len(all_articles),
        "articles": all_articles,
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f" Done!  Wrote {len(all_articles)} articles to news.json")
    if not all_articles:
        print(" NOTE: 0 articles — your network may be blocking the feeds,")
        print("       or feeds are temporarily down. Try again or run on")
        print("       your own computer / GitHub Actions.")
    print("=" * 60)


if __name__ == "__main__":
    main()
