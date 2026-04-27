# qasmpi

Fetch any [QASMBench](https://github.com/dqc-community/QASMBench) circuit by name. Circuits are retrieved on demand from the public GitHub repo and cached locally — no bundled files, no large wheel.

## Installation

```bash
pip install qasmpi
```

## Usage

```python
import qasmpi

# Fetch a circuit by name
qasm = qasmpi.get_circuit("qft_n18")

# Fetch the hardware-transpiled variant
qasm = qasmpi.get_circuit("qft_n18", transpiled=True)

# List all available circuits
qasmpi.list_circuits()                  # all 132
qasmpi.list_circuits(size="medium")     # small / medium / large

# Look up the size category of a circuit
qasmpi.get_size("qft_n18")              # "medium"

# Clear the local disk cache (~/.cache/qasmpi/)
qasmpi.clear_cache()
```

## How it works

Circuit files are fetched from `raw.githubusercontent.com/dqc-community/QASMBench` and cached at `~/.cache/qasmpi/`. Subsequent calls for the same circuit are served from disk without hitting the network.
