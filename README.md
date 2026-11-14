# archive.jupiterbroadcasting.com

Every episode of the retired Jupiter Broadcasting shows (`active = false`): Linux Action Show, TechSNAP, BSD Now,
Coder Radio, Linux Action News, Self-Hosted, Unfilter, and 21 more. Current shows live in
[jupiterbroadcasting.com](https://github.com/goodwinlabs/jupiterbroadcasting.com), which 301s every old
`/show/<retired-show>/…` URL here.

> Proof of concept in the `goodwinlabs` forks. Upstream, replace `goodwinlabs` with `JupiterBroadcasting` in `go.mod`,
> `config.toml`, `scripts/fetch-people.sh` and the workflows.

## How it's put together

| Piece | Where it comes from |
|---|---|
| Layouts, CSS/JS, fonts, favicons, logos | [jb-hugo-theme](https://github.com/goodwinlabs/jb-hugo-theme), a Hugo Module (pinned in `go.mod`) |
| Shows, episodes, show art, sponsors they mention | This repo (`content/show/`, `static/images/shows/`, `content/sponsors/`) |
| People pages and avatars | The main site, imported as a Hugo Module that mounts only `content/people` and `static/images/{people,hosts,guests}` |

Differences from the main site are params in `config.toml`: `shows_active = false` (home slider and `/show/` list
retired shows), `support_url` (Support button goes to the main site's membership page) and `home_subtitle`.
The nav links back to the main site for current shows, live and membership.

## Development

Requires Docker. Hugo fetches the modules on first run (Go is in the Hugo image).

    make dev          # serve with the theme pinned in go.mod
    make dev-theme    # serve against ../jb-hugo-theme with live reload (THEME_DIR to override)

Clone the theme next to this repo for `make dev-theme`:

```text
jb-hugo-theme/
jupiterbroadcasting.com/
archive.jupiterbroadcasting.com/
```

## Tests

    make dev-tests    # terminal 1: serve with every page pre-rendered
    make tests        # terminal 2

`scripts/fetch-people.sh` checks out the people pages pinned in `go.mod` into `test/.jbsite`, so the tests check the
same people Hugo builds with. CI (`.github/workflows/e2e.yml`) runs the suite against the production nginx container.

## Updates and releases

- All PRs merge into `develop`; Render builds previews. Production ships from `main` through a `develop → main`
  release PR.
- `.github/workflows/theme-bump.yml` pins the newest theme and people `develop` commits and opens a PR into
  `develop`: on `repository_dispatch` from the theme repo, hourly, or by hand.
- The theme pin in a release is the exact commit previewed on `develop`.
