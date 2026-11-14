"""
archive.jupiterbroadcasting.com imports this repo as a Hugo Module (for people pages and avatars). Go builds module
zips from every file in the repo and rejects the whole module if any path breaks its rules, which would break
the archive's build, so new files (e.g. scraped picks named after emoji titles) must follow them too.
Rules mirror golang.org/x/mod/module.CheckFilePath.
"""
from pathlib import Path

REPO = Path(__file__).parents[1]
ALLOWED_PUNCTUATION = set("!#$%&()+,-.=@[]^_{}~ ")
SKIP_DIRS = {".git", "public", "resources", "node_modules", "screenshots", ".pytest_cache", "__pycache__", "scraped-data"}


def _bad_element(element: str) -> bool:
    return any(not (c.isalpha() or c in "0123456789" or c in ALLOWED_PUNCTUATION) for c in element)


def test_paths_are_go_module_safe():
    bad, seen = [], {}
    for path in REPO.rglob("*"):
        rel = path.relative_to(REPO)
        if rel.parts[0] in SKIP_DIRS or any(p in SKIP_DIRS for p in rel.parts):
            continue
        if any(_bad_element(part) for part in rel.parts):
            bad.append(str(rel))
        folded = str(rel).casefold()
        if folded in seen and seen[folded] != str(rel):
            bad.append(f"{rel} (case-insensitive clash with {seen[folded]})")
        seen[folded] = str(rel)
    assert not bad, f"rename these so the repo stays importable as a Go/Hugo module: {sorted(set(bad))}"
