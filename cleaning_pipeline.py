"""Reusable cleaning pipeline for the mobile-money agent network extract."""
import numpy as np
import pandas as pd

VALID_TYPES = {"deposit": "Deposit", "withdrawal": "Withdrawal"}
UNKNOWN_COUNTY = "Unknown"


def clean_agent_data(txns, agents):
    """Audit, clean and merge the agent transaction extract.

    Rules applied (in order), each recorded in the returned log:
      1. Uniqueness   - drop duplicate txn_id values, preferring the copy whose
                        agent_id exists in the register.
      2. Consistency  - standardise txn_type to exactly "Deposit" / "Withdrawal".
      3. Validity     - amount -> numeric (text such as "N/A" -> NaN);
                        txn_date -> datetime (handles "YYYY/MM/DD" and "YYYY-MM-DD").
      4. Outliers     - flag amounts outside the 1.5*IQR fences (is_outlier);
                        values are kept, never deleted.
      5. Completeness - impute missing amounts with the median of valid,
                        non-outlier amounts of the same txn_type and set
                        amount_imputed = True.
      6. Merge        - LEFT join to the agent register; unknown agents keep their
                        transactions with county = "Unknown" and unknown_agent = True.

    Parameters
    ----------
    txns : pandas.DataFrame
        Raw transactions (txn_id, agent_id, txn_type, amount, txn_date).
    agents : pandas.DataFrame
        Agent register (agent_id, county, onboarded).

    Returns
    -------
    (clean_df, log) : (pandas.DataFrame, pandas.DataFrame)
        The cleaned, merged transactions and a log with columns
        step, dimension, issue, rows_affected, action.
    """
    log = []

    def record(step, dimension, issue, rows, action):
        log.append({"step": step, "dimension": dimension, "issue": issue,
                    "rows_affected": int(rows), "action": action})

    df = txns.copy()
    reg = agents.copy()
    df["agent_id"] = df["agent_id"].astype(str).str.strip()
    reg["agent_id"] = reg["agent_id"].astype(str).str.strip()
    record(0, "Info", "Raw rows loaded", len(df), "none")

    # 1. Uniqueness -----------------------------------------------------------
    n_dup = df["txn_id"].duplicated().sum()
    conflicting = (df.drop_duplicates()["txn_id"].duplicated().sum())
    df["_known"] = df["agent_id"].isin(reg["agent_id"])
    df = (df.sort_values("_known", ascending=False, kind="stable")
            .drop_duplicates("txn_id", keep="first")
            .sort_values("txn_id").drop(columns="_known").reset_index(drop=True))
    record(1, "Uniqueness", "Duplicate txn_id rows", n_dup,
           f"Removed; {conflicting} duplicate(s) differed in another column and "
           "the copy with a registered agent_id was kept")

    # 2. Consistency ----------------------------------------------------------
    raw_type = df["txn_type"].astype(str)
    std_type = raw_type.str.strip().str.lower().map(VALID_TYPES)
    n_bad_type = (raw_type != std_type).sum()
    unmapped = std_type.isna().sum()
    if unmapped:
        raise ValueError(f"{unmapped} txn_type values could not be standardised")
    df["txn_type"] = std_type
    record(2, "Consistency", "txn_type spelling/case/whitespace variants", n_bad_type,
           "Stripped, lower-cased and mapped to Deposit/Withdrawal")

    # 3. Validity & types -----------------------------------------------------
    amt_raw = df["amount"]
    amt = pd.to_numeric(amt_raw, errors="coerce")
    n_text = (amt.isna() & amt_raw.notna()).sum()
    n_missing = amt.isna().sum()
    df["amount"] = amt
    record(3, "Validity", "Non-numeric amount text (e.g. 'N/A')", n_text,
           "Coerced to NaN (pandas may already have read these as missing)")

    date_raw = df["txn_date"].astype(str).str.strip()
    n_slash = date_raw.str.contains("/").sum()
    df["txn_date"] = pd.to_datetime(date_raw.str.replace("/", "-", regex=False),
                                    format="%Y-%m-%d", errors="coerce")
    n_bad_date = df["txn_date"].isna().sum()
    if n_bad_date:
        raise ValueError(f"{n_bad_date} unparseable txn_date values")
    record(3, "Validity", "txn_date written with '/' instead of '-'", n_slash,
           "Normalised and parsed to datetime (ISO yyyy-mm-dd on export)")

    # 4. Outliers (IQR on valid amounts) --------------------------------------
    q1, q3 = df["amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df["is_outlier"] = (df["amount"] < lo) | (df["amount"] > hi)
    record(4, "Accuracy", f"IQR outliers (fences {lo:,.0f} to {hi:,.0f})",
           df["is_outlier"].sum(), "Flagged is_outlier=True; values kept")
    record(4, "Accuracy", "Amount exactly 250,000 (suspected placeholder/cap)",
           (df["amount"] == 250000).sum(),
           "Flagged; recommend verification against source system before use")

    # 5. Completeness ---------------------------------------------------------
    valid = df.loc[~df["is_outlier"] & df["amount"].notna()]
    medians = valid.groupby("txn_type")["amount"].median()
    df["amount_imputed"] = df["amount"].isna()
    df["amount"] = df["amount"].fillna(df["txn_type"].map(medians))
    record(5, "Completeness", "Missing or invalid amount", n_missing,
           "Imputed with per-txn_type median of valid non-outlier amounts "
           f"(Deposit {medians['Deposit']:,.0f}, Withdrawal {medians['Withdrawal']:,.0f}); "
           "amount_imputed=True")

    # 6. Merge ----------------------------------------------------------------
    before = len(df)
    reg = reg.drop_duplicates("agent_id")
    out = df.merge(reg[["agent_id", "county", "onboarded"]], on="agent_id",
                   how="left", validate="m:1")
    assert len(out) == before, "merge changed the row count"
    out["unknown_agent"] = out["county"].isna()
    out["county"] = out["county"].fillna(UNKNOWN_COUNTY)
    record(6, "Consistency", "Transactions referencing agents not in register",
           out["unknown_agent"].sum(),
           f"Kept via left join; county='{UNKNOWN_COUNTY}', unknown_agent=True")
    record(7, "Info", "Clean rows returned", len(out), "none")

    out = out[["txn_id", "agent_id", "county", "onboarded", "txn_type", "amount",
               "txn_date", "amount_imputed", "is_outlier", "unknown_agent"]]
    return out.reset_index(drop=True), pd.DataFrame(log)
