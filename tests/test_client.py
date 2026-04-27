import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from qasmpi._client import _transpiled_path, fetch

FAKE_QASM = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[4];\nh q[0];\n"


def _make_response(text: str):
    resp = MagicMock()
    resp.read.return_value = text.encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


@pytest.mark.parametrize("path,expected", [
    ("medium/qft_n18/qft_n18.qasm", "medium/qft_n18/qft_n18_transpiled.qasm"),
    ("large/QV_n32/32.qasm", "large/QV_n32/32_transpiled.qasm"),
    ("small/bell_n4/bell_n4.qasm", "small/bell_n4/bell_n4_transpiled.qasm"),
])
def test_transpiled_path(path, expected):
    assert _transpiled_path(path) == expected


def test_fetch_hits_network_on_cache_miss(tmp_path):
    with (
        patch("qasmpi._cache._CACHE_DIR", tmp_path),
        patch("urllib.request.urlopen", return_value=_make_response(FAKE_QASM)) as mock_open,
    ):
        result = fetch("medium/qft_n18/qft_n18.qasm")

    assert result == FAKE_QASM
    mock_open.assert_called_once()
    assert "qft_n18" in mock_open.call_args[0][0]


def test_fetch_returns_cache_on_second_call(tmp_path):
    with (
        patch("qasmpi._cache._CACHE_DIR", tmp_path),
        patch("urllib.request.urlopen", return_value=_make_response(FAKE_QASM)) as mock_open,
    ):
        fetch("medium/qft_n18/qft_n18.qasm")
        result = fetch("medium/qft_n18/qft_n18.qasm")

    assert result == FAKE_QASM
    mock_open.assert_called_once()  # only one network call


def test_fetch_404_raises_file_not_found(tmp_path):
    err = urllib.error.HTTPError(url="", code=404, msg="Not Found", hdrs={}, fp=None)
    with (
        patch("qasmpi._cache._CACHE_DIR", tmp_path),
        patch("urllib.request.urlopen", side_effect=err),
    ):
        with pytest.raises(FileNotFoundError, match="not found in repo"):
            fetch("large/ghost/ghost.qasm")


def test_fetch_transpiled_modifies_path(tmp_path):
    with (
        patch("qasmpi._cache._CACHE_DIR", tmp_path),
        patch("urllib.request.urlopen", return_value=_make_response(FAKE_QASM)) as mock_open,
    ):
        fetch("medium/qft_n18/qft_n18.qasm", transpiled=True)

    url = mock_open.call_args[0][0]
    assert "_transpiled" in url


def test_fetch_ref_appears_in_url(tmp_path):
    with (
        patch("qasmpi._cache._CACHE_DIR", tmp_path),
        patch("urllib.request.urlopen", return_value=_make_response(FAKE_QASM)) as mock_open,
    ):
        fetch("medium/qft_n18/qft_n18.qasm", ref="abc123")

    url = mock_open.call_args[0][0]
    assert "abc123" in url
