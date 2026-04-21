#!/usr/bin/env bash
# Cut a release: bump version in pyproject.toml and __init__.py, commit, tag, push.
#
# Usage:  scripts/release.sh 0.2.0
#
# Requires a clean working tree on the branch you intend to release from
# (typically main).
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <version>   (e.g. $0 0.2.0)" >&2
    exit 2
fi

version="$1"
if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+([ab.][0-9a-zA-Z.]+)?$ ]]; then
    echo "error: version '$version' does not look like semver (e.g. 0.2.0)" >&2
    exit 2
fi

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"

if [[ -n "$(git status --porcelain)" ]]; then
    echo "error: working tree is dirty; commit or stash first" >&2
    exit 1
fi

if git rev-parse "v$version" >/dev/null 2>&1; then
    echo "error: tag v$version already exists" >&2
    exit 1
fi

python3 - "$version" <<'PY'
import re, sys, pathlib
v = sys.argv[1]
py = pathlib.Path("pyproject.toml")
py.write_text(re.sub(r'^version = ".*"', f'version = "{v}"', py.read_text(), count=1, flags=re.M))
init = pathlib.Path("src/pc2bs/__init__.py")
init.write_text(re.sub(r'^__version__ = ".*"', f'__version__ = "{v}"', init.read_text(), count=1, flags=re.M))
PY

git add pyproject.toml src/pc2bs/__init__.py
git commit -m "Release v$version"
git tag -a "v$version" -m "Release $version"

branch="$(git rev-parse --abbrev-ref HEAD)"
echo
echo "Committed and tagged v$version on branch '$branch'."
echo "Push with:"
echo "  git push origin $branch v$version"
