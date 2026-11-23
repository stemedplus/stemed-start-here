import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import member_count  # noqa: E402

PAGE = '<a href="?cursor=x">Next >></a>\n  <span class="member-count">1,024 members</span>\n  <form method="get">'


class MemberCountTests(unittest.TestCase):
    def test_reads_the_total(self):
        self.assertEqual(member_count.read_count(PAGE), 1024)
        self.assertEqual(member_count.read_count('<span class="member-count">988 members</span>'), 988)

    def test_writes_count_and_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "members.json"
            member_count.update(PAGE, out, dt.date(2026, 11, 24))
            data = json.loads(out.read_text())
            self.assertEqual((data["count"], data["as_of"]), (1024, "2026-11-24"))

    def test_keeps_last_number_when_page_has_none_or_drops_sharply(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "members.json"
            out.write_text(json.dumps({"count": 988, "as_of": "2026-11-23"}))
            with self.assertRaises(ValueError):
                member_count.update("<p>Page not found</p>", out)
            with self.assertRaises(ValueError):
                member_count.update('<span class="member-count">12 members</span>', out)
            self.assertEqual(json.loads(out.read_text())["count"], 988)

    def test_published_file_is_valid(self):
        data = json.loads(member_count.OUT.read_text())
        self.assertIsInstance(data["count"], int)
        dt.date.fromisoformat(data["as_of"])


if __name__ == "__main__":
    unittest.main()
