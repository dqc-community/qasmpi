from qasmpi._cache import clear as clear_cache
from qasmpi._client import fetch as _fetch
from qasmpi._registry import REGISTRY

__all__ = ["get_circuit", "list_circuits", "get_size", "clear_cache"]


def get_circuit(name: str, *, transpiled: bool = False, ref: str = "master") -> str:
    """Return the QASM text for a named QASMBench circuit.

    Args:
        name: Circuit name as listed by list_circuits() (e.g. "qft_n18").
        transpiled: If True, fetch the hardware-transpiled variant.
        ref: Git ref (branch, tag, or commit SHA) to fetch from.

    Raises:
        KeyError: Circuit name not in the registry.
        FileNotFoundError: Transpiled variant does not exist in the repo.
    """
    if name not in REGISTRY:
        close = [k for k in REGISTRY if name.lower() in k.lower()]
        hint = f" Did you mean one of: {close[:5]}?" if close else ""
        raise KeyError(f"Unknown circuit {name!r}.{hint}")
    entry = REGISTRY[name]
    return _fetch(entry["path"], ref=ref, transpiled=transpiled)


def list_circuits(*, size: str | None = None) -> list[str]:
    """Return sorted circuit names, optionally filtered by size ('small'/'medium'/'large')."""
    if size is not None and size not in ("small", "medium", "large"):
        raise ValueError(f"size must be 'small', 'medium', or 'large', got {size!r}")
    return sorted(
        name for name, entry in REGISTRY.items()
        if size is None or entry["size"] == size
    )


def get_size(name: str) -> str:
    """Return the size category ('small', 'medium', 'large') for a circuit."""
    if name not in REGISTRY:
        raise KeyError(f"Unknown circuit {name!r}")
    return REGISTRY[name]["size"]
