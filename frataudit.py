import glob 
import pandas as pd
import numpy as np
import sqlite3
import os
import re
import sys
import PyPDF2
import matplotlib.pyplot as plt
import db
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ----- Data Collection ------
try:
    rollover_amount = float(input("Enter the treasury starting balance (Input value only no dollar signs or commas): "))
    card_rollover = float(input("Enter the total starting balance for the cards (Input value only no dollar signs or commas): "))
    extra_heads = int(input("Enter the total number of alumni brothers and inactive/removed brothers in roster: "))
    nibs_inbound = int(input("Enter number of initiates you expected to be billed for: "))
except ValueError:
    print("Error: Invalid input, and no way you put a fraction of a brother. Input the value only, no dollar signs or commas.")
    sys.exit(1)

# Grabs transaction details in cards 
try:
    transaction_dfs = []
    for one_filename in glob.glob('transactions/*.csv'): 
        print(f'Loading {one_filename}')
        new_df = pd.read_csv(one_filename, 
                            usecols=['Date', 'Merchant', 'Amount', 'Balance'], 
                            skiprows=[1])
        new_df['Card_Source'] = one_filename
        transaction_dfs.append(new_df)

    if not transaction_dfs:
        raise FileNotFoundError
    
    transaction_dfs_df = pd.concat(transaction_dfs, ignore_index=True)
    
    transaction_dfs_df = transaction_dfs_df.drop_duplicates(subset=['Date', 'Merchant', 'Amount', 'Balance'])
    
    transaction_dfs_df['Amount'] = transaction_dfs_df['Amount'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
    
    transaction_dfs_df.loc[transaction_dfs_df['Merchant'].str.contains('KAPPA SIGMA', case=False, na=False), 'Merchant'] = 'KAPPA SIGMA HQ'
    
    transaction_dfs_df.loc[transaction_dfs_df['Merchant'].str.contains('Transfer from', case=False, na=False), 'Amount'] *= -1
    
    transaction_dfs_df.loc[~transaction_dfs_df['Merchant'].str.contains('Transfer', case=False, na=False), 'Amount'] *= -1
    
    card_rollover_row = pd.DataFrame([{
        'Merchant': 'Starting Balance', 
        'Amount': card_rollover
    }])
    
    grouped_transaction_df = pd.concat([card_rollover_row, transaction_dfs_df], ignore_index=True)
    
    net_transaction_df = grouped_transaction_df.groupby('Merchant')['Amount'].sum().reset_index()
    
    net_transactions = net_transaction_df['Amount'].sum()
    
    print(f"Net transaction balance of: ${net_transactions:,.2f}")
    print(grouped_transaction_df)
    
except FileNotFoundError:
    print("Error: Insert valid transaction file in the folder.")
    sys.exit(1)
except ValueError:
    print("Error: Invalid input. Input the value only, no dollar signs or commas.")
    sys.exit(1)
    
#Grabs roster of active brothers and calculates Total HQ and per brother dues
try:
    roster_list = []
    for filename in glob.glob('roster/*.csv'):
        print(f'Loading roster: {filename}')
        df = pd.read_csv(filename)
        roster_list.append(df)
        
    if not roster_list:
        raise FileNotFoundError
    
    roster_df = pd.concat(roster_list, ignore_index=True)
    
    roster_df = roster_df.drop_duplicates(subset=['First name', 'Last name', 'Email'])
    
    headcount = len(roster_df) - extra_heads

    if headcount <= 35: 
        hq_fees = 7950
        hq_fees += 10.34 * headcount
    elif headcount > 35:
        hq_fees = 10.34 * headcount
        hq_fees += 1300
        hq_fees += 190 * headcount
        
    total_due = hq_fees
    dues_per_brother = total_due / headcount
    
    print(f"Total brothers across all files: {headcount}")
    print(f"Total HQ Due: ${total_due:,.2f}")
    print(f"Per Brother: ${dues_per_brother:,.2f}")

except FileNotFoundError:
    print("Error: Insert valid file in the roster folder.")
    sys.exit(1)
except ValueError:
    print("Error: Invalid input. Enter a whole number only.")
    sys.exit(1)

# Grabs tresury details, net balance
try:
    treasury_dfs = []
    for one_filename in glob.glob('treasury/*.csv'): 
        print(f'Loading {one_filename}')
        new_df = pd.read_csv(one_filename, 
                            usecols=['Date', 'Status', 'Description', 'Amount', 'Balance'], 
                            skiprows=[1])
        treasury_dfs.append(new_df)

    if not treasury_dfs:
        raise FileNotFoundError
    
    treasury_dfs_df = pd.concat(treasury_dfs, ignore_index=True)
    
    treasury_dfs_df = treasury_dfs_df.drop_duplicates(subset=['Date', 'Status', 'Description', 'Amount', 'Balance'])
    
    treasury_dfs_df['Amount'] = treasury_dfs_df['Amount'].replace({r'\$': '', ',': ''}, regex=True).astype(float)
    
    rollover_row = pd.DataFrame([{
        'Status': 'Starting Balance', 
        'Description': 'Rollover from last semester', 
        'Amount': rollover_amount
    }])
    
    grouped_treasury_df = treasury_dfs_df.groupby(['Status', 'Description'])['Amount'].sum().reset_index()
    
    net_treasury_df = pd.concat([rollover_row, grouped_treasury_df], ignore_index=True)
    
    net_balance = net_treasury_df['Amount'].sum()
    
    print(f"Net balance of: ${net_balance:,.2f}")
    print(net_treasury_df)
    
except FileNotFoundError:
    print("Error: Insert valid file in the treasury folder.")
    sys.exit(1)
except ValueError:
    print("Error: Invalid input. Input the value only, no dollar signs or commas.")
    sys.exit(1)


#Audit time
# --- AUDIT FOR TREASURY AND CARD ---
treasury_dfs_df['Date'] = pd.to_datetime(treasury_dfs_df['Date'])
transaction_dfs_df['Date'] = pd.to_datetime(transaction_dfs_df['Date'])

start_date = treasury_dfs_df['Date'].min()
end_date = treasury_dfs_df['Date'].max() + pd.Timedelta(days=5) # change days for avg cash arrival time

audit_cards_df = transaction_dfs_df[
    (transaction_dfs_df['Date'] >= start_date) & 
    (transaction_dfs_df['Date'] <= end_date)
].copy()

bank_out = treasury_dfs_df[treasury_dfs_df['Description'].str.contains('Transfer to gMoney', case=False)]['Amount'].sum()

card_net_in = audit_cards_df[audit_cards_df['Merchant'].str.contains('Transfer', case=False)]['Amount'].sum()

cash_flow_delta = bank_out + card_net_in

if abs(cash_flow_delta) < 1:
    print(f"Net Delta is within limits: {cash_flow_delta:,.2f}")
elif abs(cash_flow_delta) >=1:
    print(f"DISCREPANCY: Net Delta is NOT within limits: {cash_flow_delta:,.2f}")

# --- AUDIT INVOICES ---
try:
    invoice_files = list(set(glob.glob('*.pdf') + glob.glob('ORDER*') + glob.glob('invoices/*.pdf')))
    
    if not invoice_files:
        print("No invoices found.")
    else:
        actual_nibs_billed = 0
        
        for inv in invoice_files:
            with open(inv, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            qty_pattern = r'(\d+\.\d{2})Dues:\s*([\w\s]+?)(?=\s\d+\.\d{2})'
            matches = re.findall(qty_pattern, text)
            
            for qty_str, desc in matches:
                qty_val = int(float(qty_str))
                if "UNDERGRADUATE DUES" in desc.upper() or "LIABILITY" in desc.upper():
                    if qty_val != headcount:
                        print(f"DISCREPANCY: Mismatch in {inv}. Billed {qty_val}, roster has {headcount}.")
                    else:
                        print(f"QTY matches headcount ({qty_val}) in {inv}")

            actual_nibs_billed += text.count("Initiate Fee")
    
        if actual_nibs_billed !=  nibs_inbound:
            print(f"DISCREPANCY: Billed for {actual_nibs_billed} NIBs, expected {nibs_inbound}.")
        else:
            print(f"All {actual_nibs_billed} initiate fees found correctly.")

except Exception as e:
    print(f"PDF Error: {e}")


# --- The SQL part ---
RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
SEMESTER = input("Enter semester (e.g. Fall2025, Spring2026): ").strip()

print(f"Audit started: {RUN_TIMESTAMP}")
print(f"Semester: {SEMESTER}")

db.init_db()
conn = db.get_connection()

transaction_dfs_df['semester'] = SEMESTER
transaction_dfs_df.to_sql('transactions', conn, if_exists='append', index=False)

treasury_dfs_df['semester'] = SEMESTER
treasury_dfs_df.to_sql('treasury', conn, if_exists='append', index=False)

conn.execute("""
    INSERT INTO audit_runs (run_date, semester, headcount, net_balance, net_transactions, cash_flow_delta, hq_fees, dues_per_brother)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (RUN_TIMESTAMP, SEMESTER, headcount, net_balance, net_transactions, cash_flow_delta, hq_fees, dues_per_brother))

conn.commit()
conn.close()