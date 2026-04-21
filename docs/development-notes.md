# Development Notes

## Versioning and releases

The **Python package version** (what `pc2bs --version` and `pip show pc2bs` report) lives in two hand-edited places that must stay in sync:

- `pyproject.toml` — `[project] version = "X.Y.Z"`
- `src/pc2bs/__init__.py` — `__version__ = "X.Y.Z"`

Releases are cut by bumping both, committing, and creating a matching Git tag `vX.Y.Z`. The helper script `scripts/release.sh` does all of that in one step.

### Cutting a release

From a clean working tree on the branch you want to release (typically `main`):

```bash
scripts/release.sh 0.2.0
git push origin main v0.2.0
```

The script:

1. Validates the version string and that the working tree is clean.
2. Rewrites the `version = "..."` line in `pyproject.toml` and the `__version__ = "..."` line in `src/pc2bs/__init__.py`.
3. Commits the bump with message `Release v0.2.0`.
4. Creates an annotated Git tag `v0.2.0`.
5. Prints the `git push` command to run. The script does **not** push automatically so you can inspect the commit and tag first.

After pushing, create a GitHub Release from the tag if you want release notes on the repo page.

### After pulling a new tag

`pc2bs --version` reads from `src/pc2bs/__init__.py` directly, so a plain `git pull` is enough — no reinstall needed just to see the new version number.

`pip show pc2bs` reads from the installed package metadata, which is frozen at install time. If you want `pip show` to match, reinstall:

```bash
cd /path/to/pc2bs
python3 -m pip install -e .
```

You only need to reinstall for real when the **dependencies** in `pyproject.toml` change.

### Manual bump (if you skip the script)

Edit both files by hand, then:

```bash
git add pyproject.toml src/pc2bs/__init__.py
git commit -m "Release vX.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin main vX.Y.Z
```

### Version scheme

Follow [semver](https://semver.org/): `MAJOR.MINOR.PATCH`. For pc2bs:

- **PATCH** (`0.1.0` → `0.1.1`) — bug fixes, doc changes, internal cleanup.
- **MINOR** (`0.1.0` → `0.2.0`) — new flags, new behavior, anything user-visible that is not a fix.
- **MAJOR** (`0.x.y` → `1.0.0`) — reserved for breaking CLI changes or file-format changes.

### Source of truth

`src/pc2bs/__init__.py` is the authoritative version string at runtime; `pyproject.toml` is what `pip install` and `pip show` see. The release script updates both together so they never drift. If you ever find them out of sync, `__init__.py` is what `pc2bs --version` will report.
