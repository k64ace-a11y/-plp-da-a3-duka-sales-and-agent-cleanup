# PLP Data Analytics Assignment 3 — Duka Sales and Agent Cleanup

## Project contents
- `generate_data.py` — reproducible generators for Duka Electronics and the mobile-money agent network.
- `duka_sales_exploration.ipynb` — sales exploration, Tasks 1–8 and executive summary.
- `agent_cleanup.ipynb` — audit, cleaning, merge validation, summaries and Data Quality Report.
- `cleaning_pipeline.py` — reusable `clean_agent_data(txns, agents)` function and cleaning log.
- `excel/duka_branch_summary.xlsx` — source table, SUMIFS branch summary, XLOOKUP region, and branch-by-channel formula cross-tab.
- `outputs/premium_online_coast_capital.csv` — filtered Duka orders, saved without an index.
- `outputs/agent_transactions_clean.csv` — cleaned agent transactions, including flags and county.

## Important note about the Duka generator
The assignment brief supplied the complete mobile-money generator but did not include the Duka Electronics generator from the Practical. To make this project runnable, `generate_data.py` contains a clearly documented, reproducible reconstruction of a 1,000-order Duka dataset using seed `2026`. It uses an explicit schema (`order_id`, `order_date`, `branch`, `city`, `product`, `channel`, `units`, `unit_price`). This reconstruction may not match the exact columns or results expected by the PLP checker if the Practical used a different original generator. Replace `generate_duka_sales()` with the official Practical version if you can obtain it. The agent generator follows the supplied assignment code.

## Setup
Use Python 3.10 or later.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Regenerate source data
From the repository root:

```bash
python generate_data.py
```

This creates `duka_sales.csv`, `agents.csv`, and `agent_transactions.csv` in the project root. Raw generated CSVs are intentionally not committed.

## Run the notebooks
Start Jupyter from the repository root:

```bash
jupyter notebook
```

Run `duka_sales_exploration.ipynb` and `agent_cleanup.ipynb` from top to bottom. The notebooks read the raw CSVs from the project root and write the deliverables into `outputs/`. Restart the kernel and use **Run All** before committing so all outputs are visible.

## Duka Executive Summary
- Duka Electronics recorded 1,000 orders between January and June 2026.
- The highest-revenue branch was Nairobi CBD, generating KES 14,101,258.
- The top-revenue product was Laptop, contributing KES 18,280,437.
- Weekend orders totalled 302, compared with 698 weekday orders.
- Premium online orders from Nairobi and Mombasa numbered 117 and generated KES 9,588,486.

## Agent data row counts
- Original generated transactions: **600**.
- Duplicate rows appended by the supplied generator: **12**.
- Raw transaction extract: **612 rows**.
- Unique transaction IDs after deduplication: **600 rows**.
- Cleaned output: **600 rows**.
- Transactions with unknown agents: **7** (retained with county `Unknown`).

## Spreadsheet note
The workbook includes an Excel source table, a branch summary with `SUMIFS`-based revenue and an `XLOOKUP` region formula, plus a formula-driven branch-by-channel cross-tab whose totals reconcile to the notebook. The cross-tab is a PivotTable-style summary, not an embedded Excel-native PivotTable object. If the assessor requires a native PivotTable object, open the workbook in desktop Excel, select the `DukaSales` table, choose **Insert → PivotTable**, place `branch` in Rows, `channel` in Columns and `revenue` (or a calculated revenue field) in Values, then save the workbook.

## Privacy and governance
Do not publish real customer phone numbers, names, account identifiers or other personal data. Restrict access to raw extracts, minimise and mask identifiers, encrypt files, limit retention and document the lawful basis and purpose for processing under the Kenya Data Protection Act, 2019.

## Dependencies
The analysis notebooks and data generators use `pandas` and `numpy`.
