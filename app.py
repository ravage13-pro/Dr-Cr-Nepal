# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import uuid
import altair as alt
from streamlit_gsheets import GSheetsConnection
import db_logic

# ==============================================================================
# PAGE CONFIGURATION & AESTHETIC THEME INJECTION
# ==============================================================================
st.set_page_config(
    page_title="Dr-Cr Ledger - Google Sheets CRUD Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium Google Fonts and CSS for beautiful light, soft-tint elements
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0f172a;
    }
    
    /* Header Gradient Banner - Light Premium Blue */
    .header-banner {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        border: 1px solid rgba(79, 70, 229, 0.1);
        border-radius: 20px;
        padding: 30px 40px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.15);
        position: relative;
        overflow: hidden;
    }
    .header-banner::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    .header-title {
        color: #ffffff;
        font-size: 2.2rem;
        margin: 0;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    .header-subtitle {
        color: #e0e7ff;
        font-size: 1rem;
        margin-top: 8px;
        margin-bottom: 0;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* Clean Light Metric Cards */
    .metric-card-container {
        display: flex;
        gap: 20px;
        margin-bottom: 25px;
    }
    .metric-card {
        flex: 1;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.1);
        border-color: #cbd5e1;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 5px;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Theme Accents (Debit = Outflow = Red, Credit = Inflow = Green) */
    .debit-accent { border-left: 5px solid #ef4444; } /* Outflow (DR) - Red */
    .credit-accent { border-left: 5px solid #10b981; } /* Inflow (CR) - Green */
    .balance-accent { border-left: 5px solid #4f46e5; } /* Net Balance - Indigo */
    
    .badge-debit { background-color: rgba(239, 68, 68, 0.1); color: #ef4444; }
    .badge-credit { background-color: rgba(16, 185, 129, 0.1); color: #10b981; }
    .badge-balance { background-color: rgba(79, 70, 229, 0.1); color: #4f46e5; }
    
    /* Onboarding Checklist styling */
    .step-box {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #4f46e5;
        color: #334155;
    }
    
    /* Pulse Dot for status indicators */
    .pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .pulse-green {
        background-color: #10b981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.3);
        animation: pulse 1.8s infinite;
    }
    .pulse-red {
        background-color: #ef4444;
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3);
        animation: pulse 1.8s infinite;
    }
    
    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.3);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    /* Clean Streamlit component overrides */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: -0.01em;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# SCHEMA & MOCK DATA DEFINITIONS
# ==============================================================================
DEFAULT_COLUMNS = ["ID", "Date", "Description", "Category", "Type", "Amount"]

MOCK_TRANSACTIONS = []

CATEGORIES = [
    "Services", 
    "Consulting", 
    "Office Rent", 
    "Software", 
    "Supplies", 
    "Marketing", 
    "Travel", 
    "Utilities", 
    "Tax",
    "Cash Withdrawal",
    "Opening Balance",
    "Miscellaneous"
]

# ==============================================================================
# SECRETS & INTEGRATION STATE DETECTION
# ==============================================================================
def check_secrets_configured():
    """Checks if streamlit secrets are fully configured for GSheetsConnection."""
    try:
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            gsheets = st.secrets["connections"]["gsheets"]
            required_keys = ["spreadsheet", "type", "project_id", "private_key", "client_email"]
            return all(k in gsheets and gsheets[k] not in ("", None) for k in required_keys)
    except Exception:
        pass
    return False

# Initialize session state flags
secrets_configured = check_secrets_configured()

if "mode" not in st.session_state:
    st.session_state.mode = "live" if secrets_configured else "demo"

# Set up mock transactions in session state if they aren't initialized yet
if "demo_df" not in st.session_state:
    st.session_state.demo_df = pd.DataFrame(columns=DEFAULT_COLUMNS)

# Nepal Time (NPT) Daily Reset Check (UTC+5:45)
utc_now = datetime.datetime.now(datetime.timezone.utc)
npt_now = utc_now + datetime.timedelta(hours=5, minutes=45)
current_npt_date = npt_now.date()

if "last_active_day_npt" not in st.session_state:
    st.session_state.last_active_day_npt = current_npt_date

if st.session_state.last_active_day_npt != current_npt_date:
    # Clear Sandbox/Demo memory
    st.session_state.demo_df = pd.DataFrame(columns=DEFAULT_COLUMNS)
    # Clear Streamlit cache to sync fresh data
    st.cache_data.clear()
    # Update active stored day
    st.session_state.last_active_day_npt = current_npt_date
    st.toast("⏰ A new day has started! System reset successfully for Nepal Time (NPT).")

# Cache clear helper to force read fresh gsheets data
def force_refresh():
    st.cache_data.clear()

def clean_pdf_text(text):
    if text is None:
        return ""
    return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_pdf_report_safe(df_day, selected_date, opening_bal, total_cr, total_dr, closing_bal):
    import warnings
    import sys
    import io
    import traceback
    
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = create_pdf_report(df_day, selected_date, opening_bal, total_cr, total_dr, closing_bal)
            return res
    except Exception as e:
        traceback.print_exc(file=old_stderr)
        return b""
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

def create_pdf_report(df_day, selected_date, opening_bal, total_cr, total_dr, closing_bal):
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        from fpdf import FPDF
        
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_margins(15, 20, 15)
        pdf.add_page()
        
        pdf.set_fill_color(79, 70, 229) 
        pdf.rect(0, 0, 210, 45, 'F')
        
        pdf.set_y(10)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 22)
        pdf.cell(0, 10, "DR-CR LEDGER PRO", ln=1, align='C')
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 6, "DAILY ACCOUNT STATEMENT & RECONCILIATION", ln=1, align='C')
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 5, f"Statement Date: {selected_date.strftime('%A, %B %d, %Y')}", ln=1, align='C')
        
        pdf.set_y(52)
        pdf.set_text_color(15, 23, 42) 
        
        pdf.set_font('Helvetica', 'B', 13)
        pdf.cell(0, 8, "1. Executive Summary Table", ln=1)
        pdf.ln(2)
        
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_fill_color(241, 245, 249) 
        pdf.set_text_color(71, 85, 105) 
        
        pdf.cell(45, 8, "Opening Balance", 1, 0, 'C', True)
        pdf.cell(45, 8, "Daily Inflows (CR)", 1, 0, 'C', True)
        pdf.cell(45, 8, "Daily Outflows (DR)", 1, 0, 'C', True)
        pdf.cell(45, 8, "Closing Balance", 1, 1, 'C', True)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(15, 23, 42) 
        pdf.cell(45, 10, f"Rs. {opening_bal:,.2f}", 1, 0, 'C')
        pdf.set_text_color(16, 185, 129) 
        pdf.cell(45, 10, f"Rs. {total_cr:,.2f}", 1, 0, 'C')
        pdf.set_text_color(239, 68, 68) 
        pdf.cell(45, 10, f"Rs. {total_dr:,.2f}", 1, 0, 'C')
        pdf.set_text_color(79, 70, 229) 
        pdf.cell(45, 10, f"Rs. {closing_bal:,.2f}", 1, 1, 'C')
        
        pdf.ln(8)
        pdf.set_text_color(15, 23, 42) 
        
        pdf.set_font('Helvetica', 'B', 13)
        pdf.cell(0, 8, "2. Transaction Detail Ledger", ln=1)
        pdf.ln(2)
        
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(79, 70, 229) 
        pdf.set_text_color(255, 255, 255)
        
        pdf.cell(25, 8, "ID", 1, 0, 'L', True)
        pdf.cell(65, 8, "Description", 1, 0, 'L', True)
        pdf.cell(35, 8, "Category", 1, 0, 'L', True)
        pdf.cell(20, 8, "Type", 1, 0, 'C', True)
        pdf.cell(35, 8, "Amount", 1, 1, 'R', True)
        
        pdf.set_text_color(51, 65, 85) 
        pdf.set_font('Helvetica', '', 8.5)
        
        if df_day.empty:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(180, 10, "No transactions recorded on this date.", 1, 1, 'C')
        else:
            bg_toggle = False
            for _, row in df_day.iterrows():
                if bg_toggle:
                    pdf.set_fill_color(248, 250, 252)
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                type_text = "CR" if row["Type"] == "Credit" else "DR"
                
                pdf.cell(25, 8, clean_pdf_text(row["ID"]), 1, 0, 'L', True)
                pdf.cell(65, 8, clean_pdf_text(row["Description"])[:35], 1, 0, 'L', True)
                pdf.cell(35, 8, clean_pdf_text(row["Category"]), 1, 0, 'L', True)
                
                if row["Type"] == "Credit":
                    pdf.set_text_color(16, 185, 129)
                else:
                    pdf.set_text_color(239, 68, 68)
                pdf.cell(20, 8, type_text, 1, 0, 'C', True)
                
                pdf.set_text_color(51, 65, 85) 
                try:
                    amount_val = float(row["Amount"])
                except (ValueError, TypeError):
                    amount_val = 0.0
                pdf.cell(35, 8, f"Rs. {amount_val:,.2f}", 1, 1, 'R', True)
                bg_toggle = not bg_toggle
                
        pdf.ln(12)
        
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, "3. Statement Declarations & Approvals", ln=1)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.multi_cell(0, 4.5, "This document serves as an official daily closing account record generated by the Dr-Cr Ledger Pro system. All transactions entered have been reconciled against active balances.")
        
        pdf.ln(15)
        
        pdf.set_text_color(15, 23, 42)
        pdf.set_font('Helvetica', 'B', 9.5)
        
        pdf.cell(90, 4, "_____________________________", ln=0, align='L')
        pdf.cell(90, 4, "_____________________________", ln=1, align='R')
        pdf.cell(90, 4, "Prepared By: Accountant", ln=0, align='L')
        pdf.cell(90, 4, "Approved By: Auditor / Supervisor", ln=1, align='R')
        
        pdf_bytes = pdf.output()
        return bytes(pdf_bytes)

# ==============================================================================
# DATA SYNCHRONIZATION (READ) - Main Sheet 1
# ==============================================================================
df = pd.DataFrame(columns=DEFAULT_COLUMNS)
error_message = None

if st.session_state.mode == "live":
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl="5s")
        if df is not None and not df.empty:
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            for col in DEFAULT_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            df = df[DEFAULT_COLUMNS]
        else:
            df = pd.DataFrame(columns=DEFAULT_COLUMNS)
            conn.update(data=df)
            
    except Exception as e:
        error_message = str(e)
        st.session_state.mode = "demo"
        df = st.session_state.demo_df.copy()
else:
    df = st.session_state.demo_df.copy()

# Ensure types are correct
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
df["Type"] = df["Type"].fillna("Debit")
df["Category"] = df["Category"].fillna("Miscellaneous")
df["Description"] = df["Description"].fillna("No details provided")


# ==============================================================================
# SPECIALIZED UDHARO TRACKER STATE INITIALIZATION & CACHING
# ==============================================================================
if "sales_df" not in st.session_state:
    st.session_state.sales_df = pd.DataFrame(columns=["Date", "Customer_Name", "Customer_Phone", "Total_Amount", "Amount_Paid", "Balance_Due", "ID", "Type", "Payment_Method", "Cheque_Details"])
if "purchases_df" not in st.session_state:
    st.session_state.purchases_df = pd.DataFrame(columns=["Date", "Supplier_Name", "Supplier_Phone", "Total_Amount", "Amount_Paid", "Balance_Due", "ID", "Type", "Payment_Method", "Cheque_Details"])

def load_udharo_data(force=False):
    if st.session_state.mode == "live":
        try:
            if force or st.session_state.sales_df.empty or "last_sales_fetch" not in st.session_state:
                st.session_state.sales_df = db_logic.fetch_sales_sheet()
                st.session_state.last_sales_fetch = datetime.datetime.now()
            if force or st.session_state.purchases_df.empty or "last_purchases_fetch" not in st.session_state:
                st.session_state.purchases_df = db_logic.fetch_purchases_sheet()
                st.session_state.last_purchases_fetch = datetime.datetime.now()
        except Exception as e:
            st.error(f"Error loading Udharo data: {e}")
    else:
        # Mock sandbox data if empty
        if st.session_state.sales_df.empty:
            st.session_state.sales_df = pd.DataFrame([
                {"Date": datetime.date.today(), "Customer_Name": "Ramesh Adhikari", "Customer_Phone": "9851098765", "Total_Amount": 25000.0, "Amount_Paid": 10000.0, "Balance_Due": 15000.0, "ID": "tx-s-mock1", "Type": "Udharo", "Payment_Method": "Udharo", "Cheque_Details": ""},
                {"Date": datetime.date.today() - datetime.timedelta(days=2), "Customer_Name": "Sita Thapa", "Customer_Phone": "9841345678", "Total_Amount": 8500.0, "Amount_Paid": 8500.0, "Balance_Due": 0.0, "ID": "tx-s-mock2", "Type": "Cash", "Payment_Method": "Cash", "Cheque_Details": ""},
                {"Date": datetime.date.today() - datetime.timedelta(days=5), "Customer_Name": "Karan Shrestha", "Customer_Phone": "9812345678", "Total_Amount": 12000.0, "Amount_Paid": 4000.0, "Balance_Due": 8000.0, "ID": "tx-s-mock3", "Type": "Udharo", "Payment_Method": "Udharo", "Cheque_Details": ""}
            ])
        if st.session_state.purchases_df.empty:
            st.session_state.purchases_df = pd.DataFrame([
                {"Date": datetime.date.today(), "Supplier_Name": "NAASA Tech Supplies", "Supplier_Phone": "014234567", "Total_Amount": 45000.0, "Amount_Paid": 15000.0, "Balance_Due": 30000.0, "ID": "tx-p-mock1", "Type": "Udharo", "Payment_Method": "Udharo", "Cheque_Details": ""},
                {"Date": datetime.date.today() - datetime.timedelta(days=3), "Supplier_Name": "Pooja Stationery", "Supplier_Phone": "9860123456", "Total_Amount": 5000.0, "Amount_Paid": 5000.0, "Balance_Due": 0.0, "ID": "tx-p-mock2", "Type": "Cash", "Payment_Method": "Cash", "Cheque_Details": ""}
            ])

# Initial load
load_udharo_data()


# ==============================================================================
# GLOBAL SIDEBAR CONFIGURATION
# ==============================================================================
with st.sidebar:
    st.markdown("<h2 style='margin-top:0; color:#4f46e5; font-family:\"Outfit\", sans-serif;'>🧭 Navigation Menu</h2>", unsafe_allow_html=True)
    app_page = st.selectbox(
        "Select Dashboard Page",
        options=["📊 General Cash Ledger", "🤝 Debts & Credits"],
        index=0,
        key="global_page_nav"
    )
    st.markdown("---")

    st.markdown("<h3 style='margin-top:0;'>🛠️ Connection Control</h3>", unsafe_allow_html=True)
    
    if secrets_configured:
        st.markdown("""
            <div style='background:rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius:10px; padding: 12px; margin-bottom: 20px; display: flex; align-items: center;'>
                <span class='pulse-dot pulse-green'></span>
                <span style='color:#34d399; font-weight:600; font-size:0.9rem;'>Connected to Google Sheets</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background:rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius:10px; padding: 12px; margin-bottom: 20px; display: flex; align-items: center;'>
                <span class='pulse-dot pulse-red'></span>
                <span style='color:#f87171; font-weight:600; font-size:0.9rem;'>Offline: Demo Mode Active</span>
            </div>
        """, unsafe_allow_html=True)
        
    mode_options = ["Demo / Sandbox Mode", "Live Google Sheets Connection"]
    selected_mode_idx = 1 if (st.session_state.mode == "live" and secrets_configured) else 0
    
    mode_selection = st.radio(
        "Select Operation Mode",
        options=mode_options,
        index=selected_mode_idx,
        disabled=not secrets_configured,
        help="To enable 'Live Connection', follow the secrets configuration instructions to add your Google Service Account credentials."
    )
    
    if mode_selection == "Live Google Sheets Connection" and secrets_configured:
        st.session_state.mode = "live"
    else:
        st.session_state.mode = "demo"
        
    if st.session_state.mode == "live":
        if st.button("🔄 Sync with Google Sheets", on_click=force_refresh, use_container_width=True):
            load_udharo_data(force=True)
        
    st.markdown("---")
    st.markdown("### 📚 Connection Guide")
    st.info("""
    **Cash Ledger Convention:**
    - **Credit (CR):** Positive cash flow (Inflows / Revenues / Receipts). Increases balance.
    - **Debit (DR):** Negative cash flow (Outflows / Expenses / Payments). Decreases balance.
    """)
    
    with st.expander("🔑 Secure Setup Instructions"):
        st.markdown(f"""
        1. **Enable APIs**: Enable Google Drive and Google Sheets APIs in Google Cloud Console.
        2. **Create Service Account**: Generate a JSON key.
        3. **Share Spreadsheet**: Share your spreadsheet with the service account email.
        4. **Configure Secrets**: Create `.streamlit/secrets.toml` in your project folder using [secrets_template.toml](file:///c:/Users/ruchi/OneDrive/Documents/dr-cr-project/secrets_template.toml) as a guide.
        """)

# ==============================================================================
# RENDER PAGE: 📊 GENERAL CASH LEDGER
# ==============================================================================
if app_page == "📊 General Cash Ledger":
    
    # Header Banner & Top Taskbar
    col_title, col_taskbar = st.columns([3, 1])
    
    with col_title:
        st.markdown("""
            <div class="header-banner" style="margin-bottom: 15px; padding: 25px 35px;">
                <div class="header-title" style="font-size: 2.0rem;">⚖️ Dr-Cr Ledger Pro</div>
                <div class="header-subtitle" style="font-size: 0.95rem;">Secure Accounting Ledger with Real-time Google Sheets CRUD Operations</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_taskbar:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        with st.popover("📅 View Daily Entries", use_container_width=True):
            st.markdown("<h4 style='margin-top:0; color:#4f46e5; font-family:\"Outfit\", sans-serif;'>📅 Daily Entry Finder</h4>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.85rem; color:#64748b; margin-top:-5px;'>Select a date to inspect all recorded debit/credit entries.</p>", unsafe_allow_html=True)
            
            selected_date = st.date_input("Select Date", value=datetime.date.today(), key="view_date_picker")
            daily_entries = df[df["Date"] == selected_date] if not df.empty else pd.DataFrame()
            
            if not daily_entries.empty:
                st.markdown(f"<div style='margin-bottom:10px; font-weight:600; font-size:0.9rem; color:#0f172a;'>🔍 {len(daily_entries)} Entries on {selected_date}:</div>", unsafe_allow_html=True)
                
                day_credits = daily_entries[daily_entries["Type"] == "Credit"]["Amount"].sum()
                day_debits = daily_entries[daily_entries["Type"] == "Debit"]["Amount"].sum()
                day_diff = day_credits - day_debits
                
                st.markdown(f"""
                    <div style='background: #f1f5f9; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; font-size: 0.8rem; border-left: 3px solid #4f46e5;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span>Total Inflow (CR):</span> <strong style='color:#10b981;'>Rs. {day_credits:,.2f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin-top: 2px;'>
                            <span>Total Outflow (DR):</span> <strong style='color:#ef4444;'>Rs. {day_debits:,.2f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; margin-top: 4px; border-top: 1px dashed #cbd5e1; padding-top: 4px; font-weight:600;'>
                            <span>Net Daily Change:</span> <span style='color:{"#10b981" if day_diff >= 0 else "#ef4444"};'>Rs. {day_diff:,.2f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                for _, row in daily_entries.iterrows():
                    badge_style = "background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2);" if row["Type"] == "Credit" else "background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2);"
                    type_label = "CR" if row["Type"] == "Credit" else "DR"
                    st.markdown(f"""
                        <div style='background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <strong style='font-size: 0.85rem; color: #1e293b;'>{row['Description']}</strong>
                                <span style='padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; {badge_style}'>{type_label} Rs. {row['Amount']:,.2f}</span>
                            </div>
                            <div style='font-size: 0.75rem; color: #64748b; margin-top: 4px; display: flex; justify-content: space-between;'>
                                <span>Category: <b>{row['Category']}</b></span>
                                <span style='font-family: monospace;'>ID: {row['ID']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='text-align: center; padding: 20px 10px; color: #64748b;'>
                        <span style='font-size: 2rem; display: block; margin-bottom: 10px;'>📅</span>
                        <span style='font-size: 0.85rem;'>No ledger entries recorded on <b>{selected_date}</b>.</span>
                    </div>
                """, unsafe_allow_html=True)
    
    if error_message:
        st.error(f"❌ Google Sheets Connection Error: {error_message}")
        st.info("⚠️ Falling back to sandbox Demo Mode. Please check your `.streamlit/secrets.toml` parameters or spreadsheet permissions.")

    # Ledger Settings sidebar sub-element
    detected_opening = 0.0
    opening_row = df[(df["Category"] == "Opening Balance") | (df["Description"] == "Opening Balance")] if not df.empty else pd.DataFrame()
    if not opening_row.empty:
        detected_opening = float(opening_row.iloc[0]["Amount"])
    
    with st.sidebar:
        st.markdown("### 💰 Ledger Settings")
        opening_balance = st.number_input(
            "Opening Balance (Rs.)",
            min_value=0.00,
            max_value=10000000.00,
            value=detected_opening,
            step=500.00,
            help="Specify the starting balance of this ledger."
        )
        
        if opening_balance != detected_opening:
            if st.button("💾 Save Balance to Google Sheet", use_container_width=True, type="primary"):
                updated_df = df.copy()
                opening_idx = updated_df[(updated_df["Category"] == "Opening Balance") | (updated_df["Description"] == "Opening Balance")].index
                
                if not opening_idx.empty:
                    if opening_balance == 0.0:
                        updated_df = updated_df.drop(opening_idx)
                    else:
                        updated_df.at[opening_idx[0], "Amount"] = round(opening_balance, 2)
                        updated_df.at[opening_idx[0], "Type"] = "Credit"
                        updated_df.at[opening_idx[0], "Date"] = (df["Date"].min() if not df.empty and pd.notnull(df["Date"].min()) else datetime.date.today()).strftime("%Y-%m-%d")
                elif opening_balance > 0.0:
                    new_id = f"tx-opening"
                    earliest_date = df["Date"].min() if not df.empty and pd.notnull(df["Date"].min()) else datetime.date.today()
                    new_row = pd.DataFrame([{
                        "ID": new_id,
                        "Date": earliest_date.strftime("%Y-%m-%d") if isinstance(earliest_date, (datetime.date, datetime.datetime)) else str(earliest_date),
                        "Description": "Opening Balance",
                        "Category": "Opening Balance",
                        "Type": "Credit",
                        "Amount": round(opening_balance, 2)
                    }])
                    updated_df = pd.concat([new_row, updated_df], ignore_index=True)
                
                if st.session_state.mode == "live":
                    try:
                        conn.update(data=updated_df)
                        st.success("🎉 Opening Balance successfully written to Google Sheets!")
                        force_refresh()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update Google Sheet: {e}")
                else:
                    st.session_state.demo_df = updated_df
                    st.success("🎉 Opening Balance successfully updated in Demo Sandbox!")
                    st.rerun()
                    
        st.markdown("---")

    # Financial Computations
    total_debits = df[(df["Type"] == "Debit") & (df["Category"] != "Opening Balance")]["Amount"].sum()   
    total_credits = df[(df["Type"] == "Credit") & (df["Category"] != "Opening Balance")]["Amount"].sum() 
    net_balance = opening_balance + total_credits - total_debits 

    st.markdown(f"""
        <div class="metric-card-container">
            <div class="metric-card credit-accent">
                <div class="metric-title">📥 Total Credits (CR - Cash Inflow)</div>
                <div class="metric-value" style="color: #10b981;">Rs. {total_credits:,.2f}</div>
                <span class="metric-badge badge-credit">+{len(df[df["Type"] == "Credit"])} Entries</span>
            </div>
            <div class="metric-card debit-accent">
                <div class="metric-title">📤 Total Debits (DR - Cash Outflow)</div>
                <div class="metric-value" style="color: #ef4444;">Rs. {total_debits:,.2f}</div>
                <span class="metric-badge badge-debit">-{len(df[df["Type"] == "Debit"])} Entries</span>
            </div>
            <div class="metric-card balance-accent">
                <div class="metric-title">⚖️ Net Ledger Balance</div>
                <div class="metric-value" style="color: {'#4f46e5' if net_balance >= 0 else '#ef4444'};">Rs. {net_balance:,.2f}</div>
                <span class="metric-badge badge-balance">{'Positive Balance' if net_balance >= 0 else 'Deficit'}</span>
                {f'<span style="font-size:0.75rem; color:#64748b; display:block; margin-top:5px;">(Incl. Rs. {opening_balance:,.2f} Opening Balance)</span>' if opening_balance > 0 else ''}
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Liquidity Vault Calculations
    sales_df_l = st.session_state.sales_df.copy()
    purchases_df_l = st.session_state.purchases_df.copy()
    
    # Graceful parsing and cleaning
    for df_temp in [sales_df_l, purchases_df_l]:
        if not df_temp.empty:
            if "Payment_Method" not in df_temp.columns:
                df_temp["Payment_Method"] = df_temp.apply(lambda row: "Udharo" if row["Type"] == "Udharo" else "Cash", axis=1)
            else:
                df_temp["Payment_Method"] = df_temp["Payment_Method"].fillna(df_temp.apply(lambda row: "Udharo" if row["Type"] == "Udharo" else "Cash", axis=1))
            df_temp["Amount_Paid"] = pd.to_numeric(df_temp["Amount_Paid"], errors="coerce").fillna(0.0)
            df_temp["Payment_Method"] = df_temp["Payment_Method"].astype(str).str.strip()

    def get_l_sum(df_temp, methods):
        if df_temp.empty:
            return 0.0
        mask = df_temp["Payment_Method"].str.lower().isin([m.lower() for m in methods])
        return df_temp.loc[mask, "Amount_Paid"].sum()

    # Cash Till: Cash
    cash_till = get_l_sum(sales_df_l, ["Cash"]) - get_l_sum(purchases_df_l, ["Cash"])
    
    # Bank Balance: Bank Transfer or Cheque
    bank_balance = get_l_sum(sales_df_l, ["Bank Transfer", "Cheque"]) - get_l_sum(purchases_df_l, ["Bank Transfer", "Cheque"])
    
    # Fonepay QR Wallet: Fonepay
    fonepay_wallet = get_l_sum(sales_df_l, ["Fonepay"]) - get_l_sum(purchases_df_l, ["Fonepay"])
    
    # eSewa Wallet: eSewa
    esewa_wallet = get_l_sum(sales_df_l, ["eSewa"]) - get_l_sum(purchases_df_l, ["eSewa"])
    
    # Khalti Wallet: Khalti
    khalti_wallet = get_l_sum(sales_df_l, ["Khalti"]) - get_l_sum(purchases_df_l, ["Khalti"])

    with st.expander("💳 Account Balances", expanded=True):
        st.markdown("<p style='font-size:0.95rem; color:#475569; margin-top:-5px; font-weight:500;'>Real-time liquid assets reconciled across active payment systems.</p>", unsafe_allow_html=True)
        col_l1, col_l2, col_l3, col_l4, col_l5 = st.columns(5)
        
        with col_l1:
            st.markdown(f"""
                <div class="metric-card balance-accent" style="padding:15px; border-left: 5px solid #d97706; background:#fffbeb; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.05);">
                    <div style="font-size:0.75rem; font-weight:700; color:#b45309; text-transform:uppercase; letter-spacing:0.05em;">💵 Cash Till</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#78350f; margin-top:5px; font-family:'Outfit', sans-serif;">Rs. {cash_till:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_l2:
            st.markdown(f"""
                <div class="metric-card balance-accent" style="padding:15px; border-left: 5px solid #2563eb; background:#eff6ff; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.05);">
                    <div style="font-size:0.75rem; font-weight:700; color:#1d4ed8; text-transform:uppercase; letter-spacing:0.05em;">🏦 Bank Balance</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#1e40af; margin-top:5px; font-family:'Outfit', sans-serif;">Rs. {bank_balance:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_l3:
            st.markdown(f"""
                <div class="metric-card balance-accent" style="padding:15px; border-left: 5px solid #059669; background:#ecfdf5; box-shadow: 0 4px 15px rgba(5, 150, 105, 0.05);">
                    <div style="font-size:0.75rem; font-weight:700; color:#047857; text-transform:uppercase; letter-spacing:0.05em;">📱 Fonepay QR</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#065f46; margin-top:5px; font-family:'Outfit', sans-serif;">Rs. {fonepay_wallet:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_l4:
            st.markdown(f"""
                <div class="metric-card balance-accent" style="padding:15px; border-left: 5px solid #4f46e5; background:#eef2ff; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.05);">
                    <div style="font-size:0.75rem; font-weight:700; color:#4338ca; text-transform:uppercase; letter-spacing:0.05em;">🟢 eSewa Wallet</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#3730a3; margin-top:5px; font-family:'Outfit', sans-serif;">Rs. {esewa_wallet:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col_l5:
            st.markdown(f"""
                <div class="metric-card balance-accent" style="padding:15px; border-left: 5px solid #db2777; background:#fdf2f8; box-shadow: 0 4px 15px rgba(219, 39, 119, 0.05);">
                    <div style="font-size:0.75rem; font-weight:700; color:#be185d; text-transform:uppercase; letter-spacing:0.05em;">🟣 Khalti Wallet</div>
                    <div style="font-size:1.35rem; font-weight:800; color:#9d174d; margin-top:5px; font-family:'Outfit', sans-serif;">Rs. {khalti_wallet:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)

    # Main Tabs
    tab_dashboard, tab_create, tab_update, tab_delete = st.tabs([
        "📊 Ledger Insights & Analytics",
        "➕ Create Ledger Entry (Insert)",
        "✏️ Update Ledger Entry (Edit)",
        "❌ Delete Ledger Entry (Remove)"
    ])

    with tab_dashboard:
        col_filters, col_charts = st.columns([1, 2])
        
        with col_filters:
            st.markdown("### 🔍 Search & Filters")
            search_query = st.text_input("Search description or ID", placeholder="Search transactions...")
            filter_category = st.multiselect("Filter by Category", options=CATEGORIES, default=[])
            filter_type = st.multiselect("Filter by Type", options=["Debit", "Credit"], default=[])
            
            filtered_df = df.copy()
            if search_query:
                filtered_df = filtered_df[
                    filtered_df["Description"].str.contains(search_query, case=False, na=False) |
                    filtered_df["ID"].str.contains(search_query, case=False, na=False)
                ]
            if filter_category:
                filtered_df = filtered_df[filtered_df["Category"].isin(filter_category)]
            if filter_type:
                filtered_df = filtered_df[filtered_df["Type"].isin(filter_type)]
                
            st.markdown(f"**Showing {len(filtered_df)} of {len(df)} transactions**")
            
            st.data_editor(
                filtered_df,
                column_config={
                    "ID": st.column_config.TextColumn("Transaction ID", width="small", disabled=True),
                    "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "Description": st.column_config.TextColumn("Description", width="medium"),
                    "Category": st.column_config.SelectboxColumn("Category", options=CATEGORIES, width="small"),
                    "Type": st.column_config.SelectboxColumn("Type", options=["Debit", "Credit"], width="small"),
                    "Amount": st.column_config.NumberColumn("Amount (Rs.)", format="Rs. %.2f", width="small")
                },
                hide_index=True,
                use_container_width=True,
                disabled=True,
                key="ledger_table"
            )
            
        with col_charts:
            st.markdown("### 📈 Visual Accounting Insights")
            
            if not filtered_df.empty:
                chart_df = filtered_df.copy()
                chart_df['Date_Parsed'] = pd.to_datetime(chart_df['Date'])
                chart_df = chart_df.sort_values(by='Date_Parsed')
                
                chart_df['Net_Value'] = chart_df.apply(
                    lambda row: row['Amount'] if row['Type'] == 'Credit' else -row['Amount'], axis=1
                )
                chart_df['Cumulative_Balance'] = opening_balance + chart_df['Net_Value'].cumsum()
                
                line_chart = alt.Chart(chart_df).mark_line(
                    point=alt.OverlayMarkDef(color='#4f46e5', size=60), 
                    strokeWidth=3, 
                    color='#6366f1'
                ).encode(
                    x=alt.X('Date_Parsed:T', title='Transaction Date'),
                    y=alt.Y('Cumulative_Balance:Q', title='Running Balance (Rs.)'),
                    tooltip=['Date:N', 'Description:N', 'Type:N', 'Amount:Q', 'Cumulative_Balance:Q']
                ).properties(
                    height=250,
                    title="Running Ledger Balance Trend"
                ).interactive()
                
                st.altair_chart(line_chart, use_container_width=True)
                
                col_chart_left, col_chart_right = st.columns(2)
                
                with col_chart_left:
                    cat_df = filtered_df.groupby(["Category", "Type"])["Amount"].sum().reset_index()
                    cat_chart = alt.Chart(cat_df).mark_bar().encode(
                        x=alt.X('Amount:Q', title='Total (Rs.)'),
                        y=alt.Y('Category:N', sort='-x', title='Category'),
                        color=alt.Color('Type:N', scale=alt.Scale(domain=['Credit', 'Debit'], range=['#10b981', '#ef4444']), title='Type'),
                        tooltip=['Category:N', 'Type:N', 'Amount:Q']
                    ).properties(
                        height=200,
                        title="Volume by Category"
                    )
                    st.altair_chart(cat_chart, use_container_width=True)
                    
                with col_chart_right:
                    type_df = filtered_df.groupby("Type")["Amount"].sum().reset_index()
                    donut_chart = alt.Chart(type_df).mark_arc(innerRadius=40).encode(
                        theta=alt.Theta(field="Amount", type="quantitative"),
                        color=alt.Color(field="Type", type="nominal", scale=alt.Scale(domain=['Credit', 'Debit'], range=['#10b981', '#ef4444'])),
                        tooltip=['Type:N', 'Amount:Q']
                    ).properties(
                        height=200,
                        title="Credit (CR) vs Debit (DR) Ratio"
                    )
                    st.altair_chart(donut_chart, use_container_width=True)
            else:
                st.info("💡 Add ledger entries or adjust your filters to view analytical insights.")

    with tab_create:
        st.markdown("### ➕ Record a New Transaction")
        
        with st.form("insert_transaction_form", clear_on_submit=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                tx_date = st.date_input("Transaction Date", value=datetime.date.today())
                tx_type = st.selectbox("Entry Type (DR/CR)", options=["Debit", "Credit"])
            with col_c2:
                tx_category = st.selectbox("Category", options=CATEGORIES)
                tx_amount = st.number_input("Amount (Rs.)", min_value=0.01, max_value=1000000.0, value=100.0, step=10.0, format="%.2f")
            with col_c3:
                tx_desc = st.text_input("Description / Notes", placeholder="E.g., Adobe Creative Cloud Subscription")
                
            submit_btn = st.form_submit_button("💾 Save Ledger Entry")
            
            if submit_btn:
                if not tx_desc.strip():
                    st.error("❌ Description is required!")
                else:
                    new_id = f"tx-{uuid.uuid4().hex[:6]}"
                    final_type = tx_type
                    if tx_category == "Cash Withdrawal":
                        final_type = "Debit"
                        st.toast("ℹ️ Automatically listed as Debit (DR) for Cash Withdrawal.")
                    
                    new_entry = {
                        "ID": new_id,
                        "Date": tx_date.strftime("%Y-%m-%d"),
                        "Description": tx_desc.strip(),
                        "Category": tx_category,
                        "Type": final_type,
                        "Amount": round(tx_amount, 2)
                    }
                    
                    updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    
                    if st.session_state.mode == "live":
                        try:
                            conn.update(data=updated_df)
                            st.success(f"🎉 Successfully inserted transaction '{tx_desc}' to Google Sheet!")
                            st.balloons()
                            force_refresh()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to save to Google Sheets: {e}")
                    else:
                        st.session_state.demo_df = updated_df
                        st.success(f"🎉 Successfully registered transaction '{tx_desc}' in Demo Sandbox!")
                        st.rerun()

    with tab_update:
        st.markdown("### ✏️ Edit an Existing Transaction")
        if df.empty:
            st.info("💡 The ledger is empty. Create some entries first.")
        else:
            select_options = [f"{row['ID']} - {row['Description']} (Rs. {row['Amount']:.2f})" for _, row in df.iterrows()]
            selected_option = st.selectbox("Select Transaction to Edit", options=select_options)
            
            selected_id = selected_option.split(" - ")[0]
            selected_row = df[df["ID"] == selected_id].iloc[0]
            
            with st.form("update_transaction_form"):
                st.markdown(f"**Editing Transaction: `{selected_id}`**")
                col_u1, col_u2, col_u3 = st.columns(3)
                
                with col_u1:
                    val = selected_row["Date"]
                    if isinstance(val, (datetime.date, datetime.datetime)):
                        orig_date = val
                    else:
                        try:
                            orig_date = datetime.datetime.strptime(str(val), "%Y-%m-%d").date()
                        except Exception:
                            orig_date = datetime.date.today()
                    u_date = st.date_input("Date", value=orig_date)
                    u_type = st.selectbox("Type", options=["Debit", "Credit"], index=0 if selected_row["Type"] == "Debit" else 1)
                    
                with col_u2:
                    cat_idx = CATEGORIES.index(selected_row["Category"]) if selected_row["Category"] in CATEGORIES else 0
                    u_category = st.selectbox("Category", options=CATEGORIES, index=cat_idx)
                    u_amount = st.number_input("Amount (Rs.)", min_value=0.01, value=float(selected_row["Amount"]), step=10.0, format="%.2f")
                    
                with col_u3:
                    u_desc = st.text_input("Description", value=selected_row["Description"])
                    
                update_btn = st.form_submit_button("📝 Apply Changes")
                
                if update_btn:
                    if not u_desc.strip():
                        st.error("❌ Description cannot be blank!")
                    else:
                        updated_df = df.copy()
                        row_idx = updated_df[updated_df["ID"] == selected_id].index[0]
                        final_u_type = u_type
                        if u_category == "Cash Withdrawal":
                            final_u_type = "Debit"
                            st.toast("ℹ️ Automatically forced to Debit (DR) for Cash Withdrawal.")
                        
                        updated_df.at[row_idx, "Date"] = u_date.strftime("%Y-%m-%d")
                        updated_df.at[row_idx, "Type"] = final_u_type
                        updated_df.at[row_idx, "Category"] = u_category
                        updated_df.at[row_idx, "Amount"] = round(u_amount, 2)
                        updated_df.at[row_idx, "Description"] = u_desc.strip()
                        
                        if st.session_state.mode == "live":
                            try:
                                conn.update(data=updated_df)
                                st.success(f"🎉 Updated transaction `{selected_id}` in Google Sheets!")
                                force_refresh()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to save update: {e}")
                        else:
                            st.session_state.demo_df = updated_df
                            st.success(f"🎉 Updated transaction `{selected_id}` in Sandbox memory!")
                            st.rerun()

    with tab_delete:
        st.markdown("### ❌ Delete a Ledger Entry")
        if df.empty:
            st.info("💡 The ledger is empty.")
        else:
            delete_options = [f"{row['ID']} - {row['Description']} (Rs. {row['Amount']:.2f})" for _, row in df.iterrows()]
            delete_selection = st.selectbox("Select Transaction to Delete", options=delete_options, key="del_select")
            
            delete_id = delete_selection.split(" - ")[0]
            delete_row = df[df["ID"] == delete_id].iloc[0]
            
            st.warning(f"""
            **⚠️ Are you sure you want to permanently delete this transaction?**
            - **ID:** `{delete_row['ID']}`
            - **Description:** `{delete_row['Description']}`
            - **Amount:** `Rs. {delete_row['Amount']:.2f}`
            """)
            
            confirm_delete = st.button("🔴 Yes, Delete", use_container_width=True)
            if confirm_delete:
                updated_df = df[df["ID"] != delete_id].copy()
                if st.session_state.mode == "live":
                    try:
                        conn.update(data=updated_df)
                        st.success(f"🗑️ Successfully deleted transaction `{delete_id}` from Google Sheets!")
                        force_refresh()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to delete record: {e}")
                else:
                    st.session_state.demo_df = updated_df
                    st.success(f"🗑️ Successfully deleted transaction `{delete_id}` from Sandbox!")
                    st.rerun()

    # End Day Closing & PDF Generator
    st.markdown("---")
    st.markdown("### 🏁 End Day Account Statement Generator")
    
    with st.container():
        st.markdown("""
            <div style='background: #ffffff; border: 1px solid #cbd5e1; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); margin-top: 15px;'>
                <h4 style='margin-top: 0; color: #0f172a; font-family: "Outfit", sans-serif; font-size: 1.25rem;'>🏁 End Day Closing & PDF Statement</h4>
                <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 20px;'>
                    Finalize records for a chosen business day. This tool will calculate the opening balance, daily credits/debits, closing balance, and generate a downloadable professional PDF statement.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_e1, col_e2 = st.columns([1, 2])
        with col_e1:
            end_day_date = st.date_input("Select Statement Date", value=datetime.date.today(), key="end_day_date_picker")
            
            prior_tx = df[df["Date"] < end_day_date] if not df.empty else pd.DataFrame()
            prior_credits = prior_tx[(prior_tx["Type"] == "Credit") & (prior_tx["Category"] != "Opening Balance")]["Amount"].sum() if not prior_tx.empty else 0.0
            prior_debits = prior_tx[(prior_tx["Type"] == "Debit") & (prior_tx["Category"] != "Opening Balance")]["Amount"].sum() if not prior_tx.empty else 0.0
            
            day_opening_balance = opening_balance + prior_credits - prior_debits
            
            day_tx = df[df["Date"] == end_day_date] if not df.empty else pd.DataFrame()
            day_credits = day_tx[day_tx["Type"] == "Credit"]["Amount"].sum() if not day_tx.empty else 0.0
            day_debits = day_tx[day_tx["Type"] == "Debit"]["Amount"].sum() if not day_tx.empty else 0.0
            day_closing_balance = day_opening_balance + day_credits - day_debits
            
            pdf_bytes = create_pdf_report_safe(day_tx, end_day_date, day_opening_balance, day_credits, day_debits, day_closing_balance)
            
            st.download_button(
                label="📄 Download A4 PDF Statement",
                data=pdf_bytes,
                file_name=f"DR_CR_Ledger_Statement_{end_day_date.strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_e2:
            st.markdown(f"""
                <div style='background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;'>
                    <div style='font-weight: 700; font-size: 0.95rem; color: #1e293b; margin-bottom: 12px; display: flex; justify-content: space-between;'>
                        <span>📊 Statement Preview Summary</span>
                        <span style='color: #4f46e5;'>{end_day_date.strftime('%Y-%m-%d')}</span>
                    </div>
                    <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;'>
                        <div style='background: #ffffff; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px;'>
                            <span style='font-size: 0.75rem; color: #64748b; font-weight:600; text-transform:uppercase;'>Opening Balance</span>
                            <div style='font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-top: 4px;'>Rs. {day_opening_balance:,.2f}</div>
                        </div>
                        <div style='background: #ffffff; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px; border-left: 3px solid #10b981;'>
                            <span style='font-size: 0.75rem; color: #10b981; font-weight:600; text-transform:uppercase;'>Daily Inflow (CR)</span>
                            <div style='font-size: 1.1rem; font-weight: 700; color: #10b981; margin-top: 4px;'>Rs. {day_credits:,.2f}</div>
                        </div>
                        <div style='background: #ffffff; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px; border-left: 3px solid #ef4444;'>
                            <span style='font-size: 0.75rem; color: #ef4444; font-weight:600; text-transform:uppercase;'>Daily Outflow (DR)</span>
                            <div style='font-size: 1.1rem; font-weight: 700; color: #ef4444; margin-top: 4px;'>Rs. {day_debits:,.2f}</div>
                        </div>
                        <div style='background: #ffffff; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px; border-left: 3px solid #4f46e5;'>
                            <span style='font-size: 0.75rem; color: #4f46e5; font-weight:600; text-transform:uppercase;'>Closing Balance</span>
                            <div style='font-size: 1.1rem; font-weight: 700; color: #4f46e5; margin-top: 4px;'>Rs. {day_closing_balance:,.2f}</div>
                        </div>
                    </div>
                    <div style='font-size: 0.8rem; color: #64748b; margin-top: 12px; border-top: 1px dashed #cbd5e1; padding-top: 12px; display: flex; justify-content: space-between;'>
                        <span>Total Daily Entries: <b>{len(day_tx)}</b></span>
                        <span>Reconciliation: <b>Verified ✓</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    if not secrets_configured:
        st.markdown("---")
        st.markdown("## 🔑 Credentials TOML Builder")
        with st.expander("🛠️ Interactive Secrets Generator"):
            sheet_url = st.text_input("Spreadsheet URL", value="https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit")
            p_id = st.text_input("Project ID (project_id)", value="my-gcp-project-12345")
            pk_id = st.text_input("Private Key ID (private_key_id)", value="a1b2c3d4e5f6g7h8")
            pk = st.text_area("Private Key (private_key)")
            email = st.text_input("Client Email (client_email)")
            c_id = st.text_input("Client ID (client_id)")
            
            formatted_pk = pk.replace('\n', '\\n') if pk else '-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n'
            escaped_email = email.replace('@', '%40') if email else ''
            
            generated_toml = f"""[connections.gsheets]
spreadsheet = "{sheet_url}"
type = "service_account"
project_id = "{p_id}"
private_key_id = "{pk_id}"
private_key = "{formatted_pk}"
client_email = "{email}"
client_id = "{c_id}"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/{escaped_email}"
"""
            st.code(generated_toml, language="toml")


# ==============================================================================
# RENDER PAGE: 🤝 DEBTS & CREDITS (UDHARO TRACKER)
# ==============================================================================
else:
    # Reload fresh data
    load_udharo_data()
    
    sales_df = st.session_state.sales_df
    purchases_df = st.session_state.purchases_df
    
    # Header Banner - Specialized for Udharo Tracker
    st.markdown("""
        <div class="header-banner" style="margin-bottom: 20px; padding: 25px 35px; background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);">
            <div class="header-title" style="font-size: 2.0rem;">🤝 Debts & Credits (Udharo Tracker)</div>
            <div class="header-subtitle" style="font-size: 0.95rem;">Track Customer Receivables & Supplier Payables with Simple Local-Friendly Debt Settlement</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. High-Contrast Metric Cards (Side-by-side)
    # Sum of customer Balance_Due (Receivables - where type is 'Udharo')
    active_sales_udharo = sales_df[sales_df["Type"] == "Udharo"] if not sales_df.empty else pd.DataFrame()
    to_receive = active_sales_udharo["Balance_Due"].sum() if not active_sales_udharo.empty else 0.0
    
    # Sum of supplier Balance_Due (Payables - where type is 'Udharo')
    active_purchases_udharo = purchases_df[purchases_df["Type"] == "Udharo"] if not purchases_df.empty else pd.DataFrame()
    to_pay = active_purchases_udharo["Balance_Due"].sum() if not active_purchases_udharo.empty else 0.0
    
    st.markdown(f"""
        <div class="metric-card-container">
            <div class="metric-card credit-accent" style="border-left-color: #10b981;">
                <div class="metric-title" style="color: #0f766e;">📥 Total to Receive (Customer Debts)</div>
                <div class="metric-value" style="color: #10b981;">Rs. {to_receive:,.2f}</div>
                <span class="metric-badge" style="background-color: rgba(16, 185, 129, 0.1); color: #10b981;">Payment Receivables</span>
            </div>
            <div class="metric-card debit-accent" style="border-left-color: #ef4444;">
                <div class="metric-title" style="color: #9f1239;">📤 Total to Pay (Supplier Obligations)</div>
                <div class="metric-value" style="color: #ef4444;">Rs. {to_pay:,.2f}</div>
                <span class="metric-badge" style="background-color: rgba(239, 68, 68, 0.1); color: #ef4444;">Supplier Payables</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Interactive Ledger Tabs
    tab_cust, tab_supp = st.tabs(["👥 Customer Receivables", "🏢 Supplier Payables"])
    
    # --- CUSTOMER RECEIVABLES TAB ---
    with tab_cust:
        st.markdown("### 👥 Customer Receivables (Outstanding Debts)")
        
        col_c_left, col_c_right = st.columns([2, 1])
        
        with col_c_left:
            # Search bar
            search_cust = st.text_input("🔍 Search Customer by Name or Phone", placeholder="Type name or phone number...", key="search_cust_input")
            
            # Filter active receivables (Balance_Due > 0)
            cust_table_df = sales_df[sales_df["Balance_Due"] > 0].copy() if not sales_df.empty else pd.DataFrame()
            if not cust_table_df.empty:
                cust_table_df["Customer_Phone"] = cust_table_df["Customer_Phone"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
            
            if search_cust and not cust_table_df.empty:
                cust_table_df = cust_table_df[
                    cust_table_df["Customer_Name"].str.contains(search_cust, case=False, na=False) |
                    cust_table_df["Customer_Phone"].str.contains(search_cust, case=False, na=False)
                ]
                
            st.markdown(f"**Found {len(cust_table_df)} outstanding customer debt records**")
            
            if not cust_table_df.empty:
                st.data_editor(
                    cust_table_df,
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                        "Customer_Name": st.column_config.TextColumn("Customer Name", width="medium"),
                        "Customer_Phone": st.column_config.TextColumn("Phone Number"),
                        "Total_Amount": st.column_config.NumberColumn("Total Amount (Rs.)", format="Rs. %.2f"),
                        "Amount_Paid": st.column_config.NumberColumn("Amount Paid (Rs.)", format="Rs. %.2f"),
                        "Balance_Due": st.column_config.NumberColumn("Balance Due (Rs.)", format="Rs. %.2f"),
                        "Type": st.column_config.TextColumn("Status"),
                        "ID": st.column_config.TextColumn("ID", disabled=True)
                    },
                    hide_index=True,
                    use_container_width=True,
                    disabled=True,
                    key="cust_outstanding_table"
                )
            else:
                st.info("🎉 All clear! No outstanding customer receivables found.")
                
            # Expandable form to add new Sales entry (with Dynamic UI Logic)
            with st.expander("➕ Record New Customer Sale"):
                col_fs1, col_fs2 = st.columns(2)
                with col_fs1:
                    c_date = st.date_input("Sale Date", value=datetime.date.today(), key="sale_date_input")
                    c_method = st.selectbox(
                        "Payment Method *",
                        options=['Cash', 'Cheque', 'Fonepay', 'eSewa', 'Khalti', 'Bank Transfer', 'Udharo'],
                        index=6,  # Default to Udharo for outstanding receivables context
                        key="sale_payment_method"
                    )
                    
                    # Optional Cheque Number & Bank Name
                    c_cheque_details = ""
                    if c_method == "Cheque":
                        c_cheque_details = st.text_input("Cheque Number & Bank Name (Optional)", placeholder="E.g., Cheque #45612 - Nabil Bank", key="sale_cheque_details")
                    
                    # Required Customer Name and Phone Number only for Udharo
                    if c_method == "Udharo":
                        c_name = st.text_input("Customer Name *", key="sale_cust_name")
                        c_phone = st.text_input("Customer Phone Number *", key="sale_cust_phone")
                    else:
                        c_name = st.text_input("Customer Name (Optional)", value="Walk-in Customer", key="sale_cust_name")
                        c_phone = st.text_input("Customer Phone (Optional)", value="N/A", key="sale_cust_phone")

                with col_fs2:
                    c_total = st.number_input("Total Amount (Rs.) *", min_value=0.01, step=100.0, value=1000.0, key="sale_total_amount")
                    if c_method == "Udharo":
                        c_paid = st.number_input("Amount Paid (Rs.)", min_value=0.00, step=100.0, value=0.0, key="sale_amount_paid")
                    else:
                        c_paid = c_total # Automatically fully paid for non-credit sales
                        st.info(f"ℹ️ Amount Paid automatically set to Total Amount (Rs. {c_total:,.2f}) for non-Udharo sales.")

                submit_sale = st.button("💾 Save Customer Sale", type="primary", use_container_width=True, key="save_sale_btn")
                
                if submit_sale:
                    if c_method == "Udharo" and (not c_name.strip() or not c_phone.strip()):
                        st.error("❌ Customer Name and Phone Number are required for credit sales (Udharo)!")
                    elif not c_name.strip():
                        st.error("❌ Customer Name cannot be empty!")
                    elif c_paid > c_total:
                        st.error("❌ Amount Paid cannot be greater than Total Amount!")
                    else:
                        try:
                            if st.session_state.mode == "live":
                                db_logic.append_sales_record(
                                    customer_name=c_name,
                                    customer_phone=c_phone,
                                    total_amount=c_total,
                                    amount_paid=c_paid,
                                    is_credit=(c_method == "Udharo"),
                                    date=c_date,
                                    payment_method=c_method,
                                    cheque_details=c_cheque_details
                                )
                                st.success(f"🎉 Successfully recorded sale to Google Sheets!")
                            else:
                                # Sandbox mock append
                                tx_id = f"tx-s-mock-{uuid.uuid4().hex[:4]}"
                                total_val = round(float(c_total), 2)
                                paid_val = round(float(c_paid), 2)
                                due_val = round(total_val - paid_val, 2)
                                tx_type = "Udharo" if (c_method == "Udharo") else "Cash"
                                new_entry = {
                                    "Date": c_date,
                                    "Customer_Name": c_name.strip(),
                                    "Customer_Phone": c_phone.strip(),
                                    "Total_Amount": total_val,
                                    "Amount_Paid": paid_val,
                                    "Balance_Due": due_val,
                                    "ID": tx_id,
                                    "Type": tx_type,
                                    "Payment_Method": c_method,
                                    "Cheque_Details": c_cheque_details
                                }
                                st.session_state.sales_df = pd.concat([st.session_state.sales_df, pd.DataFrame([new_entry])], ignore_index=True)
                                st.success(f"🎉 Successfully recorded sale to Sandbox memory!")
                            load_udharo_data(force=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to record sale: {e}")
                                
        with col_c_right:
            st.markdown("### 💳 Debt Settlements")
            st.markdown("Settle customer debts here.")
            
            outstanding_custs = sales_df[sales_df["Balance_Due"] > 0].copy() if not sales_df.empty else pd.DataFrame()
            
            if outstanding_custs.empty:
                st.info("No customer debt to settle.")
            else:
                cust_options = [f"{row['ID']} - {row['Customer_Name']} (Owes Rs. {row['Balance_Due']:.2f})" for _, row in outstanding_custs.iterrows()]
                selected_cust_opt = st.selectbox("Select Customer to Settle", options=cust_options)
                
                selected_cust_id = selected_cust_opt.split(" - ")[0]
                selected_cust_row = outstanding_custs[outstanding_custs["ID"] == selected_cust_id].iloc[0]
                
                # Settle payment method dropdown
                selected_settle_method = st.selectbox(
                    "Settlement Method *",
                    options=['Cash', 'Cheque', 'Fonepay', 'eSewa', 'Khalti', 'Bank Transfer'],
                    index=0,
                    key="cust_settle_method"
                )
                
                selected_settle_cheque = ""
                if selected_settle_method == "Cheque":
                    selected_settle_cheque = st.text_input("Cheque Details (Optional)", placeholder="E.g., Cheque #98765 - Bank of Kathmandu", key="cust_settle_cheque_details")
                
                c_settle_amount = st.number_input(
                    "Amount Settled (Rs.)", 
                    min_value=0.01, 
                    max_value=float(selected_cust_row["Balance_Due"]), 
                    value=float(selected_cust_row["Balance_Due"]), 
                    step=10.0,
                    key="cust_settle_input"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💸 Partially Settle", use_container_width=True):
                        try:
                            if st.session_state.mode == "live":
                                db_logic.settle_customer_debt(selected_cust_id, c_settle_amount)
                                # Append new sale record representing this settlement (routing cash injection)
                                db_logic.append_sales_record(
                                    customer_name=selected_cust_row["Customer_Name"],
                                    customer_phone=selected_cust_row["Customer_Phone"],
                                    total_amount=0.0,
                                    amount_paid=c_settle_amount,
                                    is_credit=False,
                                    payment_method=selected_settle_method,
                                    cheque_details=selected_settle_cheque
                                )
                                st.success("🎉 Google Sheet updated successfully!")
                            else:
                                df_s = st.session_state.sales_df
                                idx = df_s[df_s["ID"] == selected_cust_id].index[0]
                                df_s.at[idx, "Amount_Paid"] = round(float(df_s.at[idx, "Amount_Paid"]) + c_settle_amount, 2)
                                df_s.at[idx, "Balance_Due"] = round(float(df_s.at[idx, "Total_Amount"]) - float(df_s.at[idx, "Amount_Paid"]), 2)
                                
                                # Append new mock settlement record
                                tx_id = f"tx-s-mock-settle-{uuid.uuid4().hex[:4]}"
                                new_entry = {
                                    "Date": datetime.date.today(),
                                    "Customer_Name": selected_cust_row["Customer_Name"],
                                    "Customer_Phone": selected_cust_row["Customer_Phone"],
                                    "Total_Amount": 0.0,
                                    "Amount_Paid": c_settle_amount,
                                    "Balance_Due": 0.0,
                                    "ID": tx_id,
                                    "Type": "Cash",
                                    "Payment_Method": selected_settle_method,
                                    "Cheque_Details": selected_settle_cheque
                                }
                                st.session_state.sales_df = pd.concat([df_s, pd.DataFrame([new_entry])], ignore_index=True)
                                st.success("🎉 Sandbox updated successfully!")
                            load_udharo_data(force=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error settling: {e}")
                            
                with col_btn2:
                    if st.button("✅ Clear Debt", type="primary", use_container_width=True):
                        try:
                            remaining_debt = float(selected_cust_row["Balance_Due"])
                            if st.session_state.mode == "live":
                                db_logic.clear_customer_debt(selected_cust_id)
                                # Append new sale record representing this settlement (routing cash injection)
                                db_logic.append_sales_record(
                                    customer_name=selected_cust_row["Customer_Name"],
                                    customer_phone=selected_cust_row["Customer_Phone"],
                                    total_amount=0.0,
                                    amount_paid=remaining_debt,
                                    is_credit=False,
                                    payment_method=selected_settle_method,
                                    cheque_details=selected_settle_cheque
                                )
                                st.success("🎉 Debt fully cleared in Google Sheet!")
                            else:
                                df_s = st.session_state.sales_df
                                idx = df_s[df_s["ID"] == selected_cust_id].index[0]
                                df_s.at[idx, "Amount_Paid"] = df_s.at[idx, "Total_Amount"]
                                df_s.at[idx, "Balance_Due"] = 0.0
                                
                                # Append new mock settlement record
                                tx_id = f"tx-s-mock-settle-{uuid.uuid4().hex[:4]}"
                                new_entry = {
                                    "Date": datetime.date.today(),
                                    "Customer_Name": selected_cust_row["Customer_Name"],
                                    "Customer_Phone": selected_cust_row["Customer_Phone"],
                                    "Total_Amount": 0.0,
                                    "Amount_Paid": remaining_debt,
                                    "Balance_Due": 0.0,
                                    "ID": tx_id,
                                    "Type": "Cash",
                                    "Payment_Method": selected_settle_method,
                                    "Cheque_Details": selected_settle_cheque
                                }
                                st.session_state.sales_df = pd.concat([df_s, pd.DataFrame([new_entry])], ignore_index=True)
                                st.success("🎉 Debt fully cleared in Sandbox!")
                            load_udharo_data(force=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error clearing: {e}")

    # --- SUPPLIER PAYABLES TAB ---
    with tab_supp:
        st.markdown("### 🏢 Supplier Payables (Outstanding Debts)")
        
        col_p_left, col_p_right = st.columns([2, 1])
        
        with col_p_left:
            # Search bar
            search_supp = st.text_input("🔍 Search Supplier by Name or Phone", placeholder="Type name or phone number...", key="search_supp_input")
            
            # Filter active payables (Balance_Due > 0)
            supp_table_df = purchases_df[purchases_df["Balance_Due"] > 0].copy() if not purchases_df.empty else pd.DataFrame()
            if not supp_table_df.empty:
                supp_table_df["Supplier_Phone"] = supp_table_df["Supplier_Phone"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True)
            
            if search_supp and not supp_table_df.empty:
                supp_table_df = supp_table_df[
                    supp_table_df["Supplier_Name"].str.contains(search_supp, case=False, na=False) |
                    supp_table_df["Supplier_Phone"].str.contains(search_supp, case=False, na=False)
                ]
                
            st.markdown(f"**Found {len(supp_table_df)} outstanding supplier debt obligations**")
            
            if not supp_table_df.empty:
                st.data_editor(
                    supp_table_df,
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                        "Supplier_Name": st.column_config.TextColumn("Supplier Name", width="medium"),
                        "Supplier_Phone": st.column_config.TextColumn("Phone Number"),
                        "Total_Amount": st.column_config.NumberColumn("Total Amount (Rs.)", format="Rs. %.2f"),
                        "Amount_Paid": st.column_config.NumberColumn("Amount Paid (Rs.)", format="Rs. %.2f"),
                        "Balance_Due": st.column_config.NumberColumn("Balance Due (Rs.)", format="Rs. %.2f"),
                        "Type": st.column_config.TextColumn("Status"),
                        "ID": st.column_config.TextColumn("ID", disabled=True)
                    },
                    hide_index=True,
                    use_container_width=True,
                    disabled=True,
                    key="supp_outstanding_table"
                )
            else:
                st.info("🎉 Excellent! We owe no money to any suppliers.")
                
            # Expandable form to add new Purchases entry (with Dynamic UI Logic)
            with st.expander("➕ Record New Supplier Purchase"):
                col_fp1, col_fp2 = st.columns(2)
                with col_fp1:
                    p_date = st.date_input("Purchase Date", value=datetime.date.today(), key="purchase_date_input")
                    p_method = st.selectbox(
                        "Payment Method *",
                        options=['Cash', 'Cheque', 'Fonepay', 'eSewa', 'Khalti', 'Bank Transfer', 'Udharo'],
                        index=6,  # Default to Udharo for supplier obligations context
                        key="purchase_payment_method"
                    )
                    
                    # Optional Cheque Number & Bank Name
                    p_cheque_details = ""
                    if p_method == "Cheque":
                        p_cheque_details = st.text_input("Cheque Number & Bank Name (Optional)", placeholder="E.g., Cheque #112233 - Himalayan Bank", key="purchase_cheque_details")
                    
                    # Required Supplier Name and Phone Number only for Udharo
                    if p_method == "Udharo":
                        p_name = st.text_input("Supplier Name *", key="purchase_supp_name")
                        p_phone = st.text_input("Supplier Phone Number *", key="purchase_supp_phone")
                    else:
                        p_name = st.text_input("Supplier Name (Optional)", value="Standard Supplier", key="purchase_supp_name")
                        p_phone = st.text_input("Supplier Phone (Optional)", value="N/A", key="purchase_supp_phone")

                with col_fp2:
                    p_total = st.number_input("Total Amount (Rs.) *", min_value=0.01, step=100.0, value=1000.0, key="purchase_total_amount")
                    if p_method == "Udharo":
                        p_paid = st.number_input("Amount Paid (Rs.)", min_value=0.00, step=100.0, value=0.0, key="purchase_amount_paid")
                    else:
                        p_paid = p_total # Automatically fully paid for non-credit purchases
                        st.info(f"ℹ️ Amount Paid automatically set to Total Amount (Rs. {p_total:,.2f}) for non-Udharo purchases.")

                submit_purchase = st.button("💾 Save Supplier Purchase", type="primary", use_container_width=True, key="save_purchase_btn")
                
                if submit_purchase:
                    if p_method == "Udharo" and (not p_name.strip() or not p_phone.strip()):
                        st.error("❌ Supplier Name and Phone Number are required for credit purchases (Udharo)!")
                    elif not p_name.strip():
                        st.error("❌ Supplier Name cannot be empty!")
                    elif p_paid > p_total:
                        st.error("❌ Amount Paid cannot be greater than Total Amount!")
                    else:
                        try:
                            if st.session_state.mode == "live":
                                db_logic.append_purchases_record(
                                    supplier_name=p_name,
                                    supplier_phone=p_phone,
                                    total_amount=p_total,
                                    amount_paid=p_paid,
                                    is_credit=(p_method == "Udharo"),
                                    date=p_date,
                                    payment_method=p_method,
                                    cheque_details=p_cheque_details
                                )
                                st.success(f"🎉 Successfully recorded purchase to Google Sheets!")
                            else:
                                # Sandbox mock append
                                tx_id = f"tx-p-mock-{uuid.uuid4().hex[:4]}"
                                total_val = round(float(p_total), 2)
                                paid_val = round(float(p_paid), 2)
                                due_val = round(total_val - paid_val, 2)
                                tx_type = "Udharo" if (p_method == "Udharo") else "Cash"
                                new_entry = {
                                    "Date": p_date,
                                    "Supplier_Name": p_name.strip(),
                                    "Supplier_Phone": p_phone.strip(),
                                    "Total_Amount": total_val,
                                    "Amount_Paid": paid_val,
                                    "Balance_Due": due_val,
                                    "ID": tx_id,
                                    "Type": tx_type,
                                    "Payment_Method": p_method,
                                    "Cheque_Details": p_cheque_details
                                }
                                st.session_state.purchases_df = pd.concat([st.session_state.purchases_df, pd.DataFrame([new_entry])], ignore_index=True)
                                st.success(f"🎉 Successfully recorded purchase to Sandbox memory!")
                            load_udharo_data(force=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to record purchase: {e}")
                                
        with col_p_right:
            st.markdown("### 🏢 Debt Payments")
            st.markdown("Settle supplier debts here.")
            
            outstanding_supps = purchases_df[purchases_df["Balance_Due"] > 0].copy() if not purchases_df.empty else pd.DataFrame()
            
            if outstanding_supps.empty:
                st.info("No supplier debt obligations to pay.")
            else:
                supp_options = [f"{row['ID']} - {row['Supplier_Name']} (We Owe Rs. {row['Balance_Due']:.2f})" for _, row in outstanding_supps.iterrows()]
                selected_supp_opt = st.selectbox("Select Supplier to Settle", options=supp_options)
                
                selected_supp_id = selected_supp_opt.split(" - ")[0]
                selected_supp_row = outstanding_supps[outstanding_supps["ID"] == selected_supp_id].iloc[0]
                
                # Settle payment method dropdown
                selected_supp_settle_method = st.selectbox(
                    "Settlement Method *",
                    options=['Cash', 'Cheque', 'Fonepay', 'eSewa', 'Khalti', 'Bank Transfer'],
                    index=0,
                    key="supp_settle_method"
                )
                
                selected_supp_settle_cheque = ""
                if selected_supp_settle_method == "Cheque":
                    selected_supp_settle_cheque = st.text_input("Cheque Details (Optional)", placeholder="E.g., Cheque #45456 - Nepal Bank", key="supp_settle_cheque_details")
                
                p_settle_amount = st.number_input(
                    "Amount Paid (Rs.)", 
                    min_value=0.01, 
                    max_value=float(selected_supp_row["Balance_Due"]), 
                    value=float(selected_supp_row["Balance_Due"]), 
                    step=10.0,
                    key="supp_settle_input"
                )
                
                col_pbtn1, col_pbtn2 = st.columns(2)
                with col_pbtn1:
                    if st.button("💸 Partially Pay", use_container_width=True, key="supp_part_pay_btn"):
                        try:
                            if st.session_state.mode == "live":
                                db_logic.settle_supplier_debt(selected_supp_id, p_settle_amount)
                                # Append new purchases record representing this settlement (routing cash outflow)
                                db_logic.append_purchases_record(
                                    supplier_name=selected_supp_row["Supplier_Name"],
                                    supplier_phone=selected_supp_row["Supplier_Phone"],
                                    total_amount=0.0,
                                    amount_paid=p_settle_amount,
                                    is_credit=False,
                                    payment_method=selected_supp_settle_method,
                                    cheque_details=selected_supp_settle_cheque
                                )
                                st.success("🎉 Google Sheet updated successfully!")
                            else:
                                df_p = st.session_state.purchases_df
                                idx = df_p[df_p["ID"] == selected_supp_id].index[0]
                                df_p.at[idx, "Amount_Paid"] = round(float(df_p.at[idx, "Amount_Paid"]) + p_settle_amount, 2)
                                df_p.at[idx, "Balance_Due"] = round(float(df_p.at[idx, "Total_Amount"]) - float(df_p.at[idx, "Amount_Paid"]), 2)
                                
                                # Append new mock settlement record
                                tx_id = f"tx-p-mock-settle-{uuid.uuid4().hex[:4]}"
                                new_entry = {
                                    "Date": datetime.date.today(),
                                    "Supplier_Name": selected_supp_row["Supplier_Name"],
                                    "Supplier_Phone": selected_supp_row["Supplier_Phone"],
                                    "Total_Amount": 0.0,
                                    "Amount_Paid": p_settle_amount,
                                    "Balance_Due": 0.0,
                                    "ID": tx_id,
                                    "Type": "Cash",
                                    "Payment_Method": selected_supp_settle_method,
                                    "Cheque_Details": selected_supp_settle_cheque
                                }
                                st.session_state.purchases_df = pd.concat([df_p, pd.DataFrame([new_entry])], ignore_index=True)
                                st.success("🎉 Sandbox updated successfully!")
                            load_udharo_data(force=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error settling: {e}")
                            
                with col_pbtn2:
                    if st.button("✅ Clear Obligation", type="primary", use_container_width=True, key="supp_clear_pay_btn"):
                        try:
                            remaining_obligation = float(selected_supp_row["Balance_Due"])
                            if st.session_state.mode == "live":
                                db_logic.clear_supplier_debt(selected_supp_id)
                                # Append new purchases record representing this settlement (routing cash outflow)
                                db_logic.append_purchases_record(
                                    supplier_name=selected_supp_row["Supplier_Name"],
                                    supplier_phone=selected_supp_row["Supplier_Phone"],
                                    total_amount=0.0,
                                    amount_paid=remaining_obligation,
                                    is_credit=False,
                                    payment_method=selected_supp_settle_method,
                                    cheque_details=selected_supp_settle_cheque
                                )
                                st.success("🎉 Debt fully cleared in Google Sheet!")
                            else:
                                df_p = st.session_state.purchases_df
                                idx = df_p[df_p["ID"] == selected_supp_id].index[0]
                                df_p.at[idx, "Amount_Paid"] = df_p.at[idx, "Total_Amount"]
                                df_p.at[idx, "Balance_Due"] = 0.0
                                
                                # Append new mock settlement record
                                tx_id = f"tx-p-mock-settle-{uuid.uuid4().hex[:4]}"
                                new_entry = {
                                    "Date": datetime.date.today(),
                                    "Supplier_Name": selected_supp_row["Supplier_Name"],
                                    "Supplier_Phone": selected_supp_row["Supplier_Phone"],
                                    "Total_Amount": 0.0,
                                    "Amount_Paid": remaining_obligation,
                                    "Balance_Due": 0.0,
                                    "ID": tx_id,
                                    "Type": "Cash",
                                    "Payment_Method": selected_supp_settle_method,
                                    "Cheque_Details": selected_supp_settle_cheque
                                }
                                st.session_state.purchases_df = pd.concat([df_p, pd.DataFrame([new_entry])], ignore_index=True)
                                st.success("🎉 Debt fully cleared in Sandbox!")
                            load_udharo_data(force=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error clearing: {e}")
