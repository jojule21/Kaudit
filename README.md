# Kaudit — Chapter Treasury Audit & Reconciliation Engine

A Python CLI tool that audits a fraternity chapter's finances end-to-end: it ingests card transaction exports, bank/treasury statements, the member roster, and national HQ invoice PDFs, then reconciles them against each other and flags discrepancies automatically.

Built while serving as Grand Treasurer of the Sigma Epsilon chapter of Kappa Sigma, where manual spreadsheet auditing had let billing errors slip through. Kaudit-driven audits surfaced **$1,300 in misclassified member charges** across a **$30,000 operating budget** and now back every semester's dues calculation.

## What it does

- **Card reconciliation** — merges every card CSV export, dedupes, normalizes merchant names and amounts, and nets balances against the starting rollover.
- **Treasury reconciliation** — aggregates bank statement activity by status/description and computes the true net balance.
- **Cash-flow audit** — matches bank-to-card transfers within the statement window (with a configurable settlement lag) and flags any delta over $1.00 as a `DISCREPANCY`.
- **Invoice audit** — parses HQ invoice PDFs with PyPDF2 and verifies that billed undergraduate-dues/liability quantities match the actual roster headcount, and that initiate fees billed match the expected pledge count.
- **Dues calculation** — applies Kappa Sigma HQ's tiered fee schedule to the deduped roster headcount and computes per-brother dues.
- **Audit trail** — every run is persisted to a dated SQLite database (`transactions`, `treasury`, and `audit_runs` tables), so each semester's numbers are queryable after the fact. `query.py` reports top merchants by spend and net-balance history across runs.

## Repo layout

| File | Purpose |
|---|---|
| `frataudit.py` | Main audit engine (run this) |
| `db.py` | SQLite schema + connection helpers |
| `query.py` | Reporting queries against the audit database |
| `duescalculator.py` | Standalone dues estimator (HQ fees + local budget) |
| `transactions/`, `treasury/`, `roster/`, `invoices/` | Drop your exports here (gitignored — see below) |
| `sample_data/` | Sanitized sample files so you can try it without real data |

## Quick start

```bash
pip install -r requirements.txt

# Try it with the included sample data:
cp sample_data/transactions_sample.csv transactions/
cp sample_data/treasury_sample.csv treasury/
cp sample_data/roster_sample.csv roster/

python frataudit.py
```

You'll be prompted for the treasury starting balance, card starting balance, inactive/alumni headcount adjustment, and expected initiate count. The audit prints net balances, dues, and any `DISCREPANCY` lines, then writes the run to `kaudit_<date>.db`.

```bash
python query.py   # top merchants + audit-run history
```

## Expected input formats

- `transactions/*.csv` — card exports with columns `Date, Merchant, Amount, Balance` (first data row is skipped, matching the bank's export header quirk)
- `treasury/*.csv` — bank exports with columns `Date, Status, Description, Amount, Balance`
- `roster/*.csv` — columns `First name, Last name, Email`
- `invoices/*.pdf` — HQ invoice PDFs

**Privacy:** real rosters, statements, and invoices are gitignored. Only sanitized samples are committed.

## Roadmap

- Unify the database filename between `db.py` (dated) and `query.py`
- Replace `input()` prompts with CLI flags (`argparse`)
- Export a per-semester discrepancy report to CSV
