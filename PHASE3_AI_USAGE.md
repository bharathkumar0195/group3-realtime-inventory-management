# Phase 3 AI Usage Appendix

OpenAI Codex assisted with implementation planning, the urgency-query method, automated tests, and local validation. This entry covers the query contribution; benchmark and other team contributions should be recorded as they are completed.

Significant prompts:

- "okay give me a true implementation plan"
- "ok go download it and run it independently, lmk what u find. separate from rest of the plan"
- "ok lets create a new branch and create that method so others can reuse"

An early complexity explanation stated O(m log k) without separately explaining the boundary cases. That statement is incomplete for k=0 and k=1. The implementation returns immediately for k=0 and scans the eligible records for k=1. For small k greater than one, heap selection takes O(m log k); returning all m eligible records in order takes O(m log m). The tests also use a full-catalog reference rather than trusting the low-stock set, so an incorrect eligibility index cannot silently validate itself.

The inherited tests and new query tests pass locally. Required scale benchmarks, the complete Phase 3 handoff, and team preparation for the live defense remain pending.
