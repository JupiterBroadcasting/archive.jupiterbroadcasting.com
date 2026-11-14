import re
from pathlib import Path

from pytest import fixture
from playwright.sync_api import Page, expect

from episode_data import CONTENT_SHOW, META_FILES, load_episode

from episode_data import PEOPLE as PEOPLE_DIR

EPISODES = [load_episode(p) for p in CONTENT_SHOW.glob("*/*.md") if p.name not in META_FILES]


def front_matter_field(text: str, key: str) -> str | None:
    # People front matter is flat YAML and the test image has no YAML parser.
    match = re.search(rf"^{key}:\s*(.+?)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def active_host_usernames() -> set[str]:
    usernames = set()
    for path in PEOPLE_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        if front_matter_field(text, "type") != "host":
            continue
        if front_matter_field(text, "is_hidden") == "true":
            continue
        usernames.add(front_matter_field(text, "username"))
    return usernames


@fixture(autouse=True)
def setup(page: Page):
    """
    Code here will run for every test in this file
    """
    page.goto("/people/")


def test_people_all_hosts(page: Page):
    """
    Ensure the host list shows exactly the non-hidden hosts in content/people
    """
    # hosts with no episodes on this site link to their person page (jb-hugo-theme: partials/people/small.html)
    hosted = {h for e in EPISODES for h in e.data.get("hosts") or []}
    expected = {f"/hosts/{u}" if u in hosted else f"/people/{u}/" for u in active_host_usernames()}
    assert expected

    host_links = page.locator(".host-list a")
    expect(host_links).to_have_count(len(expected))
    actual = {link.get_attribute("href") for link in host_links.all()}
    assert actual == expected


def test_people_guest_pagination(page: Page):
    """
    Ensure page 2 of the people list shows different guests than page 1
    """
    first_guest = page.locator(".guest-list a").first
    expect(first_guest).to_be_visible()
    first_guest_page_1 = first_guest.get_attribute("href")

    response = page.goto("/people/page/2/")
    assert response.status == 200
    first_guest = page.locator(".guest-list a").first
    expect(first_guest).to_be_visible()
    assert first_guest.get_attribute("href") != first_guest_page_1
