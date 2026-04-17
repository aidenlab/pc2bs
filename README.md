# pc2bs

**pc2bs** (point cloud → ball and stick) is a small command-line tool that converts a **point-cloud** Spacewalk `.sw` file into a **ball-and-stick** `.sw` file. The conversion is **one-way** only: it does not turn ball-and-stick files back into point clouds.

The tool reads and writes [HDF5](https://www.hdfgroup.org/solutions/hdf5/) using [h5py](https://www.h5py.org/). Output files are written as **plain, non-indexed** HDF5 so they load reliably in the [Spacewalk](https://aidenlab.github.io/spacewalk/) web app.

---

## What you need first

- **macOS or Linux** (or Windows with WSL; these instructions assume a Unix-style shell).
- **Internet access** the first time you install dependencies (h5py, numpy).
- A **copy of this repository** on your machine (clone with Git, or download and unpack a ZIP).

You do **not** need Conda, Anaconda, or a manually managed virtual environment for normal use. The instructions below use **pipx**, which installs the tool in an isolated environment and puts a single `pc2bs` command on your `PATH`.

---

## Install pipx (one-time)

### macOS (Homebrew)

If you use [Homebrew](https://brew.sh/):

```bash
brew install pipx
pipx ensurepath
```

`pipx ensurepath` adds pipx’s binary directory (usually `~/.local/bin`) to your shell configuration. **Close the terminal window and open a new one** after this step (or run `source ~/.zshrc` / `source ~/.bashrc`, depending on your shell).

### Any system (official installer)

If you do not use Homebrew, follow the official **pipx** installation guide:

https://pipx.pypa.io/stable/installation/

After installation, run:

```bash
pipx ensurepath
```

and restart the terminal (or `source` your shell rc file) as above.

### Check that pipx works

```bash
pipx --version
```

If you see a version number, you are ready for the next step.

---

## Install pc2bs with pipx (recommended)

Replace the path below with the **actual** path to your copy of this repository (the folder that contains `pyproject.toml`).

```bash
pipx install -e /path/to/pc2bs
```

Example if the project lives in your home directory:

```bash
pipx install -e "$HOME/SpacewalkDevelopment/pc2bs"
```

The `-e` flag means “editable”: the `pc2bs` command runs the code from that folder. **Python code changes** take effect as soon as you update the files (for example after `git pull`). If **dependencies** in `pyproject.toml` change, you need one extra step—see [Updating your installation](#updating-your-installation).

### Confirm the command is available

```bash
which pc2bs
pc2bs --version
```

You should see a path under your home directory (typically inside `.local/pipx/...`) and a version string.

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

### Case 1: You used `pipx install -e` on a local Git clone (the path in this README)

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

### Case 2: You installed directly from GitHub with pipx (no local clone)

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

### Case 3: You installed a non-editable copy from a local path (no `-e`)

Re-run install with `--force` so pipx rebuilds the environment from that path:

```bash
pipx install --force /path/to/pc2bs
```

---

## Uninstall

To remove the tool completely:

```bash
pipx uninstall pc2bs
```

---

## Troubleshooting

### `pc2bs: command not found`

1. Run `pipx ensurepath`, then **open a new terminal**.
2. Check that `~/.local/bin` (or the path pipx printed) appears in your `PATH`:

   ```bash
   echo "$PATH"
   ```

3. Run `which pc2bs` again.

### `pipx: command not found`

pipx is not installed or not on your `PATH`. Complete the **Install pipx** section above.

### Errors about HDF5 or missing modules

The `pipx` install pulls in **h5py** and **numpy** automatically. If something failed during install, try:

```bash
pipx install --force -e /path/to/pc2bs
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

## Format reference

Spacewalk documents the `.sw` layout here:

- https://aidenlab.github.io/spacewalk/file-format/specification  
- https://aidenlab.github.io/spacewalk/file-format/data-structure  

This tool intentionally does **not** read or write optional datasets such as `live_contact_map_vertices`.
