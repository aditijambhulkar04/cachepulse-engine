# CachePulse Engine

An in-memory cache engine with **O(1) LRU and LFU eviction**, exposed through a FastAPI REST API.
No database, no Redis, no frontend.

## Run
Docs: http://127.0.0.1:8000/docs

## Configuration (environment variables)
| Variable | Default | Notes |
|---|---|---|
| `CACHE_POLICY` | `LFU` | `LRU` or `LFU` |
| `CACHE_CAPACITY` | `50` | integer |

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/` | service info |
| GET | `/health` | health check |
| PUT | `/cache` | insert/update an entry |
| GET | `/cache/{key}` | fetch an entry (hit or miss) |
| DELETE | `/cache/{key}` | delete an entry |
| GET | `/cache/stats` | hits, misses, hit_rate, size, policy |
| POST | `/cache/clear` | clear the cache and reset stats |
| GET | `/cache/config` | capacity and policy |