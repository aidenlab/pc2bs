# Development Notes

## Versioning and releases

The **Python package version** (what `pc2bs --version` and `pip show pc2bs` report) comes from **Git**, not from a hand-edited string in the source tree. [setuptools-scm](https://github.com/pypa/setuptools_scm) reads your repository's **annotated or lightweight tags** (for example `v0.2.0`) when the package is built or installed.

**Typical release workflow**

1. Commit the changes you want in the release.
2. Create a tag whose name matches the version you want (common convention: **`v` + semver**, e.g. `v0.2.0`):

   ```bash
   git tag -a v0.2.0 -m "Release 0.2.0"
   git push origin main
   git push origin v0.2.0
   ```

3. On GitHub, create a **Release** from that tag (the release "name" is usually the same as the tag).

4. After a **new tag**, refresh the install so the **reported version** (`pc2bs --version`, `pip show pc2bs`) matches Git metadata. From the repo root, with the environment activated:

   ```bash
   python3 -m pip install -e .
   ```

   Use `--force-reinstall -e .` if you want a full refresh. Editable installs pick up **code** changes on `git pull` immediately, but the **version string** only updates after metadata is regenerated—run the command above after pulling **new tags**.

If you run from a checkout **without** installing the package, `pc2bs --version` may show `0.0.0+not-installed`; use a normal install for a meaningful version.
