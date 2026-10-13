---
name: tradedesk-marketdata
description: >
  Fetch historical FX, index and commodity tick data (Dukascopy or
  HistData.com) into a local candle cache, export OHLCV candles at any
  timeframe for backtests, backfill gaps, and verify or repair a cache, with
  the tradedesk-md-* commands. Use when a backtest or the miner needs market
  data that is not cached yet, or when a cache looks wrong. Don't use it for
  mining findings from a cache (tradedesk-miner).
license: MIT
metadata:
  author: radiusred.uk
---

# tradedesk-marketdata

`tradedesk-marketdata` (formerly `tradedesk-dukascopy`) downloads raw ticks
from a source, builds one 1-minute candle file per UTC day in a permanent
cache, and exports range CSVs with a metadata sidecar. Source:
<https://github.com/radiusred/tradedesk-marketdata>. Its README is the full
reference; this skill covers what an agent needs most.

## Install

```bash
pip install tradedesk-marketdata     # Python >= 3.11
tradedesk-md-export --help
```

| Command | Does |
|---|---|
| `tradedesk-md-export` | Fetch into the cache, and optionally export candles |
| `tradedesk-md-verify` | Compare a cache with a trusted reference cache, day by day (read-only) |
| `tradedesk-md-normalize` | Repair days whose prices sit outside the symbol's expected band |
| `tradedesk-md-rescale` | Snap days that drifted off a symbol's dominant scale back onto it |

`tradedesk-dc-*` are pre-2.0 aliases. Don't use them in new work.

## Export

`--source` is **required**: `dukascopy` or `histdata`.

```bash
tradedesk-md-export --source dukascopy --symbols EURUSD GBPUSD \
  --from 2025-01-01 --to 2025-01-31 \
  --resample 5min --out data \
  --cache-dir /path/to/marketdata \
  --price-divisor 1000 --workers 1
```

| Argument | Notes |
|---|---|
| `--symbols` | One or more cache symbols |
| `--from` / `--to` | Inclusive dates, `YYYY-MM-DD` |
| `--resample` | Candle size (`5min`, `15min`, `1H`, `1D`…). Needs `--out`. **Without it nothing is written to `--out`**: the run only fills the cache. |
| `--cache-dir` | Default `.cache/marketdata` relative to the working directory. Always pass the shared, permanent cache path. |
| `--workers` | Parallel symbol workers, default 4. Use 1 for `histdata`. |
| `--keep-raw` | Keep raw downloads under `{cache}/{SYMBOL}/_raw/{source}/`, so days can be rebuilt without re-downloading |
| `--commit-partial-after-days` | Default 7. See *Backfilling*. |
| `--connect-timeout`, `--read-timeout`, `--retries` | Network tuning |
| `--log-level` | `fatal`, `error`, `warn`, `info` (default), `debug`, `trace` |
| `--no-cache` | Always re-download |

Source-specific options are refused with the other source:

- **Dukascopy only:** `--price-divisor` (default 1.0), `--probe`,
  `--probe-ticks` (default 10).
- **HistData only:** `--symbol-map` (the shipped
  `sources/histdata.example.toml` is used when it is omitted).

Output: `out/{SYMBOL}_{RULE}_{bid|ask}.csv`, for example
`EURUSD_5MIN_bid.csv`, with columns `timestamp,open,high,low,close,volume`.
Each file has a `.csv.meta.json` sidecar recording exactly how it was
produced. HistData has no volume, so `volume` is `0.0`.

## Price scaling (Dukascopy)

Dukascopy stores some instruments as float32, which is kept as-is, and
others as int32 points, which are divided by `--price-divisor`. The README's
typical values are 1000 for EURUSD, 100000 for USDJPY, and 1 or 10 for
indices. **Probe before exporting a new instrument, rather than trusting a
table:**

```bash
tradedesk-md-export --source dukascopy --symbols GBPSEK \
  --from 2025-07-01 --to 2025-07-01 --probe
```

Probe takes one symbol, downloads one hour, and prints sample ticks at
several divisors. It writes nothing.

A **scale sentry** refuses to commit a day whose median close is more than
3× away from its neighbours' on disk. A refused write is an error to act
on, not noise.

## The cache

- Day files live at `{cache}/{SYMBOL}/{YYYY}/{MM0}/{DD}_{bid|ask}.csv.zst`.
  **`MM0` is zero-based: January is `00`, December is `11`.** Look for
  month `00`, not `01`.
- Dukascopy stages hourly `.bi5` files under
  `{cache}/{SYMBOL}/{YYYY}/{MM0}/{DD}/`. They are discarded once the day is
  committed, unless `--keep-raw` is set.
- **First committed wins.** A day that already has both files is never
  re-fetched by any source. To replace it, delete its two files and export
  again.
- `{cache}/{SYMBOL}/_sources.jsonl` records which source committed each
  day, at what scale. `_partial_days.jsonl` records days committed with
  known gaps.

## Backfilling

Re-running the same export command is idempotent, and it is how gaps get
filled. It skips committed days and fetches only what is missing. A day
with hours that could not be fetched (timeouts, 429s, 5xx errors) is left
uncommitted and retried on the next run. Once a day is older than
`--commit-partial-after-days`, its permanent gaps (404s, decode failures)
are committed as a partial day instead of being retried forever.

Read the summary each run:

```
EURUSD: hours total=168, missing_404=12, missing_200=8, downloaded=120, unavailable=0, decode_failed=0, days_left_for_retry=0
```

Re-run while `unavailable`, `decode_failed` or `days_left_for_retry` is
non-zero. A 404 is normally an hour with no market: weekends, holidays,
thin hours.

## Verify and repair

After backfilling from a new source, export the overlap into a **second**
cache and compare it with the one you trust:

```bash
tradedesk-md-verify --reference /path/to/trusted --cache-dir /path/to/new \
  --symbols EURUSD --from 2020-01-01 --to 2024-12-31
```

The exit status is 1 for any shifted day, any day beyond `--tolerance`
(default 0.002), any close-ratio regime other than 1.0, any unreadable
file, or no overlap at all. It is 0 when the caches agree.

For a cache at the wrong scale, run `--dry-run` first, then repair:

```bash
tradedesk-md-normalize --cache-dir /path/to/marketdata --dry-run
tradedesk-md-rescale   --cache-dir /path/to/marketdata --symbols USDJPY --dry-run
```

Both rewrite the cache only. Re-run any `--out` export afterwards, so the
CSVs are rebuilt from the corrected days.
