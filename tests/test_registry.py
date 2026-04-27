import pytest
from qasmpi._registry import REGISTRY

VALID_SIZES = {"small", "medium", "large"}


def test_total_count():
    assert len(REGISTRY) == 132


def test_all_entries_have_required_keys():
    for name, entry in REGISTRY.items():
        assert "size" in entry, f"{name}: missing 'size'"
        assert "path" in entry, f"{name}: missing 'path'"


def test_all_sizes_valid():
    for name, entry in REGISTRY.items():
        assert entry["size"] in VALID_SIZES, f"{name}: invalid size {entry['size']!r}"


def test_paths_end_with_qasm():
    for name, entry in REGISTRY.items():
        assert entry["path"].endswith(".qasm"), f"{name}: path doesn't end with .qasm"


def test_paths_start_with_size():
    for name, entry in REGISTRY.items():
        assert entry["path"].startswith(entry["size"] + "/"), (
            f"{name}: path {entry['path']!r} doesn't start with size {entry['size']!r}"
        )


def test_no_transpiled_paths_in_registry():
    for name, entry in REGISTRY.items():
        assert "_transpiled" not in entry["path"], (
            f"{name}: registry should only hold primary paths, not transpiled"
        )


@pytest.mark.parametrize("name,size", [
    ("qft_n18", "medium"),
    ("bell_n4", "small"),
    ("adder_n118", "large"),
    ("knn_n25", "medium"),
    ("ghz_state_n255", "large"),
    ("gcm_h6", "medium"),
    ("basis_test_n4", "small"),
    ("basis_trotter_n4", "small"),
])
def test_known_circuits(name, size):
    assert name in REGISTRY
    assert REGISTRY[name]["size"] == size
