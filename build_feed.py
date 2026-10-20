#!/usr/bin/env python3
"""Rebuild feed.xml from the daily digest files in items/.

Each item file is items/YYYY-MM-DD.html. Its first line must be
    <!-- title: Digest — 20 Oct 2026 (4 new posts) -->
and the rest is the digest body as an HTML fragment.
The feed keeps the 30 most recent days.
"""
import datetime as dt
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = "https://xavierblot-math.github.io/veille-ia/"
KEEP = 30


def rfc822(d: dt.datetime) -> str:
    return d.strftime("%a, %d %b %Y %H:%M:%S +0000")


def main() -> None:
    files = sorted((ROOT / "items").glob("????-??-??.html"), reverse=True)[:KEEP]
    now = dt.datetime.now(dt.timezone.utc)
    items = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        first, _, body = text.partition("\n")
        m = re.match(r"<!--\s*title:\s*(.*?)\s*-->", first)
        title = m.group(1) if m else f"Digest — {f.stem}"
        if not m:
            body = text
        day = dt.datetime.strptime(f.stem, "%Y-%m-%d").replace(
            hour=4, tzinfo=dt.timezone.utc
        )
        body = body.strip().replace("]]>", "]]&gt;")
        items.append(
            f"<item>\n<title>{html.escape(title)}</title>\n"
            f"<link>{SITE}#{f.stem}</link>\n"
            f'<guid isPermaLink="false">veille-ia-{f.stem}</guid>\n'
            f"<pubDate>{rfc822(day)}</pubDate>\n"
            f"<description><![CDATA[\n{body}\n]]></description>\n</item>"
        )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
        "<title>Veille IA &amp; maths — daily digest</title>\n"
        f"<link>{SITE}</link>\n"
        f'<atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>\n'
        "<description>Daily summary of Xena, Proofs and Prompts, Silicon Reckoner, "
        "Tao (blog and Mastodon) and Gowers.</description>\n"
        "<language>en</language>\n"
        f"<lastBuildDate>{rfc822(now)}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n</channel>\n</rss>\n"
    )
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"feed.xml rebuilt with {len(items)} item(s)")


if __name__ == "__main__":
    main()
