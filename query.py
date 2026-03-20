import sqlite3
import pandas as pd

conn = sqlite3.connect("kaudit.db")

df = pd.read_sql("""
    SELECT merchant, SUM(amount) as total_spent
    FROM transactions
    WHERE merchant != 'Starting Balance'
    GROUP BY merchant
    ORDER BY total_spent DESC
    LIMIT 10
""", conn)

print(df)

df2 = pd.read_sql("""
    SELECT semester, net_balance, dues_per_brother
    FROM audit_runs
    ORDER BY run_date
""", conn)

print(df2)

conn.close()