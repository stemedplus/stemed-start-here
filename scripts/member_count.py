"""Read the STEMEd+ Commons member total and write it to site/members.json.

    python scripts/member_count.py            # read the members page, update site/members.json
    python scripts/member_count.py page.html  # read a saved copy of the page instead

The members page (https://stemedplus.profile.hcommons.org/members/) is STEMEd+ Commons' own, and
shows the total as <span class="member-count">988 members</span>. Only that number and the date are
kept; nothing about any member.

If the page cannot be read, has no total, or the total is implausible (less than half the last
one), site/members.json is left as it was, so the homepage keeps showing the last good number.
The Publish workflow runs this every day before publishing.
"""
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://stemedplus.profile.hcommons.org/members/"
OUT = Path(__file__).resolve().parent.parent / "site" / "members.json"
COUNT = re.compile(r'class="member-count"[^>]*>\s*([\d,]+)\s+members?\b', re.I)
USER_AGENT = "STEMEd+ Commons member count (https://github.com/stemedplus/stemed-start-here)"


def read_count(html: str) -> int:
    m = COUNT.search(html)
    if not m:
        raise ValueError("no member total on the page")
    return int(m.group(1).replace(",", ""))


def update(html: str, out: Path = OUT, today: dt.date = None) -> str:
    today = today or dt.date.today()
    count = read_count(html)
    try:
        last = json.loads(out.read_text(encoding="utf-8"))["count"]
    except Exception:  # noqa: BLE001 - no earlier number
        last = 0
    if count < last / 2:
        raise ValueError(f"total {count} is less than half the last one ({last})")
    out.write_text(json.dumps({"count": count, "as_of": today.isoformat(), "source": URL}, indent=2) + "\n",
                   encoding="utf-8")
    return f"{count} members as of {today.isoformat()}"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        if argv:
            html = Path(argv[0]).read_text(encoding="utf-8")
        else:
            req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                html = resp.read().decode("utf-8", "replace")
        print(update(html))
    except Exception as error:  # noqa: BLE001 - keep the last good number
        print(f"Kept the last member count ({type(error).__name__}: {error})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
