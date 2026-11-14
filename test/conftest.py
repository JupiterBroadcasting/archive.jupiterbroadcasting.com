
import re
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple
from pytest import fixture, hookimpl
from _pytest.fixtures import SubRequest
from playwright.sync_api import Playwright, APIRequestContext, Page, Browser

# device -> the engine it really ships with (all iOS browsers are WebKit), so each device
#   only runs on that browser instead of all three
MOBILE_DEVICES = {
    # phones: narrowest, current iPhone width, newest Pixel in Playwright 1.50
    "Galaxy S9+": "chromium",
    "iPhone 15": "webkit",
    "Pixel 7": "chromium",
    # tablets: 768 is Bulma's last mobile px, 834 is Bulma tablet,
    #   1194 is desktop layout but still under $navbar-breakpoint (1220px) so the burger shows
    "iPad Mini": "webkit",
    "iPad Pro 11": "webkit",
    "iPad Pro 11 landscape": "webkit",
}

@hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    # exposes the call-phase result to fixtures, so mobile_device_tuple can screenshot on failure
    report = yield
    if report.when == "call":
        item.rep_call = report
    return report


def pytest_collection_modifyitems(config, items):
    """
    Deselect (rather than skip) browser copies of tests marked only_browser/skip_browser,
    so the summary doesn't report hundreds of skips that aren't real
    """
    keep, drop = [], []
    for item in items:
        browser = getattr(item, "callspec", None) and item.callspec.params.get("browser_name")
        only = {b for m in item.iter_markers("only_browser") for b in m.args}
        device = getattr(item, "callspec", None) and item.callspec.params.get("mobile_device_tuple")
        if device:
            only = {MOBILE_DEVICES[device]}
        skip = {b for m in item.iter_markers("skip_browser") for b in m.args}
        if browser and ((only and browser not in only) or browser in skip):
            drop.append(item)
        else:
            keep.append(item)
    if drop:
        config.hook.pytest_deselected(items=drop)
        items[:] = keep


@fixture
def get_test_dir() -> Path:
    return Path(__file__).parent.absolute()

@fixture
def screenshot_dir() -> Path:
    return Path('screenshots/')

# identified all possible device types by running the following in a
#   python interpreter + shell commands
"""
# python interpreter
with sync_playwright() as playwright:
    Path('./devices.json').write_text(j_dumps(playwright.devices, indent=2))

# shell cmd
jq '. | keys' devices.json| less
"""
# also should be able to view them here:
# https://github.com/microsoft/playwright/blob/v1.25.2/packages/playwright-core/src/server/deviceDescriptorsSource.json
@fixture(
    # function scope so menu state from one test can't leak into the next
    params=list(MOBILE_DEVICES),
)
def mobile_device_tuple(
    # how to access the params
    request: SubRequest,
    # browser object given by playwright built-in fixture
    browser: Browser,
    # Playwright object given by playwright built-in fixture
    playwright: Playwright,
    # from pytest-playwright's --base-url option
    #   so we're not having to hard-code the URL
    base_url: Optional[str],
) -> Tuple[Page,str]:

    context = browser.new_context(
        base_url=base_url,
        **playwright.devices[request.param]
    )
    page = context.new_page()
    try:
        # essentially a "return", but used with generators
        yield (page, request.param)
        # pytest-playwright's --screenshot only covers its own page fixture, not contexts made here
        report = getattr(request.node, "rep_call", None)
        if report and report.failed:
            slug = re.sub(r"[^\w.-]+", "-", request.node.nodeid).strip("-")
            page.screenshot(path=Path(request.config.getoption("--output")) / slug / "screenshot.png")
    finally:
        # supposed to get rid of coookies/other stored info after generator is done
        # https://playwright.dev/python/docs/api/class-apirequestcontext#api-request-context-dispose
        # https://github.com/microsoft/playwright.dev/blob/d9b4a2f3bd0510ea89c87ed230b8241eb33b6688/python/docs/api-testing.mdx#writing-api-test
        context.close()

# https://playwright.dev/python/docs/api-testing#configure
# used for doing similar requests to API calls
@fixture(scope="session")
def api_request_context(
    # base playwright context/object
    playwright: Playwright,
    # from pytest-playwright's --base-url option
    #   so we're not having to hard-code the URL
    base_url: Optional[str],
    # Generator is returned based on Playwright docs
) -> Generator[APIRequestContext, None, None]:
    # creates APIRequestContext to allow requests to be made
    #   using the base_url variable (from the plugin) to define
    #   the base_url which'll allow requests relative to that base_url
    request_context = playwright.request.new_context(base_url=base_url)
    # essentially a "return", but used with generators
    yield request_context
    # supposed to get rid of coookies/other stored info after generator is done
    # https://playwright.dev/python/docs/api/class-apirequestcontext#api-request-context-dispose
    # https://github.com/microsoft/playwright.dev/blob/d9b4a2f3bd0510ea89c87ed230b8241eb33b6688/python/docs/api-testing.mdx#writing-api-test
    request_context.dispose()

@fixture
def expected_rss_feeds() -> List[Dict[str,str,]]:
    # network-wide feeds only; retired shows have no subscribe page in the menu
    return [
        { 'href': 'http://feeds2.feedburner.com/JupiterBroadcasting', 'title': 'All Shows Feed - Audio'},
        { 'href': 'http://feeds2.feedburner.com/AllJupiterVideos', 'title': 'All Shows Feed - Video'},
        { 'href': 'https://jupiterstation.live/rss', 'title': 'Jupiter Station'},
    ]

@fixture
def expected_dropdown_items() -> Dict[str,List[Dict[str,str]]]:
    return {
        # Shows has no sub-menu here; its dropdown is the RSS feeds menu
        "Shows": [],
        "People": [
            {'href': '/hosts/', 'title': 'Hosts'},
            {'href': '/guests/', 'title': 'Guests'},
        ],
    }

@fixture
def expected_dropdowns() -> List[Dict[str,str]]:
    return [
        {'title': 'Shows', 'href': "/show/"},
        {'title': 'People', 'href': "/people/"},
    ]

@fixture
def expect_nav_items() -> List[Dict[str,str]]:
    return [
        {'title': 'Current Shows', 'href': 'https://www.jupiterbroadcasting.com/show/'},
        {'title': 'Live', 'href': 'https://www.jupiterbroadcasting.com/live/'},
        {'title': 'Membership', 'href': 'https://www.jupiterbroadcasting.com/membership/'},
    ]
