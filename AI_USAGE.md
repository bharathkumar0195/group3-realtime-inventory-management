# AI Usage Appendix — Group 3, Phase 1
**Project:** Real-Time Inventory Management System Using Python  
**AI tool used:** OpenAI ChatGPT  
**Purpose:** Transparently document AI assistance and critical evaluation of proposed designs.

## 1. How ChatGPT was used
ChatGPT was used as a drafting and brainstorming assistant to:
- Organize the professor's Phase 1 instructions into a design-and-handoff checklist.
- Help frame a manageable inventory-management application, its core functions, and initial workload assumptions.
- Compare candidate data structures and discuss expected Big-O time complexity and trade-offs.
- Draft a two-page design brief, a README, handoff instructions, and lightning-pitch talking points.
- Explain GitHub repository setup, collaboration, committing, and a frozen Phase 1 tag.

The application topic, **Real-Time Inventory Management System using Python**, was selected by Group 3. ChatGPT assisted with documenting and refining that topic; it did not independently make the group's final project choice.

## 2. AI-generated options considered and design decisions
The following are **design choices reflected in the current draft**. They should be checked and approved by the whole group before submission.

| Option considered with AI assistance | Current decision | Reason / trade-off |
|---|---|---|
| Python dictionary vs. unsorted list vs. balanced search tree for exact SKU lookup | Use a Python `dict` | Expected average O(1) exact lookup/update; list search is O(n); balanced tree adds implementation complexity and sorted ordering that is not needed for primary lookups. |
| Low-stock set vs. full inventory scans vs. a heap | Use a Python `set` of low-stock SKUs | Incremental membership updates are expected O(1); reporting k flagged SKUs is O(k) expected. Full scans cost O(n) per request; a heap is more suitable for ranked urgency than for simply listing all low-stock items. |
| Python list vs. linked list vs. deque for transaction history | Use a Python `list` | Amortized O(1) append is adequate for the append-oriented proof of concept; a custom linked list is unnecessary, while a deque offers little benefit without frequent front removals. |
| Full database, web dashboard, or distributed real-time synchronization | Keep a single-process, in-memory Python CLI for Phase 2 | The weekend exercise emphasizes data structures, algorithms, and manageable handoff; persistence, concurrent updates, and a production UI are beyond the proposed initial scope. |

These alternatives are not automatically “wrong.” They were *not selected for the stated workload and time constraints*. Different requirements could justify different structures.

## 3. AI recommendations: evaluation for final team confirmation
The following examples explain **why the current draft accepts or does not select** particular AI-assisted suggestions. They are recorded as proposed design reasoning, not as a claim that all five members have already voted or independently tested the system.

1. **Product lookup — accept Python `dict`.** ChatGPT compared a dictionary with an unsorted list and a balanced BST. For exact SKU queries, the dictionary's average O(1) lookup is appropriate. We did not select a list because finding a SKU could require an O(n) scan, or a balanced BST because ordered queries do not dominate this workload and a custom implementation would increase effort.
2. **Low-stock alerts — accept Python `set`; do not select a heap.** ChatGPT discussed a heap for prioritizing low-stock items. The stated requirement is to identify *all* items at or below their reorder threshold, not repeatedly remove the single most urgent item. Maintaining a set of flagged SKUs is simpler. This set must be updated whenever stock changes.
3. **Transaction history — accept Python `list`.** Append-only history benefits from amortized O(1) appends. A linked list requires custom nodes and a deque is useful if frequent removal from the front is introduced, neither of which is required for the initial design.
4. **Workload estimates — qualify, do not treat as verified.** ChatGPT proposed example frequencies and volumes. The figures in `DESIGN_BRIEF.md` remain *hypothetical assumptions*, not observed usage or measured throughput. Phase 3 should benchmark the working implementation before making performance claims.
5. **Project scope — simplify.** A database, web interface, or multi-user real-time synchronization might be suitable for production, but the current Phase 1 design intentionally uses an in-memory Python CLI for a manageable five-hour implementation handoff. The system does not persist after exit and has no concurrent-update guarantees.


## 4. Critical checks and limitations identified
- The workload figures (for example, 10,000 initial products, 100,000 future products, and estimated operations per second) are **hypothetical design assumptions**, not measured benchmarks or achieved performance.
- Python `dict` and `set` operations have **average-case**, not guaranteed worst-case, O(1) behavior.
- The low-stock set must be updated on every successful stock change; otherwise it can become inconsistent with product quantities.
- Rejecting invalid or overselling transactions is necessary to preserve the invariant `quantity >= 0`.
- "Real-time" means immediately updated state **within one running process**, not multi-user, networked, or persistent real-time guarantees.
- Phase 1 is a design deliverable. Working Python implementation and measured performance are for later project phases.

## 5. Human review and responsibility
ChatGPT produced draft material, not an independently verified implementation. Before the group submits, members should check the requirements against the instructor's rubric, confirm the proposed choices and assumed workload, check the final document length, and ensure the GitHub handoff is understandable. **Group 3 is responsible for its final technical decisions, presentation, and submissions.**

**Team confirmation before submission:** Review this appendix and remove or correct any statement that does not accurately describe how your team used AI or what your team decided.

## 6. Significant AI requests and specific AI correction (Blackboard requirement)
The following are **professionally edited summaries** of substantive requests to ChatGPT, **not verbatim quotations**. Original prompts can be consulted in the conversation history if an exact transcript is required.

1. How should Group 3 define the application scope and functional requirements for a Python-based real-time inventory management system?
2. Which workload characteristics, expected operation frequencies, data structures, and algorithmic trade-offs should the team evaluate and justify?
3. What design, handoff, version-control, and presentation documents are needed to meet the Phase 1 residency requirements?
4. How should the AI Usage Appendix explain accepted and rejected recommendations, errors identified in AI-generated work, and the required APA-formatted deliverables?

**Incorrect or incomplete AI guidance requiring correction:** The initial ChatGPT document package was described as final before the complete Blackboard requirements had been checked. It lacked the explicitly required APA presentation and at least three peer-reviewed references. This was not sufficient for the written design brief. The corrected package includes `Group3_Phase1_Design_Brief_APA.docx` with scholarly references and in-text citations. AI-proposed throughput figures are also explicitly labeled as assumptions rather than measured results. Review with the group before submission; do not claim benchmark testing or consensus without actually doing so.
