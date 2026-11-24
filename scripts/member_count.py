"""Count STEMEd+ Commons members with the Profiles API and write the total to site/members.json.

    python scripts/member_count.py               # count members through the API, update site/members.json
    python scripts/member_count.py pages.json    # count from a saved JSON list of API pages instead

The STEMEd+ Commons Profiles API (https://stemedplus.profile.hcommons.org/api/v1/members/) lists
members 20 at a time, with a cursor link to the next page ("next") and no total, so the script
follows "next" to the end and counts distinct usernames. Only that number and the date are kept;
nothing about any member.

If the API cannot be read, stops part way, or the total is implausible (less than half the last
one), site/members.json is left as it was, so the homepage keeps showing the last good number.
The Publish workflow runs this every day before publishing.
"""
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

API = "https://stemedplus.profile.hcommons.org/api/v1/members/"
SOURCE = API
OUT = Path(__file__).resolve().parent.parent / "site" / "members.json"
USER_AGENT = "STEMEd+ Commons member count (https://github.com/stemedplus/stemed-start-here)"
MAX_PAGES = 2000          # 40,000 members at 20 a page; a stop against a cursor that loops
PAUSE = 0.2               # seconds between requests, to be gentle on the API


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def next_url(page: dict, current: str):
    """The API's "next" link, kept on https (the API returns it as http://)."""
    nxt = page.get("next")
    if not nxt:
        return None
    nxt = urljoin(current, nxt)
    if nxt.startswith("http://"):
        nxt = "https://" + nxt[len("http://"):]
    return nxt


def iter_pages(fetch=get_json, start: str = API, pause: float = PAUSE):
    """Yield each page of the members list, following "next" to the end."""
    url, seen = start, set()
    while url:
        if url in seen or len(seen) >= MAX_PAGES:
            raise ValueError(f"stopped after {len(seen)} pages: the next link repeats or there are too many pages")
        seen.add(url)
        page = fetch(url)
        if not isinstance(page.get("results"), list):
            raise ValueError("an API page has no results list")
        yield page
        url = next_url(page, url)
        if url and pause:
            time.sleep(pause)


def count_members(pages) -> int:
    usernames = set()
    for page in pages:
        for member in page["results"]:
            name = member.get("username")
            if name:
                usernames.add(name)
    if not usernames:
        raise ValueError("the API listed no members")
    return len(usernames)


def update(count: int, out: Path = OUT, today: dt.date = None) -> str:
    today = today or dt.date.today()
    try:
        last = json.loads(out.read_text(encoding="utf-8"))["count"]
    except Exception:  # noqa: BLE001 - no earlier number
        last = 0
    if count < last / 2:
        raise ValueError(f"total {count} is less than half the last one ({last})")
    out.write_text(json.dumps({"count": count, "as_of": today.isoformat(), "source": SOURCE}, indent=2) + "\n",
                   encoding="utf-8")
    return f"{count} members as of {today.isoformat()}"


def main(argv=None, out: Path = OUT) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        if argv:
            pages = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
        else:
            pages = iter_pages()
        print(update(count_members(pages), out))
    except Exception as error:  # noqa: BLE001 - keep the last good number
        print(f"Kept the last member count ({type(error).__name__}: {error})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
