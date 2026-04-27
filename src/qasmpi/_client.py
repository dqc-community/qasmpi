import urllib.error
import urllib.request

from qasmpi import _cache

_RAW_BASE = "https://raw.githubusercontent.com/dqc-community/QASMBench/{ref}/{path}"


def _transpiled_path(path: str) -> str:
    # "medium/qft_n18/qft_n18.qasm" -> "medium/qft_n18/qft_n18_transpiled.qasm"
    assert path.endswith(".qasm")
    return path[:-5] + "_transpiled.qasm"


def fetch(path: str, *, ref: str = "master", transpiled: bool = False) -> str:
    if transpiled:
        path = _transpiled_path(path)

    cache_key = f"{ref}/{path}"
    cached = _cache.read(cache_key)
    if cached is not None:
        return cached

    url = _RAW_BASE.format(ref=ref, path=path)
    try:
        with urllib.request.urlopen(url) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise FileNotFoundError(
                f"Circuit not found in repo at ref={ref!r}: {path}"
            ) from exc
        raise

    _cache.write(cache_key, text)
    return text
