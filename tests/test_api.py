import pytest

import qasmpi


# ── list_circuits ────────────────────────────────────────────────────────────

def test_list_circuits_total():
    assert len(qasmpi.list_circuits()) == 132


def test_list_circuits_is_sorted():
    names = qasmpi.list_circuits()
    assert names == sorted(names)


def test_list_circuits_size_filter():
    small = qasmpi.list_circuits(size="small")
    medium = qasmpi.list_circuits(size="medium")
    large = qasmpi.list_circuits(size="large")
    assert len(small) + len(medium) + len(large) == 132
    assert all(qasmpi.get_size(n) == "small" for n in small)
    assert all(qasmpi.get_size(n) == "medium" for n in medium)
    assert all(qasmpi.get_size(n) == "large" for n in large)


def test_list_circuits_bad_size():
    with pytest.raises(ValueError, match="size must be"):
        qasmpi.list_circuits(size="huge")


# ── get_size ─────────────────────────────────────────────────────────────────

def test_get_size_known():
    assert qasmpi.get_size("qft_n18") == "medium"
    assert qasmpi.get_size("bell_n4") == "small"
    assert qasmpi.get_size("adder_n118") == "large"


def test_get_size_unknown():
    with pytest.raises(KeyError):
        qasmpi.get_size("does_not_exist")


# ── get_circuit (unit — mocked network) ──────────────────────────────────────

FAKE_QASM = "OPENQASM 2.0;\nqreg q[4];\nh q[0];\n"


def test_get_circuit_unknown_name():
    with pytest.raises(KeyError, match="Unknown circuit"):
        qasmpi.get_circuit("not_a_real_circuit")


def test_get_circuit_hint_in_error():
    with pytest.raises(KeyError, match="qft"):
        qasmpi.get_circuit("qft_n999")


def test_get_circuit_calls_fetch(tmp_path):
    from unittest.mock import MagicMock, patch

    resp = MagicMock()
    resp.read.return_value = FAKE_QASM.encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)

    with (
        patch("qasmpi._cache._CACHE_DIR", tmp_path),
        patch("urllib.request.urlopen", return_value=resp),
    ):
        text = qasmpi.get_circuit("qft_n18")

    assert text == FAKE_QASM


# ── get_circuit (integration — real network) ──────────────────────────────────
#
# These tests hit raw.githubusercontent.com. Run with: pytest -m integration
#
# Each test picks a circuit whose content is predictable and checks:
#   - correct qubit register declaration  (proves right file was fetched)
#   - approximate line count              (proves file wasn't truncated)
#   - no HTML in response                 (proves no redirect/error page slipped through)

import pathlib

_LOCAL_QASMBENCH = pathlib.Path(__file__).parents[2] / "QASMBench"


@pytest.mark.integration
def test_bell_n4_qubit_count(tmp_path):
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        text = qasmpi.get_circuit("bell_n4")
    assert "qreg q[4]" in text
    assert len(text.splitlines()) >= 10
    assert "<html" not in text.lower()


@pytest.mark.integration
def test_qft_n18_qubit_count_and_size(tmp_path):
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        text = qasmpi.get_circuit("qft_n18")
    assert "qreg q[18]" in text
    assert len(text.splitlines()) >= 800   # qft_n18 is 807 lines locally
    assert "<html" not in text.lower()


@pytest.mark.integration
def test_adder_n28_large_circuit(tmp_path):
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        text = qasmpi.get_circuit("adder_n28")
    assert "qreg q[28]" in text
    assert "<html" not in text.lower()


@pytest.mark.integration
def test_knn_n25_medium_circuit(tmp_path):
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        text = qasmpi.get_circuit("knn_n25")
    assert "qreg q0[25]" in text
    assert "<html" not in text.lower()


@pytest.mark.integration
def test_transpiled_differs_from_primary(tmp_path):
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        primary = qasmpi.get_circuit("bell_n4")
        transpiled = qasmpi.get_circuit("bell_n4", transpiled=True)
    assert primary != transpiled
    assert "qreg" in transpiled
    assert "<html" not in transpiled.lower()


@pytest.mark.integration
def test_missing_transpiled_raises(tmp_path):
    # bwt_n177 has no transpiled variant in the repo
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        with pytest.raises(FileNotFoundError, match="not found in repo"):
            qasmpi.get_circuit("bwt_n177", transpiled=True)


@pytest.mark.integration
def test_cache_avoids_second_fetch(tmp_path):
    # Fetch once, then confirm second call reads from disk (no network needed)
    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        first = qasmpi.get_circuit("qft_n18")

    cached_file = tmp_path / "master" / "medium" / "qft_n18" / "qft_n18.qasm"
    assert cached_file.exists()
    assert cached_file.read_text(encoding="utf-8") == first

    # Second call with network blocked — must still succeed from cache
    import urllib.request
    original_urlopen = urllib.request.urlopen

    def no_network(url, **kwargs):
        raise AssertionError(f"unexpected network call to {url}")

    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        with patch("urllib.request.urlopen", side_effect=no_network):
            second = qasmpi.get_circuit("qft_n18")

    assert first == second


@pytest.mark.integration
def test_matches_local_repo(tmp_path):
    # Cross-check fetched content against the local QASMBench checkout
    local_file = _LOCAL_QASMBENCH / "medium" / "qft_n18" / "qft_n18.qasm"
    if not local_file.exists():
        pytest.skip("local QASMBench repo not present")

    from unittest.mock import patch
    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        remote = qasmpi.get_circuit("qft_n18")

    local = local_file.read_text(encoding="utf-8")
    assert remote == local
