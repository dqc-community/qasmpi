import pathlib

_CACHE_DIR = pathlib.Path.home() / ".cache" / "qasmpi"


def cache_path(repo_path: str) -> pathlib.Path:
    return _CACHE_DIR / repo_path


def read(repo_path: str) -> str | None:
    p = cache_path(repo_path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def write(repo_path: str, text: str) -> None:
    p = cache_path(repo_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def clear() -> None:
    import shutil
    if _CACHE_DIR.exists():
        shutil.rmtree(_CACHE_DIR)
