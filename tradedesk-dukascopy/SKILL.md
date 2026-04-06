---
name: tradedesk-dukascopy
description: This skill enables an agent to fetch new market data from dukascopy to use in backtests.
license: MIT
metadata:
  author: radiusred.uk
--- 

# SKILL: tradedesk-dukascopy

## Overview

The `tradedesk-dukascopy` tool downloads raw tick data from Dukascopy's public datafeed, converts it into deterministic CSV candle files, and writes a metadata sidecar describing how the data was produced. The tool is available at [https://github.com/radiusred/tradedesk-dukascopy](https://github.com/radiusred/tradedesk-dukascopy)

## When to Use This Skill

Use this skill when you need to:

* Download historical FX or index tick data
* Generate OHLCV candles at any timeframe (1min, 5min, 15min, 1H, 1D, etc.)
* Backfill missing data for dates that previously failed to download
* Probe an instrument to determine its price format (float vs int)

## Basic Usage

### Export candles for a date range

```bash
tradedesk-dc-export --symbols EURUSD GBPUSD \
  --from 2025-01-01 --to 2025-01-31 \
  --resample 5min \
  --out data \
  --cache-dir /path/to/marketdata \
  --price-divisor 1000 \
  --workers 1
```

Key arguments:

| Argument          | Description                                                           |
| ----------------- | --------------------------------------------------------------------- |
| `--symbols`       | One or more symbols to export (space-separated)                       |
| `--from` / `--to` | Inclusive date range in YYYY-MM-DD format                             |
| `--resample`      | Output candle size (e.g., 5min, 15min, 1H). Omit for tick-only output |
| `--out`           | Output directory for CSV files (required if `--resample` is set)      |
| `--cache-dir`     | Persistent cache for downloaded .bi5 files and daily candles          |
| `--price-divisor` | Divisor for int32-encoded prices (see Price Scaling below)            |
| `--workers`       | Number of concurrent symbol workers (default: 4)                      |

### Probe mode (detect price format)

```bash
tradedesk-dc-export --symbols GBPSEK \
  --from 2025-07-01 --to 2025-07-01 \
  --probe
```

Probe mode downloads one hour and prints sample ticks at various divisors without writing output files.

## Price Scaling (`--price-divisor`)

Dukascopy stores tick prices differently per instrument:

| Instrument Type           | Format  | Typical Divisor |
| ------------------------- | ------- | --------------- |
| Major FX (EURUSD, GBPUSD) | int32   | 1000            |
| JPY crosses (USDJPY)      | int32   | 100000          |
| Indices (USA500)          | float32 | 1 or 10         |

If you see prices like `1.097675` instead of `1.09767`, you're using the wrong divisor.

## Re-Runs for Backfilling Missing Data

**This is the most important section for backfilling.**

### How the cache works

The tool maintains two-level caching:

1. **Hourly tick cache**: `.bi5` files downloaded from Dukascopy
2. **Daily candle cache**: 1-minute candles compressed as `.csv.zst` files

When a full day's data is successfully processed, the hourly `.bi5` files are deleted and replaced with daily 1-minute candle files. This makes subsequent exports much faster.

### Re-running is safe and efficient

Re-running the same export command is **idempotent** and is the intended way to fill gaps:

```bash
# First run - some hours failed due to Dukascopy rate limits
tradedesk-dc-export --symbols EURUSD \
  --from 2025-01-01 --to 2025-01-07 \
  --resample 5min \
  --cache-dir /path/to/marketdata \
  --price-divisor 1000

# Re-run - fills in missing hours only
tradedesk-dc-export --symbols EURUSD \
  --from 2025-01-01 --to 2025-01-07 \
  --resample 5min \
  --cache-dir /path/to/marketdata \
  --price-divisor 1000
```

On re-run, the tool:

* Skips days that already have complete daily candle cache
* Downloads only missing hourly `.bi5` files
* Retries hours that previously returned 404 or decode failures
* Completes quickly once cache is warm

### Why hours might be missing

* **HTTP 404**: Dukascopy has no data for that hour (weekends, holidays, illiquid hours)
* **Decode failure**: Corrupt or incomplete download, or price format mismatch
* **Rate limiting**: Dukascopy sometimes returns empty/partial data under load

All of these are automatically retried on re-run.

### Detecting gaps

Check the log output for patterns like:

```
EURUSD: hours total=168, missing_404=12, missing_200=8, downloaded=120, decode_failed=2
```

If `missing_404` or `decode_failed` is non-zero, re-run to fill those gaps.

## Output Files

When `--resample` is specified, the tool produces:

```
out/
  EURUSD_5MIN_bid.csv
  EURUSD_5MIN_bid.csv.meta.json
  EURUSD_5MIN_ask.csv
  EURUSD_5MIN_ask.csv.meta.json
```

The `.meta.json` sidecar contains the exact parameters used, making datasets reproducible.

## Common Patterns

### Parallel export of multiple symbols

```bash
tradedesk-dc-export --symbols EURUSD GBPUSD USDJPY \
  --from 2025-01-01 --to 2025-12-31 \
  --resample 1H \
  --out /data/2025 \
  --cache-dir /data/cache \
  --price-divisor 1000 \
  --workers 2
```

### Build up cache incrementally

```bash
# Month 1
tradedesk-dc-export --symbols EURUSD --from 2025-01-01 --to 2025-01-31 --cache-dir /data/cache --price-divisor 1000

# Month 2 - re-runs are instant for cached days
tradedesk-dc-export --symbols EURUSD --from 2025-02-01 --to 2025-02-28 --cache-dir /data/cache --price-divisor 1000
```

## CLI Reference

```
tradedesk-dc-export --help

  --symbols SYMBOL [SYMBOL ...]  One or more symbols to export
  --from YYYY-MM-DD              Inclusive start date
  --to YYYY-MM-DD                Inclusive end date
  --resample RULE                Candle size (e.g., 5min, 1H, 1D)
  --price-divisor FLOAT          Divisor for int32 prices (default: 1.0)
  --cache-dir PATH               Cache directory for .bi5 and daily candles
  --no-cache                     Disable caching, always re-download
  --workers N                    Max parallel symbol workers (default: 4)
  --probe                        Probe mode - print ticks, no output
  --probe-ticks N                Number of ticks to show in probe mode (default: 10)
  --out PATH                     Output directory for CSV files
  --log-level LEVEL              Log level: fatal, error, warn, info, debug, trace
```