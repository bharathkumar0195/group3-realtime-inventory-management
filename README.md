# Real-Time Inventory Management System — Group 3

Phase 3: see [the run guide](PHASE3_RUN.md) for the urgency query, tests, seeded benchmark, and profiling commands.

**Course residency / Phase 1 design package (November 6, 2026).**

## Purpose
Design a small Python command-line inventory program supporting product registration, SKU lookup, inventory adjustments, low-stock alerts, and reports. "Real-time" means in-process immediate updates, **not** a production multi-user or distributed system.

## Files
- `DESIGN_BRIEF.md` — two-page-target design, assumptions, complexity and alternative structures.
- `HANDOFF.md` — next-team implementation contract, tests, and exact boundary.
- `AI_USAGE.md` — disclosure template requiring the team's factual review.
- `PITCH_NOTES.md` — lightning-pitch outline and questions.
- `requirements.txt` — no third-party packages planned for Phase 2.

## Phase plan
1. Friday: design and pitch, freeze Git tag.
2. Saturday morning: inherited team implements proof of concept.
3. Saturday afternoon: inherited team optimizes/measures.
4. Sunday: inherited team audits and presents.

## Repository management
Professor and next-phase team must receive access. Submit repository URL and immutable Phase 1 tag by the professor's stated deadline.


**Blackboard Phase 1 submission:** Use `Group3_Phase1_Design_Brief_APA.docx` for the APA-formatted written brief, plus `Group3_AI_Usage_Appendix_APA.docx`. The Markdown documents are GitHub-readable companion artifacts. Verify required Blackboard submission format with the professor.


## Project files

```text
project-folder/
├── src/                       # If your repository uses a src folder
│   ├── app.py                 # Streamlit UI
│   ├── inventory.py           # Core inventory business logic
│   └── test_inventory.py      # Unit tests
├── requirements.txt           # Python dependencies (can also be inside src/)
└── README.md

```bash
python -m pip install -r requirements.txt
```

If it is one level above `src/`, use `python -m pip install -r ../requirements.txt`. You do **not** need Pandas or NumPy for the current UI's tables.
```

The remaining quantity is **3**, so the laptop is flagged as low stock. Type `exit()` to leave Python.

## Run the web UI

With your virtual environment active, run this command **from the directory containing `app.py`**:


python -m streamlit run app.py


Open **http://localhost:8501** if your browser does not open automatically. Use the left sidebar to switch between the seven features.

The UI starts with four example products (Laptop, Phone, Keyboard, and Mouse) so you can demo immediately. The Mouse starts in low-stock status.

## Run automated tests

From the directory containing `test_inventory.py`:

```bash
python -m unittest -v test_inventory.py
```

The test suite checks product lookup, duplicate SKU prevention, stock adjustments, overselling, low-stock thresholds, invalid inputs, and report sorting.

## How it works

| Data structure | Used for | Typical complexity |
|---|---|---|
| Dictionary (`products`) | Product lookup by SKU | O(1) average |
| Set (`low_stock`) | Add/remove/check low-stock SKUs | O(1) average |
| List (`transactions`) | Append successful stock adjustments | O(1) amortized append |

The inventory report sorts products in **O(n log n)** time, and the low-stock report sorts flagged SKUs in **O(k log k)** time. Filtering history by SKU takes **O(t)** time, where `t` is the number of transactions.



## Troubleshooting

**`requirements.txt` not found:** You are in the wrong folder or do not have the file. Install Streamlit directly using `python -m pip install streamlit==1.35.0`, or point `-r` to the correct path.

**`ModuleNotFoundError: streamlit`:** Activate the virtual environment and run `python -m pip install streamlit==1.35.0`.

**`ModuleNotFoundError: inventory`:** Put `app.py` and `inventory.py` in the same directory and run Streamlit from that directory.

**`ValueError: numpy.dtype size changed`:** Your Anaconda/Pandas/NumPy environment has conflicting compiled packages. Create a fresh virtual environment as shown above and run Streamlit from it. The UI intentionally avoids `st.dataframe()` and does not require Pandas for its tables.

**Port 8501 already in use:** Run `python -m streamlit run app.py --server.port 8502` and visit http://localhost:8502.

## Limitations

This is a **single-process, in-memory prototype**. Inventory and transaction history are not saved to a database or file. The Streamlit app stores state in the current browser session, so restarting or resetting that session can lose changes. CSV downloads are exports, not persistent storage.

## Technologies

- Python 3.9+
- Streamlit
- Python standard library: `dataclasses`, `datetime`, `typing`, `unittest`, `csv`, and `io`

