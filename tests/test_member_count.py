import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import member_count  # noqa: E402

API = member_count.API


def member(username):
    return {"username": username, "name": username.title(), "institutional_affiliation": None,
            "orcid": "", "academic_interests": [], "url": f"{API}{username}/", "is_superadmin": False}


# Two pages as the API returns them: 20 a page at most, "next" as http://, no total.
PAGE1 = {"next": "http://stemedplus.profile.hcommons.org/api/v1/members/?cursor=cD01OTA1MA%3D%3D",
         "previous": None, "results": [member(f"user{i}") for i in range(20)]}
PAGE2 = {"next": None, "previous": API, "results": [member(f"user{i}") for i in range(20, 25)] + [member("user0")]}


def fake_api(pages):
    calls = []
    by_url = {API: pages[0], "https://stemedplus.profile.hcommons.org/api/v1/members/?cursor=cD01OTA1MA%3D%3D": pages[1]}

    def fetch(url):
        calls.append(url)
        return by_url[url]
    return fetch, calls


class MemberCountTests(unittest.TestCase):
    def test_follows_next_on_https_and_counts_distinct_usernames(self):
        fetch, calls = fake_api([PAGE1, PAGE2])
        count = member_count.count_members(member_count.iter_pages(fetch, pause=0))
        self.assertEqual(count, 25)
        self.assertTrue(all(u.startswith("https://") for u in calls))
        self.assertEqual(len(calls), 2)

    def test_stops_if_next_link_repeats(self):
        looping = {"next": API, "previous": None, "results": [member("a")]}
        with self.assertRaises(ValueError):
            member_count.count_members(member_count.iter_pages(lambda url: looping, pause=0))

    def test_rejects_page_without_results_and_empty_list(self):
        with self.assertRaises(ValueError):
            list(member_count.iter_pages(lambda url: {"detail": "Not found."}, pause=0))
        with self.assertRaises(ValueError):
            member_count.count_members([{"next": None, "results": []}])

    def test_writes_count_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "members.json"
            member_count.update(1024, out, dt.date(2026, 11, 24))
            data = json.loads(out.read_text())
            self.assertEqual((data["count"], data["as_of"], data["source"]), (1024, "2026-11-24", API))

    def test_keeps_last_number_when_total_drops_sharply(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "members.json"
            out.write_text(json.dumps({"count": 988, "as_of": "2026-11-23"}))
            with self.assertRaises(ValueError):
                member_count.update(12, out)
            self.assertEqual(json.loads(out.read_text())["count"], 988)

    def test_main_reads_saved_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            saved = Path(tmp) / "pages.json"
            saved.write_text(json.dumps([PAGE1, PAGE2]))
            out = Path(tmp) / "members.json"
            member_count.main([str(saved)], out)
            self.assertEqual(json.loads(out.read_text())["count"], 25)

    def test_published_file_is_valid(self):
        data = json.loads(member_count.OUT.read_text())
        self.assertIsInstance(data["count"], int)
        dt.date.fromisoformat(data["as_of"])


if __name__ == "__main__":
    unittest.main()
