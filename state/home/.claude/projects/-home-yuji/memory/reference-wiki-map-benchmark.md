---
name: reference-wiki-map-benchmark
description: "how to measure the wiki map's speed (tool in ~/dev/wiki-bench, method in wiki docs/MEASURING-THE-MAP.md) and the traps that gave wrong numbers"
metadata:
  node_type: memory
  type: reference
  originSessionId: 18bdee0e-581d-4c68-8ff4-a50980b0743d
  modified: 2026-11-05T19:00:49.938Z
---

Tool: `~/dev/wiki-bench/` (`map_bench.py` traces animation-frame tasks in a headless Chrome; `map_verify.py` checks a build against a reference; `ab_run.sh` and `ab_ablate.sh` alternate versions). Method, results and the list of traps: `~/dev/wiki/docs/MEASURING-THE-MAP.md`. Kept outside the repo because it is Python and the repo is Elm/Elixir/Rust ([[work-ask-language]]: Giovanni has not decided yet).

Traps that produced wrong conclusions (2026-11-05):
- The Claude-in-Chrome browser throttles animation frames (about 1 a second): use the harness's own headless Chrome.
- Headless Chrome draws in software by default: add `--enable-gpu --ignore-gpu-blocklist --enable-gpu-rasterization --use-angle=gl`.
- The same build ran 3.5 times slower in one batch than in another. Only alternate versions inside one batch, and run a plain run before every ablation; noise of plain runs is about 5 %.
- Compare time per frame, not total busy time (a faster version fits more frames in the window).

**Why:** three earlier conclusions were wrong (labels as the main cost, "no change" between rounds, a 4x gain) until these were found.
**How to apply:** before claiming a speed-up on the wiki map, run the alternating comparison from the doc and quote per-frame times with their spread.

**Globe-turning traps (2026-11-05):** `map_bench.py` scenario `drag` drags a dot; use `pan` for turning the globe. `build.sh` deletes the
build folder, restart any `http.server` serving it. Dots in the DOM are `g.node` with a `<title>` (no data-id). Results and the v4
experiment: `~/dev/wiki-bench/globe/RESULTS.md` (round 3).

## Round 5 tools and traps (2026-11-06)
Tools live in `~/dev/wiki-bench/globe` (README.md there): compare.py (fair multi-build timing with drift control), callprof.py +
callcmp.py + elmmap.py (which Elm function owns time, exact call counts, DOM writes per input, compiled name -> Module.elm:LINE),
framelog.py. Traps: scenarios must be open loop (`play()` in map_bench.py) or a faster page gets a shorter gesture and the
comparison lies (this invalidated round 3's "v4 is 20 % smoother"); drift control showed +-5-18 % between identical runs; never
`pkill -f "pattern"` with a pattern that appears in your own command (it kills the shell); the sandbox is a git worktree of the
wiki repo. Results: RESULTS.md rounds 4-5 (v4 no gain; `will-change: transform` on svg.map cuts raster ~30 %; springs and DOM
writes are what to optimise).

## Optimisation variants (2026-11-06)
Best so far: `~/dev/wiki-globe-sandbox/variants/v6` (spring state on one array, dense step; hover/click/drag by camera maths, no DOM
discs; hover frozen during drags) on top of v2 + `will-change` rule: pan frame time -42 %, sweep -14 %, springs ~6x cheaper; zoom raster +60-75 %
unexplained. Lines as paths and keyed children gave no frame-time gain (not adopted). Not applied to ~/dev/wiki (uncommitted DY-8 work there; ask Giovanni).
Same data folder for all compared builds or layouts differ. Details: RESULTS.md rounds 6-7.
