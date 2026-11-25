# STEMEd+ Commons: Why STEMEd+?

The **Why STEMEd+?** page for [STEMEd+ Commons](https://stemedplus.org/), linked from the menu on every
STEMEd+ site: https://stemedplus.github.io/stemed-start-here/

The homepage shows what you can do on STEMEd+. This page says why it exists and why to take part:

1. **Ours, not mine.** The mission, with Join and a link to the homepage.
2. **Why we built this.** Scattered, locked away, lost.
3. **What we're building.** Open access, open scholarship, open infrastructure, and why the plus.
4. **Who it's for.** You belong here: teachers, researchers, and learning professionals from every field.
5. **Why take part.** What you get, and what you give.
6. **Where we're headed.** Peer review, humane metrics, communities with a say.
7. **Who's behind it.** NSF, Knowledge Commons and GitHub, the Advisory Board and User Advisory Committee.
8. **Your first three steps,** with a first link for each role.
9. **Other community resources.** Useful projects run by others.
10. **Collaborate with us.** Writing STEMEd+ into a grant: guided onboarding and co-design.

## Editing

Everything is in `site/index.html`, as plain HTML. The design lives on the STEMEd+ design canvas
(board 1); copy changes there into this file. The green band, menu, and footer come from
[stemedplus-theme](https://github.com/stemedplus/stemedplus-theme) and are refreshed on every publish.

## Member count

`site/members.json` holds the number of STEMEd+ Commons members and the date it was counted, for the
member-count block on the stemedplus.org homepage. The Publish workflow runs every day and
refreshes it first with `scripts/member_count.py`, which counts members through the STEMEd+ Commons
[Profiles API](https://stemedplus.profile.hcommons.org/api/v1/members/). The API lists 20 members a
page with a link to the next page and no total, so the script follows the pages to the end and
counts distinct usernames. Only the number and the date are kept, nothing about any member. If the
API can't be read, stops part way, or the total looks wrong (less than half the last one), the last
good number stays. The homepage block shows the number typed into it until the file loads.
Tests: `python -m unittest discover -s tests -v`.
