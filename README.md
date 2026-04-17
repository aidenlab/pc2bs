# pc2bs

**pc2bs** (point cloud → ball and stick) is a small command-line tool that converts a **point-cloud** Spacewalk `.sw` file into a **ball-and-stick** `.sw` file. The conversion is **one-way** only: it does not turn ball-and-stick files back into point clouds.

The tool reads and writes [HDF5](https://www.hdfgroup.org/solutions/hdf5/) using [h5py](https://www.h5py.org/). Output files are written as **plain, non-indexed** HDF5 so they load reliably in the [Spacewalk](https://aidenlab.github.io/spacewalk/) web app.

---

## Installation

You need **Python 3.10 or newer** and a **copy of this repository** on your machine (`git clone` or download a ZIP).

### Option A — You already have a Python environment

If you already use a Conda env, a `venv`, or a system/user `pip` setup, activate it and install from the repository root:

```bash
cd /path/to/pc2bs
python3 -m pip install -e .
```

The `-e` (editable) flag means `git pull` picks up source changes immediately — you do not need to reinstall after every update. The only time you need to re-run the install command is when the project's **required libraries** change (for example, a newer minimum version of `h5py` or `numpy`). When that happens, run the same command again:

```bash
python3 -m pip install -e .
```

**A note on shared environments.** If your active environment already holds other tools (for example `streamlit`, `numba`, or a Jupyter stack), installing pc2bs into it may pull in newer versions of `numpy` or other shared libraries and trigger pip warnings about **dependency conflicts** with those other tools. pc2bs itself will still work, but the other tools may break. If you hit this, use **Option B** below to install pc2bs into its own dedicated environment. Avoid `pip install --force-reinstall` in a shared environment — it aggressively upgrades transitive libraries and is the most common cause of these conflicts.

### Option B — You do not have a Python environment (use Conda)

If Python environments are new to you, install [Miniconda](https://docs.conda.io/en/latest/miniconda.html), then create and activate an environment for this tool:

```bash
conda create -n pc2bs python=3.11
conda activate pc2bs
cd /path/to/pc2bs
python3 -m pip install -e .
```

Run `conda activate pc2bs` whenever you want to use the tool.

### Verify

```bash
pc2bs --version
```

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

### Open the result in Spacewalk

Pass `--open` to hand the converted file off to the [Spacewalk](https://aidenlab.org/spacewalk/) web app in your default browser:

```bash
pc2bs --open INPUT.sw OUTPUT.sw
```

pc2bs writes `OUTPUT.sw`, starts a short-lived local web server, and opens a launcher page that uses Spacewalk's `postMessage` protocol (`spacewalk-ready` / `spacewalk-load`) to transfer the file in-memory — no upload and no drag-and-drop. If your browser blocks the pop-up, the launcher page shows a one-click button to continue.

Override the Spacewalk URL (for a self-hosted build, for example) with `--spacewalk-url`:

```bash
pc2bs --open --spacewalk-url http://localhost:5173/ INPUT.sw OUTPUT.sw
```

`--open` is incompatible with `OUTPUT = -` (the browser needs a real file to hand off).

---

## Updating

With your environment activated, pull the latest source and refresh metadata:

```bash
cd /path/to/pc2bs
git pull
python3 -m pip install -e .
```

Plain `pip install -e .` leaves already-satisfied libraries alone, so it is safe to run in a shared environment. Avoid `--force-reinstall` unless you are in a dedicated environment — it can upgrade shared libraries (e.g. `numpy`) and break other tools installed alongside pc2bs.

---

## Uninstall

With your environment activated:

```bash
python3 -m pip uninstall pc2bs
```

---

## Troubleshooting

### `pc2bs: command not found`

Activate the environment you installed into (`conda activate pc2bs`, or `source ~/.venvs/pc2bs/bin/activate`), or call the executable by full path (for example `~/.venvs/pc2bs/bin/pc2bs`).

### Errors about HDF5 or missing modules

With your environment activated, reinstall so dependencies are applied:

```bash
cd /path/to/pc2bs
python3 -m pip install -e .
```

If that does not resolve the problem and you are using a **dedicated** pc2bs environment (Option B, or a venv used only for pc2bs), you can do a clean refresh with `python3 -m pip install --force-reinstall -e .`. Do not use `--force-reinstall` in a shared environment — it can upgrade `numpy` and other libraries in ways that break other tools installed alongside pc2bs.

### `pip` warns about dependency conflicts during install

If the install log ends with lines like `ERROR: pip's dependency resolver … this behaviour is the source of the following dependency conflicts` naming packages such as `streamlit`, `numba`, `protobuf`, or `numpy`, pc2bs itself is installed — but the environment you installed into has **other tools** whose pinned versions disagree with what pip just pulled in. Run `pc2bs --version` to confirm pc2bs works. The cleanest fix is to reinstall pc2bs into a dedicated environment (Option B), so its dependencies cannot clobber the other tools.

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

See [docs/development-notes.md](docs/development-notes.md) for versioning and release notes.

---

## Format reference

Spacewalk documents the `.sw` layout here:

- https://aidenlab.github.io/spacewalk/file-format/specification  
- https://aidenlab.github.io/spacewalk/file-format/data-structure  

This tool intentionally does **not** read or write optional datasets such as `live_contact_map_vertices`.
