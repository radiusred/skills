---
name: tradedesk-miner
description: This skill enables an agent to mine raw statistical candidates from cached OHLCV data using the `tradedesk-miner` CLI. Streams `Finding` envelopes as NDJSON for downstream hypothesis testing.
license: Apache-2.0
metadata:
  author: radiusred.uk
---

# SKILL: tradedesk-miner

## Overview

The `tradedesk-miner` tool is a high-performance Rust data-mining engine for historical financial OHLCV data. It scans cached candle data (typically Dukascopy bid/ask CSVs prepared by [`tradedesk-dukascopy`](../tradedesk-dukascopy/SKILL.md)) and emits raw statistical findings as a stream of NDJSON envelopes on stdout. The tool is available at [https://github.com/radiusred/tradedesk-miner](https://github.com/radiusred/tradedesk-miner).

It sits as the discovery layer in the RadiusRed pipeline:

```
tradedesk-dukascopy (cache)  →  tradedesk-miner (raw findings)  →  Quant agent (hypotheses)  →  tradedesk (strategies)
```

Two consumption modes:

* **`miner scan`** — one scan invocation against a single instrument / timeframe / window. Use when you have a specific hypothesis to probe.
* **`miner sweep`** — a TOML manifest fans out across many (scan × instrument × timeframe × window × params) combinations with optional BH-FDR aggregation. Use for broad, agent-driven discovery passes.

## When to Use This Skill

Use this skill when you need to:

* Surface statistical anomalies, cross-instrument relationships, or seasonality effects from cached OHLCV data
* Run a single targeted scan ("Ljung-Box on EURUSD/bid at 15m over Jan 2024")
* Run a batch sweep ("every ANOM scan × 28 instruments × 3 timeframes × 6 years, FDR-controlled at α=0.05")
* List the catalogue of available scans (their names, arity, parameter schemas, and finding field shapes) without running anything
* Build reproducible research artefacts (every finding carries `param_hash`, `code_revision`, and `ReproEnvelope` for byte-identical re-runs)

## Prerequisites

* **`miner` on `$PATH`** — download from the [latest GitHub Release](https://github.com/radiusred/tradedesk-miner/releases/latest) for your platform; `tar -xzf` and put `miner` in `~/.local/bin`. No Rust toolchain required.
* **A populated cache** — either:
  * a real `tradedesk-dukascopy`-shaped cache at e.g. `/opt/tradedesk/marketdata` (see the [tradedesk-dukascopy skill](../tradedesk-dukascopy/SKILL.md)); or
  * the bundled synthetic fixture cache (clone the repo, run `bash scripts/generate-fixture-cache.sh`, point `MINER_CACHE_ROOT` at `./tests/fixtures/cache`)
* **Output discipline**: findings go to **stdout** as NDJSON; logs go to **stderr**. Never grep stderr for findings or vice versa.

## Required Config

Every invocation needs three values, resolved by `CLI flag > env var > TOML > error`:

| Setting | CLI flag | Env var | Purpose |
|---------|----------|---------|---------|
| Source cache root | `--cache-root` | `MINER_CACHE_ROOT` | Where the `<SYMBOL>/<YYYY>/<MM>/<DD>_<side>.csv.zst` files live |
| Derived-bar cache root | `--bar-cache-root` | `MINER_BAR_CACHE_ROOT` | Where miner writes aggregated bars (Arrow IPC) — created on demand |
| Output destination | `--output` | `MINER_OUTPUT` | `stdout` (default, recommended) or a file path |

Set them once per shell:

```bash
export MINER_CACHE_ROOT=/opt/tradedesk/marketdata
export MINER_BAR_CACHE_ROOT=$HOME/.cache/tradedesk-miner/bar
export MINER_OUTPUT=stdout
```

## Basic Usage

### Run a single scan

```bash
miner scan stats.autocorr.ljung_box@1 \
    --instrument EURUSD:bid \
    --timeframe 15m \
    --window 2024-01-01:2024-02-01 \
    --params lags=10
```

Output is NDJSON to stdout — `RunStart` first, then one `Result` per gap-free sub-range, then `RunEnd`:

```json
{"kind":"run_start","run_id":"…","started_at_utc":"2026-…","request":{…}}
{"kind":"result","scan_id@version":"stats.autocorr.ljung_box@1","effect":{"metric":"ljung_box_q_stat","value":33.87,"p_value":0.043,"extra":{"lags":10,"acf":[…]}},"data_slice":{"sources":[{"symbol":"EURUSD","side":"bid","timeframe":"15m"}],"window":"…","gap_manifest":{…}},"raw":{"series":{…}},"param_hash":"…","code_revision":"…"}
{"kind":"run_end","run_id":"…","wall_clock_ms":234,"summary":{"per_scan":{…}}}
```

Key arguments:

| Argument | Description |
|----------|-------------|
| `<scan_id@version>` | Positional, e.g. `stats.autocorr.ljung_box@1`. List via `miner scans` |
| `--instrument SYMBOL:side` | Repeatable. Length must match the scan's `arity()`: 1 for ANOM/SEAS, 2 for CROSS |
| `--timeframe` | `15m` / `1h` / `1d`. Drives bar aggregation |
| `--window` | `START:END` half-open ISO 8601 range, UTC-only (e.g. `2024-01-01:2024-02-01`) |
| `--params KEY=VAL` | Repeatable typed scan params (e.g. `--params lags=10 --params alpha=0.05`) |
| `--gap-policy` | `continuous_only` (default — emit one finding per gap-free sub-range) or `strict` (one `GapAborted` if any gap) |
| `--dry-run` | Emit one `DryRun` envelope showing the resolved request, no scan body |

### Inspect the catalogue (no scan run)

```bash
miner scans
```

Prints one JSONL line per registered scan — name, version, arity, parameter JSON schema, and finding field shapes (which keys appear in `effect.extra` and `raw.series`). This is the right pre-flight to check before constructing a `scan` invocation.

23 scans ship in v1 across three families: **ANOM** (single-series anomalies — Ljung-Box, ADF, KPSS, VR, ARCH-LM, JB, drawdown, outliers, vol-rolling, summary), **CROSS** (pair-arity — Pearson rolling, Spearman rolling, OLS rolling, lead-lag, Engle-Granger), **SEAS** (single-series seasonality — hour-of-day, day-of-week, session, EOM/SOM, event-window, ANOVA+Kruskal).

### Run a sweep manifest

A sweep TOML expands into a cartesian product of jobs and aggregates findings under optional BH-FDR control:

```toml
# sweep.toml
[sweep]
seed = 0xDEADBEEF                            # master seed for reproducibility

[[jobs]]
scan = "stats.autocorr.ljung_box@1"
instruments = ["EURUSD:bid", "GBPUSD:bid"]
timeframes  = ["15m", "1h"]
windows     = ["2024-01-01:2024-07-01"]
params      = { lags = 10 }

[[jobs]]
scan = "stats.stationarity.adf@1"
instruments = ["EURUSD:bid", "GBPUSD:bid"]
timeframes  = ["1d"]
windows     = ["2024-01-01:2025-01-01"]
params      = { regression = "ct", max_lag = 20 }

[hygiene]                                    # optional — bootstrap CI + null distribution
bootstrap   = "stationary"                   # or "block"
bootstrap_n = 999
null        = "phase_scramble"               # or "circular_shift"
null_n      = 999

[fdr]                                        # optional — Benjamini-Hochberg false-discovery control
family = "scan_id"                           # or "scan_only" / "instrument" / "global"
alpha  = 0.05
```

Run it:

```bash
miner sweep sweep.toml
```

Output stream: `RunStart` → one `Result`/`ScanError`/`GapAborted` per expanded job → one `SweepSummary` with FDR-aggregated `q_value`s → `RunEnd`. Re-run with the same seed for byte-identical output.

### Emit a fixture (for sanity / pipe testing)

```bash
miner emit-fixture
```

Emits one `RunStart` + one `RunEnd` envelope. Use it to verify your stdout-parsing pipeline before any real scans.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`   | Clean run — all envelopes streamed, no mid-stream errors |
| `1`   | Preflight rejection — bad CLI args, missing config, unknown scan, invalid window. Single `WireError` JSON line on stderr; no `RunStart` is emitted |
| `2`   | At least one mid-stream `ScanError` envelope — the run completed framing (`RunStart` + per-job lines + `RunEnd`) but individual jobs failed. Inspect each envelope's `kind` to find failures |
| `130` | SIGINT (Ctrl-C). Already-streamed envelopes are preserved (per-envelope stdout flush); no `RunEnd` |

When scripting, branch on the exit code BEFORE parsing stdout: exit `0` and `2` both produce parseable JSONL; exit `1` writes a `WireError` to stderr and nothing useful to stdout.

## The `Finding` Envelope

Every line on stdout is one of these `kind` values:

| Kind | When |
|------|------|
| `run_start` | First envelope. Carries `run_id` (ULID), `started_at_utc`, `miner_version`, `code_revision`, and the resolved request |
| `result` | One per successful gap-free sub-range. Carries `effect` (the scan's headline metric + p-value + `extra` map), `data_slice` (sources + window + gap_manifest), `raw.series` (the underlying arrays so consumers can re-test) |
| `scan_error` | A job failed mid-stream (data-quality / kernel error). Carries `code` and `message` |
| `gap_aborted` | `--gap-policy strict` and a gap was detected. Carries the `gap_manifest` |
| `dry_run` | `--dry-run` mode — the resolved request without running the scan body |
| `sweep_summary` | (sweep only) Aggregated FDR results across all jobs |
| `run_end` | Last envelope. Carries `wall_clock_ms` and `summary.per_scan` |

The contract: **every finding includes its raw input arrays**, not just summary stats. The Quant agent re-tests independently rather than trusting miner's summary.

## Reproducibility

Two-axis byte-identity:

* **Bit-exact re-runs**: a sweep with the same `seed`, manifest, and cache will produce byte-identical JSONL across runs (masking the volatile `run_id` / timestamps). HYG-05 is the contract; the engine seeds a `Xoshiro256PlusPlus` PRNG from the master seed and derives per-job seeds via blake3.
* **Provenance**: every `Result` carries `param_hash` (blake3 of resolved params) and `code_revision` (compile-time `MINER_CODE_REVISION` env var). Two findings are comparable iff both hashes match.

## Common Patterns

### Stream findings into a JSONL file

```bash
miner scan stats.summary.welford@1 \
    --instrument EURUSD:bid --timeframe 15m \
    --window 2024-01-01:2024-02-01 \
  > findings-eurusd-jan2024.jsonl
```

### Filter for `result` envelopes only

```bash
miner scan stats.stationarity.adf@1 --instrument EURUSD:bid --timeframe 1h \
    --window 2024-01-01:2025-01-01 \
  | jq -c 'select(.kind == "result")'
```

### Pair-arity (CROSS) scan with two legs

```bash
miner scan cross.cointegration.engle_granger@1 \
    --instrument EURUSD:bid --instrument GBPUSD:bid \
    --timeframe 1h --window 2024-01-01:2024-07-01
```

The first `--instrument` is leg A, the second is leg B (order matters for hedge ratios).

### Strict gap policy for high-stakes analysis

```bash
miner scan stats.autocorr.ljung_box@1 \
    --instrument USDJPY:bid --timeframe 15m \
    --window 2024-12-23:2025-01-03 \
    --gap-policy strict
```

If the holiday week has any cache gaps, you get one `gap_aborted` envelope and zero `result`s — better than a finding silently computed over a hole.

### Add hygiene to a single scan

```bash
miner scan stats.autocorr.ljung_box@1 \
    --instrument EURUSD:bid --timeframe 15m \
    --window 2024-01-01:2024-02-01 \
    --bootstrap stationary --bootstrap-n 999 \
    --null phase_scramble --null-n 999 \
    --seed 42
```

Bootstrap fills `effect.ci95`; null replaces `effect.p_value` with the empirical surrogate-data p-value. Same flags exist on `sweep` to override the manifest's `[hygiene]` block.

### Sweep with FDR control across all jobs

```bash
miner sweep my-discovery-sweep.toml \
  | jq -c 'select(.kind == "sweep_summary") | .fdr_by_family'
```

`sweep_summary.fdr_by_family` lists per-family adjusted q-values; reject `H0` for any finding with `q_value <= alpha`.

## Reading the Output Programmatically

Two design constraints make stdout parsing simple:

1. **One JSONL envelope per line**, with a `kind` discriminant. `jq -c` filtering works directly.
2. **`run_start` is always first, `run_end` is always last**. If you read `run_end` without an intervening `run_start`, parsing is malformed — abort.

A small Python helper ships in the repo at `docs/examples/decode_finding.py` showing the canonical parse + variant-dispatch pattern.

## CLI Reference

```text
miner [--config PATH] [--cache-root PATH] [--bar-cache-root PATH] [--output stdout|PATH] <COMMAND>

Commands:
  emit-fixture                                       Emit one RunStart + RunEnd envelope (sanity check)
  scan <scan_id@version> [options]                   Run one scan invocation
  scans                                              List the registered scan catalogue (one JSONL per scan)
  sweep <manifest.toml> [options]                    Run a TOML sweep manifest
  help                                               Print help

Global options (apply to every subcommand):
  --config PATH               Explicit config file path (otherwise XDG / CWD lookup)
  --cache-root PATH           Source cache root          [env: MINER_CACHE_ROOT]
  --bar-cache-root PATH       Derived-bar cache root     [env: MINER_BAR_CACHE_ROOT]
  --output stdout|PATH        Output destination         [env: MINER_OUTPUT]

scan options:
  --instrument SYMBOL:side    Repeatable; length must match scan arity
  --timeframe 15m|1h|1d       Bar resolution
  --window START:END          Half-open ISO 8601 window, UTC-only
  --gap-policy continuous_only|strict   Default: continuous_only
  --params KEY=VAL            Repeatable typed scan params
  --dry-run                   Emit DryRun envelope only
  --bootstrap stationary|block          Bootstrap method (HYG-03)
  --bootstrap-n N             Bootstrap resample count (cap 100_000)
  --null phase_scramble|circular_shift  Null method (HYG-04)
  --null-n N                  Null draw count (cap 100_000)
  --seed N                    Master seed for the hygiene pipeline (HYG-05)

sweep options:
  <manifest.toml>             Positional path to TOML manifest
  --dry-run                   Emit one DryRunFinding with planned_job_count, exit 0
  --seed N                    Override [sweep].seed in the manifest
  --bootstrap / --bootstrap-n / --null / --null-n  Override the [hygiene] block
```
