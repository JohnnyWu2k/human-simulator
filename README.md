# Settlement Simulator

Settlement Simulator is a self-contained simulation game with a Python engine and a browser UI. You can edit world parameters, choose policy decisions, run turn-by-turn experiments, and inspect the settlement's survival history.

## Features

- No external dependencies. The project uses only the Python standard library.
- Modular Python engine with deterministic seeds, presets, policies, events, and win or loss states.
- Browser UI for scenario editing, turn stepping, automated runs, charts, and event logs.
- Preset scenarios for testing different climates, trade conditions, and research environments.

## Run

```bash
python main.py
```

Then open `http://127.0.0.1:8000`.

`start.bat` launches the same entrypoint on Windows.

## Verification

```bash
python -m unittest discover -s tests
```
