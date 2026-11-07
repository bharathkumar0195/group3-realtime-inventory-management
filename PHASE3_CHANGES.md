# Phase 3 Changes and Speedups

## What changed

The inherited system could list low-stock products but could not rank them by urgency. Phase 3 adds top_k_urgent(k), which returns up to k eligible Product records ordered by shortfall, largest first, then SKU ascending. Shortfall is minimum stock minus quantity. Products exactly at the threshold remain eligible. Queries leave inventory and history unchanged.

A full-sort reference ranks every low-stock product before taking the first k. The optimized method uses heapq.nsmallest over the same records. For m eligible products and small k greater than one, query time changes from O(m log m) to O(m log k). Query auxiliary space changes from O(m) to O(k). Both approaches still scan eligible products. For k=1 the scan takes O(m); returning all records in order costs O(m log m).

The full-sort method is a new comparison baseline, not a feature that existed in Phase 2. Existing stock-update and report behavior is unchanged.

## Combining the contributions

The urgency method, its tests, profiling, and final-state checks were combined with Geetha's separate generator and baseline, verify, and compare modes from [commit 5528b54](https://github.com/bharathkumar0195/group3-realtime-inventory-management/commit/5528b54cc3cf5e44edf9ec4822206122716ce150).

Both contributed modules are under src, fixing their imports and inventory-file lookup. Verification now compares inventory state before and after every query. It also checks results against an independent full-catalog reference. Timed runs reconcile final quantities, product identifiers, low-stock membership, and transaction count. The earlier command delegates to one canonical runner.

All 29 tests pass: 10 inherited inventory tests, 12 urgency tests, and 7 generator/benchmark tests. The generator produces exactly the same product records and update sequences as the earlier runner at both required scales. The inventory implementation itself was unchanged by the benchmark integration at f901d09. Kamlesh's later text-validation refactor was merged through PR #2 at b3a7c63. It strips valid text once instead of twice; the dictionary, low-stock set, transaction list, and urgency algorithm are unchanged. All 29 tests pass on that merged code.

## Measurements

Python 3.11.16 on macOS ARM64 ran both algorithms on fresh, identical stores. Each timed repetition contains 500 queries with k=10 interleaved with 500 updates. The table uses medians of three repetitions; setup, verification, printing, and profiling are outside timing.

| Products | Run | Full sort | Heap selection | Speedup |
|---|---|---:|---:|---:|
| 10,000 | Earlier runner | 1.007 s | 0.355 s | 2.83x |
| 10,000 | Before validation merge (f901d09) | 0.927 s | 0.333 s | 2.78x |
| 10,000 | After validation merge (b3a7c63) | 0.904 s | 0.320 s | 2.82x |
| 100,000 | Earlier runner | 15.601 s | 5.901 s | 2.64x |
| 100,000 | Before validation merge (f901d09) | 15.914 s | 5.877 s | 2.71x |
| 100,000 | After validation merge (b3a7c63) | 14.061 s | 4.681 s | 3.00x |

The optimization is heap selection compared with full sorting within each run. Combining the runners improves reuse and validation; it does not introduce another algorithm improvement. Differences between process runs can reflect machine activity and set iteration order. The before/after-validation rows do not isolate the helper's effect; their speedup column always compares full sorting with heap selection within the same run.

Seed 532 generates quantities from 0 through 40 with minimum stock 20. The first 250 products start at 20 and each receive +1 then -2, crossing the threshold in both directions. Seeded records do not fix Python hash randomization. Initially 5,226 of 10,000 and 51,099 of 100,000 products are low stock.

Raw evidence: [current samples](results/current/phase3_benchmark.csv), [current baseline profile](results/current/phase3_benchmark-100000-sort-profile.txt), [current heap profile](results/current/phase3_benchmark-100000-heap-profile.txt), and [earlier samples](results/earlier/urgent_benchmark.csv). The earlier run was published in commit 38e8d9e. The pre-validation-merge CSV remains in [commit f901d09](https://github.com/bharathkumar0195/group3-realtime-inventory-management/blob/f901d09052495de7dd34b5981e979e59b7b43768/results/current/phase3_benchmark.csv). Current samples were rerun after the validation merge and carry the updated inventory checksum. Profiles include instrumentation overhead and are separate from the timing table.

## Trade-offs and limits

The query avoids maintaining a permanent ranking index, so stock updates need no new index work. It scans low-stock records on each call. Memory bounds are algorithmic analysis; memory usage was not measured. Results cover one synthetic distribution and one machine. Stronger read-only checks increase verification time outside the timed workload.

The system remains in memory and single-process. Product records are mutable, so callers must use manager methods for stock changes. Any separate instructor-supplied dataset or harness still requires its own validation. These results support the code handoff; final optimization notes, the required appendix, live defense, and phase freeze remain separate deliverables.

Use the [run guide](PHASE3_RUN.md) to reproduce the tests, measurements, and profiles.
