import importlib.metadata

try:
    __version__: str = importlib.metadata.version("pc2bs")
except importlib.metadata.PackageNotFoundError:
    # e.g. running from a bare source tree without `pip install -e .`
    __version__ = "0.0.0+not-installed"
