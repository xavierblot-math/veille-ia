#!/usr/bin/env python3
"""Download the source feeds into sources/ (run daily by GitHub Actions).

Each line of SOURCES is: file name, URL. On failure the previous copy is kept
and the error is recorded in sources/status.txt, so the digest can say so.
"""
import datetime as dt
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "sources"

SOURCES = [
    ("xena", "https://xenaproject.wordpress.com/feed/"),
    ("gowers", "https://gowers.wordpress.com/feed/"),
    ("tao-blog", "https://terrytao.wordpress.com/feed/"),
    ("tao-mastodon", "https://mathstodon.xyz/@tao.rss"),
    ("proofsandprompts", "https://proofsandprompts.com/feed/"),
    ("siliconreckoner", "https://siliconreckoner.substack.com/feed"),
]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"fetched_at: {now}"]
    for name, url in SOURCES:
        target = OUT / f"{name}.xml"
        tmp = OUT / f"{name}.xml.tmp"
        r = subprocess.run(
            ["curl", "-sSL", "--max-time", "60", "--retry", "2", "-A", UA,
             "-o", str(tmp), "-w", "%{http_code}", url],
            capture_output=True, text=True,
        )
        code = r.stdout.strip()
        ok = r.returncode == 0 and code == "200" and tmp.exists() and tmp.stat().st_size > 200
        if ok:
            tmp.replace(target)
            lines.append(f"{name}: ok ({target.stat().st_size} bytes) {url}")
        else:
            tmp.unlink(missing_ok=True)
            err = (r.stderr.strip() or f"HTTP {code}")[:200]
            lines.append(f"{name}: FAILED ({err}) {url}")
        print(lines[-1], flush=True)
    (OUT / "status.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
