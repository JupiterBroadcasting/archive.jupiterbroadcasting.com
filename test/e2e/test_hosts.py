from pytest import fixture
from playwright.sync_api import Page, expect


@fixture(autouse=True)
def setup(page: Page):
    page.goto("/hosts/")


def test_current_and_former_hosts_share_one_list(page: Page):
    hosts = page.locator(".hosts-list")
    expect(hosts).to_have_count(1)
    expect(hosts).to_contain_text("Chris Fisher")
    expect(hosts).to_contain_text("Alan Pope")
    expect(page.locator(".former-hosts-list")).to_have_count(0)
    expect(page.get_by_role("heading", name="Former Hosts")).to_have_count(0)


def test_hosts_paginated_alphabetically_across_one_list(page: Page):
    page.goto("/hosts/page/2/")
    expect(page.locator(".hosts-list")).to_contain_text("Jim Salter")
    expect(page.locator(".hosts-list")).not_to_contain_text("Chris Fisher")


def test_hidden_people_not_listed(page: Page):
    expect(page.locator("main, #wrapper")).not_to_contain_text("Friends of Jupiter Broadcasting")
