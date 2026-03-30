# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`backtesting.py` is a Python library for backtesting trading strategies. It simulates strategy performance over historical OHLCV data and outputs statistics and plots.

## Commands

```bash
# Install dev dependencies
pip install -e '.[doc,test,dev]'

# Run all tests (unittest-based)
python -m backtesting.test

# Lint with ruff (project's primary linter)
ruff check backtesting

# Lint with flake8 (legacy)
flake8 backtesting

# Type check
mypy backtesting

# Coverage
coverage run -m backtesting.test && coverage report
```

## Code Architecture

### Core Package: `backtesting/`

- `backtesting.py` — Main module containing `Backtest`, `Strategy`, `Order`, `Trade`, `Position`, `_Broker`. The engine iterates bar-by-bar calling `Strategy.next()`.
- `lib.py` — Utilities: `crossover`, `cross`, `barssince`, `quantile`, `SignalStrategy`, `TrailingStrategy`, `FractionalBacktest`, `MultiBacktest`, `plot_heatmaps`.
- `_plotting.py` — Bokeh visualization (plots equity curve, trades, OHLCV).
- `_stats.py` — Statistics computation (`compute_stats`, drawdown analysis, geometric mean).
- `_util.py` — Internal helpers: `try_`, `patch`, `_Array`, `_Indicator`, `_Data`, `SharedMemoryManager`.

### Test Package: `backtesting/test/`

- `_test.py` — Main test suite (~1180 lines, unittest). Run via `python -m backtesting.test`.
- `__init__.py` — Test data loaders: `GOOG` (daily stock), `EURUSD` (hourly forex), `BTCUSD` (monthly crypto), plus `SMA` helper.
- `__main__.py` — Entry point that invokes `unittest.main` on `_test`.

### Key Patterns

- **Strategy**: Subclass `Strategy`, implement `init()` (indicator setup with `self.I()`) and `next()` (trading logic with `self.buy()`/`self.sell()`).
- **`self.I(fn, *args)`**: Declares an indicator; returns a pandas Series; auto-plotted.
- **`crossover(a, b)`**: Returns `True` when `a` crosses above `b`.
- **`Backtest.run()`**: Returns a `Stats` object with `_trades`, `_equity_curve`, and computed metrics.
- **`Backtest.optimize()`**: Grid-search over parameter tuples; uses `backtesting.Pool` for multiprocessing.
- **`SharedMemoryManager`**: Used internally for passing DataFrames to subprocesses during optimization.

### Dependencies

- `numpy >= 1.17`, `pandas >= 0.25`, `bokeh >= 3.0`
- Test: `matplotlib`, `scikit-learn`, `tqdm`, `sambo`

### Code Style

- Primary linter: **ruff** (configured in `pyproject.toml`).
- Legacy: flake8 + mypy (configured in `setup.cfg`).
- `doc/examples/` is excluded from linting.
- Max line length: 100 (ruff), 120 (flake8).
