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

The `-e` (editable) flag means `git pull` picks up source changes immediately. If `pyproject.toml` dependencies change, re-run `python3 -m pip install -e .` (or `--force-reinstall -e .` for a clean refresh).

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

---

## Updating

With your environment activated, pull the latest source and refresh metadata:

```bash
cd /path/to/pc2bs
git pull
python3 -m pip install -e .
```

Use `python3 -m pip install --force-reinstall -e .` if dependencies changed and you want a clean refresh.

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

Reinstall so dependencies are applied:

```bash
cd /path/to/pc2bs
python3 -m pip install --force-reinstall -e .
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

See [docs/development-notes.md](docs/development-notes.md) for versioning and release notes.

---

## Format reference

Spacewalk documents the `.sw` layout here:

- https://aidenlab.github.io/spacewalk/file-format/specification  
- https://aidenlab.github.io/spacewalk/file-format/data-structure  

This tool intentionally does **not** read or write optional datasets such as `live_contact_map_vertices`.
