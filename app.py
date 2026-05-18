# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import uuid
import altair as alt
from streamlit_gsheets import GSheetsConnection

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

MOCK_TRANSACTIONS = [
    {"ID": "tx-1001", "Date": "2026-05-10", "Description": "Client Milestone Payment: Website Redesign", "Category": "Services", "Type": "Credit", "Amount": 2500.00},
    {"ID": "tx-1002", "Date": "2026-05-11", "Description": "Monthly Coworking Office Rent", "Category": "Office Rent", "Type": "Debit", "Amount": 450.00},
    {"ID": "tx-1003", "Date": "2026-05-12", "Description": "Vercel & Figma Team Subscriptions", "Category": "Software", "Type": "Debit", "Amount": 89.00},
    {"ID": "tx-1004", "Date": "2026-05-14", "Description": "Retainer Invoice: UX Strategy Consulting", "Category": "Services", "Type": "Credit", "Amount": 1200.00},
    {"ID": "tx-1005", "Date": "2026-05-15", "Description": "Paper, Notebooks, and Desk Supplies", "Category": "Supplies", "Type": "Debit", "Amount": 45.50},
    {"ID": "tx-1006", "Date": "2026-05-16", "Description": "LinkedIn Ads Lead Gen Campaign", "Category": "Marketing", "Type": "Debit", "Amount": 300.00},
    {"ID": "tx-1007", "Date": "2026-05-17", "Description": "Contractor Payout: Technical SEO Audit", "Category": "Consulting", "Type": "Debit", "Amount": 600.00},
    {"ID": "tx-1008", "Date": "2026-05-18", "Description": "Project Milestone 2: Backend Development", "Category": "Services", "Type": "Credit", "Amount": 3200.00},
]

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
    st.session_state.demo_df = pd.DataFrame(MOCK_TRANSACTIONS)

# Cache clear helper to force read fresh gsheets data
def force_refresh():
    st.cache_data.clear()

# ==============================================================================
# HEADER BANNER & SIDEBAR INTEGRATION CONTROL
# ==============================================================================
st.markdown("""
    <div class="header-banner">
        <div class="header-title">⚖️ Dr-Cr Ledger Pro</div>
        <div class="header-subtitle">Secure Accounting Ledger with Real-time Google Sheets CRUD Operations</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar Design
with st.sidebar:
    st.markdown("<h3 style='margin-top:0;'>🛠️ Connection Control</h3>", unsafe_allow_html=True)
    
    # Elegant connection status indicator
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
        
    # Mode selector (only selectable if secrets are configured; otherwise locked to Demo Mode)
    mode_options = ["Demo / Sandbox Mode", "Live Google Sheets Connection"]
    selected_mode_idx = 1 if (st.session_state.mode == "live" and secrets_configured) else 0
    
    mode_selection = st.radio(
        "Select Operation Mode",
        options=mode_options,
        index=selected_mode_idx,
        disabled=not secrets_configured,
        help="To enable 'Live Connection', follow the secrets configuration instructions to add your Google Service Account credentials."
    )
    
    # Update active mode
    if mode_selection == "Live Google Sheets Connection" and secrets_configured:
        st.session_state.mode = "live"
    else:
        st.session_state.mode = "demo"
        
    # Manual Refresh button for live mode
    if st.session_state.mode == "live":
        st.button("🔄 Sync with Google Sheets", on_click=force_refresh, use_container_width=True)
        
    st.markdown("---")
    

    
    # Information & Onboarding card
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
# DATA SYNCHRONIZATION (READ)
# ==============================================================================
# Load data depending on the chosen mode
df = pd.DataFrame(columns=DEFAULT_COLUMNS)
error_message = None

if st.session_state.mode == "live":
    try:
        # Establish the Google Sheets connection
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Read from the configured spreadsheet. By default, it reads the first sheet
        df = conn.read(ttl="5s")
        
        # Ensure we have all correct columns, standardizing names
        if df is not None and not df.empty:
            # If spreadsheet was read but has columns matching, verify and clean
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            for col in DEFAULT_COLUMNS:
                if col not in df.columns:
                    df[col] = None
            df = df[DEFAULT_COLUMNS]
        else:
            # Initialize sheet with headers if empty
            df = pd.DataFrame(columns=DEFAULT_COLUMNS)
            conn.update(data=df)
            
    except Exception as e:
        error_message = str(e)
        st.error(f"❌ Google Sheets Connection Error: {error_message}")
        st.info("⚠️ Falling back to sandbox Demo Mode. Please check your `.streamlit/secrets.toml` parameters or spreadsheet permissions.")
        st.session_state.mode = "demo"
        df = st.session_state.demo_df.copy()
else:
    # Read sandbox data from session state
    df = st.session_state.demo_df.copy()

# Ensure types are correct
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
df["Type"] = df["Type"].fillna("Debit")
df["Category"] = df["Category"].fillna("Miscellaneous")
df["Description"] = df["Description"].fillna("No details provided")

# ==============================================================================
# LEDGER SETTINGS & OPENING BALANCE INTERCONNECT
# ==============================================================================
detected_opening = 0.0
# Find if an Opening Balance transaction already exists in the loaded DataFrame
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
        help="Specify the starting balance of this ledger. You can save/update this value in your Google Sheet spreadsheet below."
    )
    
    # Render save button if the value in the input field differs from the spreadsheet row
    if opening_balance != detected_opening:
        if st.button("💾 Save Balance to Google Sheet", use_container_width=True, type="primary"):
            # Update or create the Opening Balance row
            updated_df = df.copy()
            
            # Find matching row indices
            opening_idx = updated_df[(updated_df["Category"] == "Opening Balance") | (updated_df["Description"] == "Opening Balance")].index
            
            if not opening_idx.empty:
                if opening_balance == 0.0:
                    # If set to zero, remove it entirely
                    updated_df = updated_df.drop(opening_idx)
                else:
                    # Update existing opening balance entry
                    updated_df.at[opening_idx[0], "Amount"] = round(opening_balance, 2)
                    updated_df.at[opening_idx[0], "Type"] = "Credit"
                    updated_df.at[opening_idx[0], "Date"] = (df["Date"].min() if not df.empty and pd.notnull(df["Date"].min()) else datetime.date.today()).strftime("%Y-%m-%d")
            elif opening_balance > 0.0:
                # Add new opening balance entry at the beginning
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
            
            # Save updated data
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

# ==============================================================================
# FINANCIAL COMPUTATIONS
# ==============================================================================
total_debits = df[(df["Type"] == "Debit") & (df["Category"] != "Opening Balance")]["Amount"].sum()   # Outflow (DR)
total_credits = df[(df["Type"] == "Credit") & (df["Category"] != "Opening Balance")]["Amount"].sum() # Inflow (CR)
net_balance = opening_balance + total_credits - total_debits # Balance = Opening + Credit (Inflow) - Debit (Outflow)

# Render HTML metric cards with premium design and colors
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

# ==============================================================================
# MAIN TABS: VISUALIZATION, LEDGER VIEW & CRUD OPERATIONS
# ==============================================================================
tab_dashboard, tab_create, tab_update, tab_delete = st.tabs([
    "📊 Ledger Insights & Analytics",
    "➕ Create Ledger Entry (Insert)",
    "✏️ Update Ledger Entry (Edit)",
    "❌ Delete Ledger Entry (Remove)"
])

# ------------------------------------------------------------------------------
# TAB 1: DASHBOARD, SEARCH, FILTERS & ANALYTICS
# ------------------------------------------------------------------------------
with tab_dashboard:
    col_filters, col_charts = st.columns([1, 2])
    
    with col_filters:
        st.markdown("### 🔍 Search & Filters")
        search_query = st.text_input("Search description or ID", placeholder="Search transactions...")
        filter_category = st.multiselect("Filter by Category", options=CATEGORIES, default=[])
        filter_type = st.multiselect("Filter by Type", options=["Debit", "Credit"], default=[])
        
        # Apply filters
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
        
        # Display Transaction Table beautifully using Streamlit Data Editor
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
            # 1. Timeline Cumulative Balance Chart
            # Prepare data: Sort by date
            chart_df = filtered_df.copy()
            chart_df['Date_Parsed'] = pd.to_datetime(chart_df['Date'])
            chart_df = chart_df.sort_values(by='Date_Parsed')
            
            # Net Value per transaction (Positive for Credit/Inflow, Negative for Debit/Outflow)
            chart_df['Net_Value'] = chart_df.apply(
                lambda row: row['Amount'] if row['Type'] == 'Credit' else -row['Amount'], axis=1
            )
            
            # Calculate cumulative balance
            chart_df['Cumulative_Balance'] = opening_balance + chart_df['Net_Value'].cumsum()
            
            # Line Chart using Altair for state-of-the-art visuals
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
            
            # 2. Expenses Category Breakdowns (Pie/Donut and Bar side-by-side)
            col_chart_left, col_chart_right = st.columns(2)
            
            with col_chart_left:
                # Category Volume
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
                # Debit vs Credit Distribution
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

# ------------------------------------------------------------------------------
# TAB 2: CREATE / INSERT OPERATION
# ------------------------------------------------------------------------------
with tab_create:
    st.markdown("### ➕ Record a New Transaction")
    st.markdown("Fill in the fields below to add a transaction to your ledger.")
    
    with st.form("insert_transaction_form", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        
        with col_c1:
            tx_date = st.date_input("Transaction Date", value=datetime.date.today())
            tx_type = st.selectbox("Entry Type (DR/CR)", options=["Debit", "Credit"], 
                                   help="Debit represents an outflow (expense); Credit represents an inflow (income).")
        
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
                # Generate unique ID for CRUD targeting
                new_id = f"tx-{uuid.uuid4().hex[:6]}"
                
                # Force Cash Withdrawal to Debit (DR - Outflow)
                final_type = tx_type
                if tx_category == "Cash Withdrawal":
                    final_type = "Debit"
                    st.toast("ℹ️ Automatically listed as Debit (DR) for Cash Withdrawal.")
                
                # Construct new record
                new_entry = {
                    "ID": new_id,
                    "Date": tx_date.strftime("%Y-%m-%d"),
                    "Description": tx_desc.strip(),
                    "Category": tx_category,
                    "Type": final_type,
                    "Amount": round(tx_amount, 2)
                }
                
                # Append to active DataFrame
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                
                # Save data based on mode
                if st.session_state.mode == "live":
                    try:
                        conn.update(data=updated_df)
                        st.success(f"🎉 Successfully inserted transaction '{tx_desc}' to Google Sheet!")
                        st.balloons()
                        # Force refresh
                        force_refresh()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to save to Google Sheets: {e}")
                else:
                    st.session_state.demo_df = updated_df
                    st.success(f"🎉 Successfully registered transaction '{tx_desc}' in Demo Sandbox!")
                    st.toast("Updated demo ledger in memory!")
                    st.rerun()

# ------------------------------------------------------------------------------
# TAB 3: UPDATE / EDIT OPERATION
# ------------------------------------------------------------------------------
with tab_update:
    st.markdown("### ✏️ Edit an Existing Transaction")
    st.markdown("Select a transaction from the list to modify its contents.")
    
    if df.empty:
        st.info("💡 The ledger is empty. Create some entries first.")
    else:
        # Create a dropdown mapping ID + Description for easy targeting
        select_options = [f"{row['ID']} - {row['Description']} (Rs. {row['Amount']:.2f})" for _, row in df.iterrows()]
        selected_option = st.selectbox("Select Transaction to Edit", options=select_options)
        
        # Extract ID
        selected_id = selected_option.split(" - ")[0]
        selected_row = df[df["ID"] == selected_id].iloc[0]
        
        # Render edit form
        with st.form("update_transaction_form"):
            st.markdown(f"**Editing Transaction: `{selected_id}`**")
            col_u1, col_u2, col_u3 = st.columns(3)
            
            with col_u1:
                # Handle both datetime/date objects and strings gracefully
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
                # Find index of original category
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
                    # Update row in-place
                    updated_df = df.copy()
                    row_idx = updated_df[updated_df["ID"] == selected_id].index[0]
                    
                    # Force Cash Withdrawal to Debit (DR - Outflow)
                    final_u_type = u_type
                    if u_category == "Cash Withdrawal":
                        final_u_type = "Debit"
                        st.toast("ℹ️ Automatically forced to Debit (DR) for Cash Withdrawal.")
                    
                    updated_df.at[row_idx, "Date"] = u_date.strftime("%Y-%m-%d")
                    updated_df.at[row_idx, "Type"] = final_u_type
                    updated_df.at[row_idx, "Category"] = u_category
                    updated_df.at[row_idx, "Amount"] = round(u_amount, 2)
                    updated_df.at[row_idx, "Description"] = u_desc.strip()
                    
                    # Save
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

# ------------------------------------------------------------------------------
# TAB 4: DELETE / REMOVE OPERATION
# ------------------------------------------------------------------------------
with tab_delete:
    st.markdown("### ❌ Delete a Ledger Entry")
    st.markdown("Select a transaction to permanently remove it from your records.")
    
    if df.empty:
        st.info("💡 The ledger is empty.")
    else:
        # Select transaction to delete
        delete_options = [f"{row['ID']} - {row['Description']} (Rs. {row['Amount']:.2f})" for _, row in df.iterrows()]
        delete_selection = st.selectbox("Select Transaction to Delete", options=delete_options, key="del_select")
        
        # Extract target ID
        delete_id = delete_selection.split(" - ")[0]
        delete_row = df[df["ID"] == delete_id].iloc[0]
        
        # Show details inside a warning box
        st.warning(f"""
        **⚠️ Are you sure you want to permanently delete this transaction?**
        - **ID:** `{delete_row['ID']}`
        - **Date:** `{delete_row['Date']}`
        - **Description:** `{delete_row['Description']}`
        - **Category:** `{delete_row['Category']}`
        - **Type:** `{delete_row['Type']}` (DR/CR)
        - **Amount:** `Rs. {delete_row['Amount']:.2f}`
        """)
        
        col_d1, col_d2 = st.columns([1, 5])
        with col_d1:
            confirm_delete = st.button("🔴 Yes, Delete", use_container_width=True)
            
        if confirm_delete:
            # Filter out deleted record
            updated_df = df[df["ID"] != delete_id].copy()
            
            # Save
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

# ==============================================================================
# SECRETS AUTOMATED BUILDER (FOR NEW USERS)
# ==============================================================================
if not secrets_configured:
    st.markdown("---")
    st.markdown("## 🔑 Credentials TOML Builder")
    st.markdown("Copy your Google Cloud Service Account JSON contents and convert them to the proper Streamlit TOML structure below.")
    
    with st.expander("🛠️ Interactive Secrets Generator"):
        st.info("Input your credentials below to generate a valid `secrets.toml` content you can copy directly!")
        
        sheet_url = st.text_input("Spreadsheet URL", value="https://docs.google.com/spreadsheets/d/your-spreadsheet-id/edit")
        p_id = st.text_input("Project ID (project_id)", value="my-gcp-project-12345")
        pk_id = st.text_input("Private Key ID (private_key_id)", value="a1b2c3d4e5f6g7h8")
        pk = st.text_area("Private Key (private_key)", placeholder="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBg...\n-----END PRIVATE KEY-----\n")
        email = st.text_input("Client Email (client_email)", value="service-account@my-gcp-project-12345.iam.gserviceaccount.com")
        c_id = st.text_input("Client ID (client_id)", value="102938475647382910293")
        
        # Pre-format to avoid f-string backslash limitations in Python < 3.12
        formatted_pk = pk.replace('\n', '\\n') if pk else '-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n'
        escaped_email = email.replace('@', '%40') if email else ''
        
        # Build TOML string
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
        st.caption("ℹ️ Copy this generated snippet and paste it inside `.streamlit/secrets.toml` in your project workspace.")
