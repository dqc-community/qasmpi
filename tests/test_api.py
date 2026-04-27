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

@pytest.mark.integration
def test_get_circuit_live_fetch(tmp_path):
    from unittest.mock import patch

    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        text = qasmpi.get_circuit("bell_n4")

    assert "OPENQASM" in text
    assert "qreg" in text


@pytest.mark.integration
def test_get_circuit_live_transpiled(tmp_path):
    from unittest.mock import patch

    with patch("qasmpi._cache._CACHE_DIR", tmp_path):
        text = qasmpi.get_circuit("bell_n4", transpiled=True)

    assert "OPENQASM" in text
