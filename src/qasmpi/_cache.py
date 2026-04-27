import pathlib
import time

_CACHE_DIR = pathlib.Path.home() / ".cache" / "qasmpi"
_TTL = 48 * 3600  # seconds


def cache_path(repo_path: str) -> pathlib.Path:
    return _CACHE_DIR / repo_path


def read(repo_path: str) -> str | None:
    p = cache_path(repo_path)
    if p.exists():
        if time.time() - p.stat().st_mtime < _TTL:
            return p.read_text(encoding="utf-8")
        p.unlink()
    return None


def write(repo_path: str, text: str) -> None:
    p = cache_path(repo_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def clear() -> None:
    import shutil
    if _CACHE_DIR.exists():
        shutil.rmtree(_CACHE_DIR)
