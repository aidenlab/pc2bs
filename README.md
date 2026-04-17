# pc2bs

**pc2bs** (point cloud → ball and stick) is a small command-line tool that converts a **point-cloud** Spacewalk `.sw` file into a **ball-and-stick** `.sw` file. The conversion is **one-way** only: it does not turn ball-and-stick files back into point clouds.

The tool reads and writes [HDF5](https://www.hdfgroup.org/solutions/hdf5/) using [h5py](https://www.h5py.org/). Output files are written as **plain, non-indexed** HDF5 so they load reliably in the [Spacewalk](https://aidenlab.github.io/spacewalk/) web app.

---

## What you need first

- **macOS or Linux** (or Windows with WSL; these instructions assume a Unix-style shell).
- **Python 3.10 or newer** (`python3 --version`).
- **Internet access** the first time you install dependencies (`h5py`, `numpy`).
- A **copy of this repository** on your machine (clone with Git, or download and unpack a ZIP).

You only need **pipx** if you choose the pipx install path below. If you already use **Conda**, a **virtualenv**, or **system/user `pip`**, use [Option A](#option-a-install-with-pip-into-an-environment-you-already-use) and skip pipx entirely.

---

## Choose how to install

### Option A: Install with `pip` into an environment you already use

Use this when you already have a Conda env, a `venv`, or a user-wide `pip install --user` setup and you are comfortable activating that environment (or keeping its `bin` directory on your `PATH`).

1. **Activate** your Conda environment, **or** create/activate a venv:

   ```bash
   python3 -m venv ~/.venvs/pc2bs
   source ~/.venvs/pc2bs/bin/activate
   ```

2. **Install dependencies** (if they are not already present). Either let `pip` pull them in as dependencies of `pc2bs`, or install explicitly, for example:

   ```bash
   python3 -m pip install "h5py>=3.10" "numpy>=1.24"
   ```

3. **Install this project** from the repository root (the directory that contains `pyproject.toml`):

   ```bash
   cd /path/to/pc2bs
   python3 -m pip install -e .
   ```

   The `-e` (editable) flag means `git pull` updates the code immediately; if **dependencies** in `pyproject.toml` change, run `pip install -e .` again (or `pip install --force-reinstall -e .`) in that same environment—see [Updating your installation](#updating-your-installation).

4. **Run the tool** while that environment is active (or call the full path to the script, e.g. `~/.venvs/pc2bs/bin/pc2bs`).

```bash
which pc2bs
pc2bs --version
```

---

### Option B: Install with **pipx** (optional, no existing env required)

**pipx** is handy when you want a **single global `pc2bs` command** and a separate, automatic environment for this app—**you do not need pipx** if Option A already fits your workflow.

Install pipx **only if** you choose this option:

- **macOS (Homebrew):** `brew install pipx` then `pipx ensurepath`, then open a new terminal (or `source ~/.zshrc`).
- **Other systems:** follow https://pipx.pypa.io/stable/installation/ and run `pipx ensurepath`.

Then install **pc2bs** (replace the path with your clone):

```bash
pipx install -e /path/to/pc2bs
```

Example:

```bash
pipx install -e "$HOME/SpacewalkDevelopment/pc2bs"
```

Confirm:

```bash
which pc2bs
pc2bs --version
```

You should see a path under your home directory (often under `.local/pipx/...`) and a version string.

---

## Use the tool

### Basic usage

```bash
pc2bs INPUT.sw OUTPUT.sw
```

- **INPUT.sw** must be a **point-cloud** `.sw` (Spacewalk `multi_point` layout: spatial traces with four values per sample—region index and x, y, z—or equivalent layout recognized by the reader).
- **OUTPUT.sw** is created (or overwritten) as a **ball-and-stick** `.sw` (`single_point`: one x, y, z per genomic region per trace).

If you pass a file that is **already** ball-and-stick, the tool exits with an error and does not overwrite your output with a misleading conversion.

### Quiet mode (shell scripts and loops)

```bash
pc2bs -q INPUT.sw OUTPUT.sw
```

### Standard input and output

You may use `-` for the input and/or output. The whole HDF5 file is buffered to a temporary file internally (HDF5 needs random access), which is the usual pattern for binary CLI tools.

```bash
pc2bs - OUTPUT.sw < INPUT.sw
pc2bs INPUT.sw - > OUTPUT.sw
```

### Run without installing (optional)

From the repository root, after installing dependencies into any environment:

```bash
python3 -m pip install -e .
python3 -m pc2bs --version
```

---

## Updating your installation

This project will get **revisions, new features, and bug fixes**. How you update depends on how you installed `pc2bs`.

### Case 1: You used `pip install -e` (Conda, venv, or user `pip`)

1. **Activate** the same environment you used when installing.

2. Update the source and reinstall metadata when needed:

   ```bash
   cd /path/to/pc2bs
   git pull
   python3 -m pip install -e .
   ```

   Use `pip install --force-reinstall -e .` if dependencies in `pyproject.toml` changed and you want a clean refresh.

3. Check the version string:

   ```bash
   pc2bs --version
   ```

---

### Case 2: You used `pipx install -e` on a local Git clone

You pointed pipx at a folder on disk (for example `~/SpacewalkDevelopment/pc2bs`) and used the `-e` (editable) flag.

1. **Get the latest code** from that folder’s repository:

   ```bash
   cd /path/to/pc2bs
   git pull
   ```

2. **If only Python source changed** (`.py` files, no change to `pyproject.toml` dependencies), you are done. The next time you run `pc2bs`, it already uses the updated code.

3. **If `pyproject.toml` changed** (for example a newer minimum version of `h5py` or `numpy`), refresh the libraries inside pipx’s environment for this app:

   ```bash
   pipx reinstall pc2bs
   ```

   That reinstalls `pc2bs` from the same editable path and reapplies dependency pins.

4. **Optional sanity check** after any update:

   ```bash
   pc2bs --version
   ```

If something still looks wrong, force pipx to re-link the environment from your clone:

```bash
pipx install --force -e /path/to/pc2bs
```

---

### Case 3: You installed directly from GitHub with pipx (no local clone)

Example first-time install:

```bash
pipx install git+https://github.com/aidenlab/pc2bs.git
```

To pull the latest commit from the default branch (`main`):

```bash
pipx upgrade pc2bs
```

If `upgrade` does not pick up changes you expect, reinstall from the URL:

```bash
pipx install --force git+https://github.com/aidenlab/pc2bs.git
```

Then run `pc2bs --version` again.

---

### Case 4: You installed a non-editable copy from a local path with pipx (no `-e`)

Re-run install with `--force` so pipx rebuilds the environment from that path:

```bash
pipx install --force /path/to/pc2bs
```

---

## Uninstall

- **pipx:** `pipx uninstall pc2bs`
- **pip** (the environment where you ran `pip install -e .`): `python3 -m pip uninstall pc2bs`

---

## Troubleshooting

### `pc2bs: command not found`

- If you installed with **venv or Conda**, activate that environment first, or call the executable by full path (for example `~/.venvs/pc2bs/bin/pc2bs`).
- If you used **`pip install --user`**, ensure `~/.local/bin` is on your `PATH`.
- If you used **pipx**, run `pipx ensurepath`, open a new terminal, and confirm `~/.local/bin` appears in `echo "$PATH"`.

### `pipx: command not found`

You only need pipx if you chose **Option B**. Otherwise use **Option A** with `pip` in an environment you already have.

### Errors about HDF5 or missing modules

Reinstall so dependencies are applied:

```bash
# pipx
pipx install --force -e /path/to/pc2bs

# or, in your venv / conda env
cd /path/to/pc2bs && python3 -m pip install --force-reinstall -e .
```

### Spacewalk still will not open the output file

- Confirm the **input** was really a point-cloud `.sw` (not already ball-and-stick).
- Try opening the output in an HDF5 viewer (for example [myHDF5](https://myhdf5.hdfgroup.org/)) to confirm the file is valid HDF5.
- If the problem persists, compare against a known-good ball-and-stick `.sw` from the same project or documentation.

---

## Development (optional)

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## Versioning and releases

The **Python package version** (what `pc2bs --version` and `pip show pc2bs` report) comes from **Git**, not from a hand-edited string in the source tree. [setuptools-scm](https://github.com/pypa/setuptools_scm) reads your repository’s **annotated or lightweight tags** (for example `v0.2.0`) when the package is built or installed.

**Typical release workflow**

1. Commit the changes you want in the release.
2. Create a tag whose name matches the version you want (common convention: **`v` + semver**, e.g. `v0.2.0`):

   ```bash
   git tag -a v0.2.0 -m "Release 0.2.0"
   git push origin main
   git push origin v0.2.0
   ```

3. On GitHub, create a **Release** from that tag (the release “name” is usually the same as the tag).

4. After a **new tag**, refresh the install so the **reported version** (`pc2bs --version`, `pip show pc2bs`) matches Git metadata:

   - **pipx:** `pipx reinstall pc2bs`
   - **venv / Conda / `pip install -e`:** from the repo root, with the env activated: `python3 -m pip install -e .` (or `--force-reinstall -e .` if you want a full refresh)

   Editable installs pick up **code** changes on `git pull` immediately, but the **version string** only updates after metadata is regenerated—run one of the commands above after pulling **new tags**.

If you run from a checkout **without** installing the package (`pip install -e .` / pipx), `pc2bs --version` may show `0.0.0+not-installed`; use a normal install for a meaningful version.

---

## Format reference

Spacewalk documents the `.sw` layout here:

- https://aidenlab.github.io/spacewalk/file-format/specification  
- https://aidenlab.github.io/spacewalk/file-format/data-structure  

This tool intentionally does **not** read or write optional datasets such as `live_contact_map_vertices`.
