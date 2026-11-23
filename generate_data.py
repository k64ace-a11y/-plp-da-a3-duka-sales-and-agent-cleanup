"""Dataset generators for the PLP Week 3 assignment.

Run `python generate_data.py` to (re)create the raw CSVs:
  * agents.csv, agent_transactions.csv  (Engagement 2, seed 44)
  * duka_sales.csv                      (Engagement 1, seed 2026)

The raw CSVs are NOT committed; the checker regenerates them from this file.
"""
import numpy as np, pandas as pd


def generate_agent_network():
    # ---- Engagement 2 · Mobile money agent network (seed 44) -- UNCHANGED ----
    rng = np.random.default_rng(44)
    n = 600
    agents = pd.DataFrame({
        "agent_id": [f"AG{i:03d}" for i in range(1, 21)],
        "county": rng.choice(["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"], 20),
        "onboarded": pd.date_range("2024-01-01", periods=20, freq="MS")
                       .strftime("%Y-%m-%d"),
    })
    txns = pd.DataFrame({
        "txn_id": [f"TX{i:05d}" for i in range(1, n + 1)],
        "agent_id": rng.choice(agents["agent_id"], n),
        "txn_type": rng.choice(["Deposit", "withdrawal", "DEPOSIT ",
                                "Withdrawal", "deposit"], n),
        "amount": rng.lognormal(7.5, 0.8, n).round(0).astype(str),
        "txn_date": (pd.to_datetime("2026-03-01")
                     + pd.to_timedelta(rng.integers(0, 60, n), unit="D"))
                    .strftime("%Y-%m-%d"),
    })
    idx = rng.choice(n, 30, replace=False)
    txns.loc[idx[:15], "amount"] = np.nan
    txns.loc[idx[15:20], "amount"] = "N/A"
    txns.loc[idx[20:25], "amount"] = "250000"
    txns.loc[idx[25:], "txn_date"] = txns.loc[idx[25:], "txn_date"].str.replace("-", "/")
    txns = pd.concat([txns, txns.sample(12, random_state=1)], ignore_index=True)
    txns.loc[rng.choice(len(txns), 8, replace=False), "agent_id"] = "AG099"
    agents.to_csv("agents.csv", index=False)
    txns.to_csv("agent_transactions.csv", index=False)


def generate_duka_sales():
    # ---- Engagement 1 · Duka Electronics (seed 2026) ----
    # TODO: paste the Week 3 Practicals generator here UNCHANGED (seed 2026,
    # 1,000 orders, writes duka_sales.csv).
    raise NotImplementedError("Paste the Duka Electronics generator here.")


if __name__ == "__main__":
    generate_agent_network()
    try:
        generate_duka_sales()
    except NotImplementedError as e:
        print("Skipped Duka:", e)
