# PLP Week 3 · Duka Sales & Agent Network Cleanup

Two client engagements from a Nairobi analytics consultancy, in one repository.

## Status
| Engagement | Status |
|---|---|
| 2 · Mobile-money agent network (audit, clean, merge, summarise) | **Complete** |
| 1 · Duka Electronics (sales exploration, Excel) | **Pending:** needs the Duka generator (seed 2026) from the Week 3 Practicals; see `generate_data.py` |

## Summary of the engagements
**Engagement 1 · Duka Electronics.** Explore 1,000 orders (Jan–Jun 2026) for the half-year review: derived columns, branch and product rankings, weekend vs weekday, best/worst month, Premium online orders from Nairobi/Mombasa, an Excel SUMIFS/XLOOKUP/PivotTable summary and a five-number Executive Summary. *(To be completed.)*

**Engagement 2 · Mobile-money agent network.** A legacy extract of 612 transactions across 20 agents / 5 counties was audited, cleaned and merged with the agent register. Issues found: 12 duplicate `txn_id`s (one disguised by a changed `agent_id`), 5 spellings of `txn_type`, 22 missing amounts (15 blank + 7 `N/A`), 5 dates with `/`, 5 suspicious amounts of exactly KES 250,000 (46.5 % of total value) and 8 rows for an unregistered agent `AG099`. The full audit, decisions, county summary, weekly pivot and one-page Data Quality Report (six dimensions + Kenya DPA 2019 privacy paragraph) are in `agent_cleanup.ipynb`.

### Agent data before-and-after row count
| Stage | Rows |
|---|---|
| Raw `agent_transactions.csv` | **612** |
| After removing duplicate `txn_id`s | **600** (12 removed) |
| After left merge with `agents.csv` | **600** (7 transactions with unknown agent `AG099`, kept as `county="Unknown"`) |

## Duka Executive Summary
*(To be pasted here from `duka_sales_exploration.ipynb` once Engagement 1 is complete.)*

## How to regenerate the data and run the notebooks
```bash
pip install -r requirements.txt jupyter
python generate_data.py                 # writes agents.csv, agent_transactions.csv (and duka_sales.csv)
jupyter nbconvert --to notebook --execute --inplace agent_cleanup.ipynb
jupyter nbconvert --to notebook --execute --inplace duka_sales_exploration.ipynb
```
Raw CSVs are git-ignored; only `outputs/` and `excel/` data files are committed. Before submitting, restart the kernel and run every notebook top to bottom.

## Repository layout
```
generate_data.py                      dataset generators (agent network seed 44; Duka seed 2026)
cleaning_pipeline.py                  clean_agent_data(txns, agents) -> (clean_df, log)
agent_cleanup.ipynb                   Engagement 2 notebook
duka_sales_exploration.ipynb          Engagement 1 notebook (pending)
excel/duka_branch_summary.xlsx        Engagement 1 workbook (pending)
outputs/agent_transactions_clean.csv  cleaned, merged transactions
outputs/premium_online_coast_capital.csv   (pending)
requirements.txt
```
