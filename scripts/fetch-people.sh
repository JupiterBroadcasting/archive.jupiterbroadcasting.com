#!/usr/bin/env bash
# Checks out content/people from the main-site commit pinned in go.mod into test/.jbsite, so the e2e tests read the
# same people pages Hugo mounts into the build.
set -euo pipefail
cd "$(dirname "$0")/.."

module=github.com/goodwinlabs/jupiterbroadcasting.com
version=$(awk -v m="$module" '$1 == m { print $2 }' go.mod | head -1)
sha=${version##*-}
dest=test/.jbsite

if [ ! -d "$dest/.git" ]; then
  git clone --quiet --filter=blob:none --no-checkout "https://${module}.git" "$dest"
  git -C "$dest" sparse-checkout set content/people
fi
git -C "$dest" fetch --quiet origin "$sha" 2>/dev/null || git -C "$dest" fetch --quiet origin
git -C "$dest" checkout --quiet --detach "$sha"
echo "people from ${module}@${sha}: $(ls "$dest/content/people" | wc -l) files"
