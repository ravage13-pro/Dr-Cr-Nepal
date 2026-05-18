# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
import uuid
from streamlit_gsheets import GSheetsConnection

DEFAULT_COLUMNS = ["ID", "Date", "Description", "Category", "Type", "Amount"]

# Sales Sheet Columns: [Date, Customer_Name, Customer_Phone, Total_Amount, Amount_Paid, Balance_Due, ID, Type]
SALES_COLUMNS = ["Date", "Customer_Name", "Customer_Phone", "Total_Amount", "Amount_Paid", "Balance_Due", "ID", "Type"]

# Purchases Sheet Columns: [Date, Supplier_Name, Supplier_Phone, Total_Amount, Amount_Paid, Balance_Due, ID, Type]
PURCHASES_COLUMNS = ["Date", "Supplier_Name", "Supplier_Phone", "Total_Amount", "Amount_Paid", "Balance_Due", "ID", "Type"]

def get_connection():
    """
    Establish and return the GSheetsConnection.
    """
    return st.connection("gsheets", type=GSheetsConnection)

def validate_sheet_exists() -> bool:
    """
    Checks if the Google Sheet exists and is accessible.
    Returns True if accessible, False otherwise.
    """
    try:
        # Check secrets first
        if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
            return False
        
        gsheets_secrets = st.secrets["connections"]["gsheets"]
        required_keys = ["spreadsheet", "type", "project_id", "private_key", "client_email"]
        if not all(k in gsheets_secrets and gsheets_secrets[k] not in ("", None) for k in required_keys):
            return False
            
        # Try to connect and perform a minimal read
        conn = get_connection()
        df = conn.read(ttl="1s")
        return df is not None
    except Exception:
        return False

# ==============================================================================
# GENERAL CASH LEDGER FUNCTIONS (SHEET 1)
# ==============================================================================

def fetch_udharo_list() -> pd.DataFrame:
    """
    Fetches the latest 'Udharo' (Credit Sales / Payment Receivable) list from the Google Sheet (Sheet1).
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet does not exist or is not accessible.")
        
    conn = get_connection()
    df = conn.read(ttl="1s")
    
    if df is None or df.empty:
        return pd.DataFrame(columns=DEFAULT_COLUMNS)
        
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    for col in DEFAULT_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[DEFAULT_COLUMNS]
    
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df["Type"] = df["Type"].fillna("Debit")
    df["Category"] = df["Category"].fillna("Miscellaneous")
    df["Description"] = df["Description"].fillna("")
    
    udharo_df = df[
        (df["Type"].str.lower() == "credit") | 
        (df["Type"].str.lower() == "udharo") |
        (df["Description"].str.lower().str.contains("udharo", na=False)) |
        (df["Category"].str.lower().str.contains("udharo", na=False))
    ].copy()
    
    return udharo_df

def fetch_receipt_payable_list() -> pd.DataFrame:
    """
    Fetches the latest 'Receipt Payable' (Credit Purchases / Accounts Payable) list from the Google Sheet (Sheet1).
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet does not exist or is not accessible.")
        
    conn = get_connection()
    df = conn.read(ttl="1s")
    
    if df is None or df.empty:
        return pd.DataFrame(columns=DEFAULT_COLUMNS)
        
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    for col in DEFAULT_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[DEFAULT_COLUMNS]
    
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df["Type"] = df["Type"].fillna("Debit")
    df["Category"] = df["Category"].fillna("Miscellaneous")
    df["Description"] = df["Description"].fillna("")
    
    payable_df = df[
        (df["Type"].str.lower() == "receipt payable") | 
        (df["Type"].str.lower() == "payable") |
        (df["Description"].str.lower().str.contains("payable", na=False)) |
        (df["Category"].str.lower().str.contains("payable", na=False))
    ].copy()
    
    return payable_df

def append_transaction(description: str, category: str, tx_type: str, amount: float, date=None, tx_id=None) -> pd.DataFrame:
    """
    Core function to append any transaction to the main cash ledger sheet (Sheet1).
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet does not exist or is not accessible. Cannot write.")
        
    if not description.strip():
        raise ValueError("Description is required.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    if not tx_type or not tx_type.strip():
        raise ValueError("Transaction Type is required.")
        
    conn = get_connection()
    df = conn.read(ttl="1s")
    
    if df is None:
        df = pd.DataFrame(columns=DEFAULT_COLUMNS)
    else:
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        for col in DEFAULT_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[DEFAULT_COLUMNS]
        
    if date is None:
        date = datetime.date.today()
    if isinstance(date, (datetime.date, datetime.datetime)):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)
        
    if tx_id is None:
        tx_id = f"tx-{uuid.uuid4().hex[:6]}"
        
    new_entry = {
        "ID": tx_id,
        "Date": date_str,
        "Description": description.strip(),
        "Category": category,
        "Type": tx_type.strip(),
        "Amount": round(float(amount), 2)
    }
    
    updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    conn.update(data=updated_df)
    return updated_df

def append_sale(description: str, category: str, amount: float, date=None, tx_id=None, is_credit: bool = True) -> pd.DataFrame:
    tx_type = "Credit" if is_credit else "Cash Sale"
    return append_transaction(
        description=description,
        category=category,
        tx_type=tx_type,
        amount=amount,
        date=date,
        tx_id=tx_id
    )

def append_expense(description: str, category: str, amount: float, date=None, tx_id=None, is_credit: bool = True) -> pd.DataFrame:
    tx_type = "Receipt Payable" if is_credit else "Debit"
    return append_transaction(
        description=description,
        category=category,
        tx_type=tx_type,
        amount=amount,
        date=date,
        tx_id=tx_id
    )

# ==============================================================================
# SPECIALIZED UDHARO TRACKER FUNCTIONS (SALES & PURCHASES SHEETS)
# ==============================================================================

def fetch_sales_sheet() -> pd.DataFrame:
    """
    Fetches the entire 'Sales' worksheet (Customer Udharo Tracker).
    Columns: [Date, Customer_Name, Customer_Phone, Total_Amount, Amount_Paid, Balance_Due, ID, Type]
    """
    if not validate_sheet_exists():
        return pd.DataFrame(columns=SALES_COLUMNS)
        
    try:
        conn = get_connection()
        df = conn.read(worksheet="Sales", ttl="5s")
        
        if df is None or df.empty:
            return pd.DataFrame(columns=SALES_COLUMNS)
            
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        for col in SALES_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[SALES_COLUMNS]
        
        # Clean data types
        df["Total_Amount"] = pd.to_numeric(df["Total_Amount"], errors="coerce").fillna(0.0)
        df["Amount_Paid"] = pd.to_numeric(df["Amount_Paid"], errors="coerce").fillna(0.0)
        df["Balance_Due"] = pd.to_numeric(df["Balance_Due"], errors="coerce").fillna(0.0)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["Customer_Name"] = df["Customer_Name"].fillna("Unknown Customer")
        df["Customer_Phone"] = df["Customer_Phone"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
        df["Type"] = df["Type"].fillna("Udharo")
        
        return df
    except Exception:
        return pd.DataFrame(columns=SALES_COLUMNS)

def fetch_purchases_sheet() -> pd.DataFrame:
    """
    Fetches the entire 'Purchases' worksheet (Supplier Udharo Tracker).
    Columns: [Date, Supplier_Name, Supplier_Phone, Total_Amount, Amount_Paid, Balance_Due, ID, Type]
    """
    if not validate_sheet_exists():
        return pd.DataFrame(columns=PURCHASES_COLUMNS)
        
    try:
        conn = get_connection()
        df = conn.read(worksheet="Purchases", ttl="5s")
        
        if df is None or df.empty:
            return pd.DataFrame(columns=PURCHASES_COLUMNS)
            
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        for col in PURCHASES_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[PURCHASES_COLUMNS]
        
        # Clean data types
        df["Total_Amount"] = pd.to_numeric(df["Total_Amount"], errors="coerce").fillna(0.0)
        df["Amount_Paid"] = pd.to_numeric(df["Amount_Paid"], errors="coerce").fillna(0.0)
        df["Balance_Due"] = pd.to_numeric(df["Balance_Due"], errors="coerce").fillna(0.0)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df["Supplier_Name"] = df["Supplier_Name"].fillna("Unknown Supplier")
        df["Supplier_Phone"] = df["Supplier_Phone"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
        df["Type"] = df["Type"].fillna("Udharo")
        
        return df
    except Exception:
        return pd.DataFrame(columns=PURCHASES_COLUMNS)

def append_sales_record(customer_name: str, customer_phone: str, total_amount: float, amount_paid: float, is_credit: bool = True, date=None, tx_id=None) -> pd.DataFrame:
    """
    Appends a new record to the 'Sales' worksheet.
    Balance_Due is auto-computed as: Total_Amount - Amount_Paid
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet does not exist or is not accessible.")
        
    if not customer_name.strip():
        raise ValueError("Customer Name is required.")
        
    df = fetch_sales_sheet()
    
    if date is None:
        date = datetime.date.today()
    if isinstance(date, (datetime.date, datetime.datetime)):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)
        
    if tx_id is None:
        tx_id = f"tx-s-{uuid.uuid4().hex[:6]}"
        
    total_val = round(float(total_amount), 2)
    paid_val = round(float(amount_paid), 2)
    due_val = round(total_val - paid_val, 2)
    tx_type = "Udharo" if is_credit else "Cash"
    
    new_entry = {
        "Date": date_str,
        "Customer_Name": customer_name.strip(),
        "Customer_Phone": str(customer_phone).strip(),
        "Total_Amount": total_val,
        "Amount_Paid": paid_val,
        "Balance_Due": due_val,
        "ID": tx_id,
        "Type": tx_type
    }
    
    updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    conn = get_connection()
    conn.update(worksheet="Sales", data=updated_df)
    return updated_df

def append_purchases_record(supplier_name: str, supplier_phone: str, total_amount: float, amount_paid: float, is_credit: bool = True, date=None, tx_id=None) -> pd.DataFrame:
    """
    Appends a new record to the 'Purchases' worksheet.
    Balance_Due is auto-computed as: Total_Amount - Amount_Paid
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet does not exist or is not accessible.")
        
    if not supplier_name.strip():
        raise ValueError("Supplier Name is required.")
        
    df = fetch_purchases_sheet()
    
    if date is None:
        date = datetime.date.today()
    if isinstance(date, (datetime.date, datetime.datetime)):
        date_str = date.strftime("%Y-%m-%d")
    else:
        date_str = str(date)
        
    if tx_id is None:
        tx_id = f"tx-p-{uuid.uuid4().hex[:6]}"
        
    total_val = round(float(total_amount), 2)
    paid_val = round(float(amount_paid), 2)
    due_val = round(total_val - paid_val, 2)
    tx_type = "Udharo" if is_credit else "Cash"
    
    new_entry = {
        "Date": date_str,
        "Supplier_Name": supplier_name.strip(),
        "Supplier_Phone": str(supplier_phone).strip(),
        "Total_Amount": total_val,
        "Amount_Paid": paid_val,
        "Balance_Due": due_val,
        "ID": tx_id,
        "Type": tx_type
    }
    
    updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    conn = get_connection()
    conn.update(worksheet="Purchases", data=updated_df)
    return updated_df

def settle_customer_debt(tx_id: str, amount_settled: float) -> pd.DataFrame:
    """
    Partially or fully settles a customer debt by ID.
    Increments Amount_Paid and decrements Balance_Due accordingly.
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet is not accessible.")
        
    df = fetch_sales_sheet()
    if df.empty:
        raise ValueError("No customer records found.")
        
    matching_idx = df[df["ID"] == tx_id].index
    if matching_idx.empty:
        raise ValueError(f"No transaction found with ID: {tx_id}")
        
    idx = matching_idx[0]
    total_amount = float(df.at[idx, "Total_Amount"])
    current_paid = float(df.at[idx, "Amount_Paid"])
    
    new_paid = round(current_paid + float(amount_settled), 2)
    if new_paid > total_amount:
        new_paid = total_amount # Cannot pay more than owed
        
    df.at[idx, "Amount_Paid"] = new_paid
    df.at[idx, "Balance_Due"] = round(total_amount - new_paid, 2)
    
    # Save back dates and clean formatting
    df["Date"] = df["Date"].astype(str)
    
    conn = get_connection()
    conn.update(worksheet="Sales", data=df)
    return df

def settle_supplier_debt(tx_id: str, amount_settled: float) -> pd.DataFrame:
    """
    Partially or fully settles a supplier debt by ID.
    Increments Amount_Paid and decrements Balance_Due accordingly.
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet is not accessible.")
        
    df = fetch_purchases_sheet()
    if df.empty:
        raise ValueError("No supplier records found.")
        
    matching_idx = df[df["ID"] == tx_id].index
    if matching_idx.empty:
        raise ValueError(f"No transaction found with ID: {tx_id}")
        
    idx = matching_idx[0]
    total_amount = float(df.at[idx, "Total_Amount"])
    current_paid = float(df.at[idx, "Amount_Paid"])
    
    new_paid = round(current_paid + float(amount_settled), 2)
    if new_paid > total_amount:
        new_paid = total_amount # Cannot pay more than owed
        
    df.at[idx, "Amount_Paid"] = new_paid
    df.at[idx, "Balance_Due"] = round(total_amount - new_paid, 2)
    
    # Save back dates and clean formatting
    df["Date"] = df["Date"].astype(str)
    
    conn = get_connection()
    conn.update(worksheet="Purchases", data=df)
    return df

def clear_customer_debt(tx_id: str) -> pd.DataFrame:
    """
    Fully clears a customer's debt by setting Amount_Paid to Total_Amount.
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet is not accessible.")
        
    df = fetch_sales_sheet()
    if df.empty:
        raise ValueError("No customer records found.")
        
    matching_idx = df[df["ID"] == tx_id].index
    if matching_idx.empty:
        raise ValueError(f"No transaction found with ID: {tx_id}")
        
    idx = matching_idx[0]
    total_amount = float(df.at[idx, "Total_Amount"])
    
    df.at[idx, "Amount_Paid"] = total_amount
    df.at[idx, "Balance_Due"] = 0.0
    
    df["Date"] = df["Date"].astype(str)
    
    conn = get_connection()
    conn.update(worksheet="Sales", data=df)
    return df

def clear_supplier_debt(tx_id: str) -> pd.DataFrame:
    """
    Fully clears a supplier's debt by setting Amount_Paid to Total_Amount.
    """
    if not validate_sheet_exists():
        raise FileNotFoundError("Google Sheet is not accessible.")
        
    df = fetch_purchases_sheet()
    if df.empty:
        raise ValueError("No supplier records found.")
        
    matching_idx = df[df["ID"] == tx_id].index
    if matching_idx.empty:
        raise ValueError(f"No transaction found with ID: {tx_id}")
        
    idx = matching_idx[0]
    total_amount = float(df.at[idx, "Total_Amount"])
    
    df.at[idx, "Amount_Paid"] = total_amount
    df.at[idx, "Balance_Due"] = 0.0
    
    df["Date"] = df["Date"].astype(str)
    
    conn = get_connection()
    conn.update(worksheet="Purchases", data=df)
    return df
