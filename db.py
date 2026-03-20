import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = f"kaudit_{datetime.now().strftime('%Y-%m-%d')}.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            merchant TEXT,
            amount REAL,
            balance REAL,
            card_source TEXT,
            semester TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS treasury (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            status TEXT,
            description TEXT,
            amount REAL,
            balance REAL,
            semester TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT DEFAULT (datetime('now')),
            semester TEXT,
            headcount INTEGER,
            net_balance REAL,
            net_transactions REAL,
            cash_flow_delta REAL,
            hq_fees REAL,
            dues_per_brother REAL
        )
    """)

    conn.commit()
    conn.close()