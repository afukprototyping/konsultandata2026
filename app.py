import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="GSB Admin Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Dark Mode & Modern Minimalist CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background-color: #0F172A;
}
#MainMenu, footer, header {
    visibility: hidden;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* Header Styling */
.header-container {
    background-color: #1E293B;
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #334155;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}
.header-title {
    color: #F8FAFC;
    font-size: 1.75rem;
    font-weight: 800;
    margin: 0 0 4px 0;
    letter-spacing: -0.025em;
}
.header-subtitle {
    color: #94A3B8;
    font-size: 0.875rem;
    margin: 0;
    font-weight: 500;
}
.header-kpi-label {
    color: #94A3B8;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-align: right;
    margin-bottom: 4px;
}
.header-kpi-value {
    color: #38BDF8;
    font-size: 2.25rem;
    font-weight: 800;
    line-height: 1;
    text-align: right;
}

/* Section Styling */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #334155;
}

/* Metric Cards HTML */
.custom-metric-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
    height: 100%;
}
.cmc-label {
    color: #94A3B8;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.cmc-value {
    color: #F8FAFC;
    font-size: 1.875rem;
    font-weight: 800;
    line-height: 1.2;
}
.cmc-caption {
    color: #64748B;
    font-size: 0.75rem;
    margin-top: 8px;
    font-weight: 500;
}
.cmc-value.warning {
    color: #F87171;
}

/* Financial Cards (Tax Section) */
.fin-card {
    border-radius: 10px;
    padding: 20px;
    border: 1px solid #334155;
    background: #1E293B;
}

/* Streamlit Overrides for Dark Mode */
.stDataFrame {
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


def check_password():
    def _submit():
        st.session_state["auth_ok"] = (
            st.session_state["_pw"] == st.secrets["APP_PASSWORD"]
        )
        del st.session_state["_pw"]

    if st.session_state.get("auth_ok"):
        return True

    failed = st.session_state.get("auth_ok") is False
    title  = "Access Denied" if failed else "GSB Authentication"
    note   = "Invalid credentials." if failed else "Enter password to access the dashboard."

    st.markdown(
        f'<div style="max-width:400px;margin:80px auto;background:#1E293B;border:1px solid #334155;border-radius:12px;'
        f'padding:40px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.3);text-align:center;">'
        f'<h2 style="margin:0 0 8px;font-weight:800;font-size:1.5rem;color:#F8FAFC;">{title}</h2>'
        f'<p style="margin:0 0 24px;color:#94A3B8;font-size:0.875rem;">{note}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div style="margin-top:-75px;"></div>', unsafe_allow_html=True)
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Password...")
    return False

if not check_password():
    st.stop()


def _find_col(df: pd.DataFrame, exact: str, keyword: str) -> str | None:
    if exact in df.columns:
        return exact
    for c in df.columns:
        if keyword.lower() in str(c).lower():
            return c
    return None


@st.cache_data(ttl=600)
def load_data():
    scope  = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds  = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    df1 = pd.DataFrame(client.open_by_url(st.secrets["URL_SPS1"]).sheet1.get_all_records())
    df2 = pd.DataFrame(client.open_by_url(st.secrets["URL_SPS2"]).sheet1.get_all_records())

    df2 = df2.iloc[24:].copy()
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    col_id      = _find_col(df2, "ID Klien (26.XXX)\nisi 3 angka belakang saja", "ID Klien")
    col_nom     = _find_col(df2, "Nominal yang diberikan", "Nominal")
    col_layanan = _find_col(df1, "Layanan yang diinginkan", "Layanan")
    col_nama    = _find_col(df1, "Nama Klien", "Nama")

    if not col_id or not col_nom:
        raise ValueError(f"Critical columns not found. SPS2 Columns: {list(df2.columns)}")

    # Standardize ID and Nominal
    df2[col_id]  = df2[col_id].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    # Generate Expected IDs for Incoming Clients based on row index (1 becomes 001, 2 becomes 002, etc.)
    df1['Generated_ID'] = (df1.index + 1).astype(str).str.zfill(3)

    return df1, df2, col_id, col_nom, col_layanan, col_nama


try:
    df_incoming, df_completed, COL_ID, COL_NOM, COL_LAYANAN, COL_NAMA = load_data()
except Exception as e:
    st.error(f"Failed to fetch data. Details: {e}")
    st.stop()


# Variables & Calculations
COMMITMENT_FEE = 50_000

total_incoming = len(df_incoming)
total_completed = len(df_completed)
total_pending  = total_incoming - total_completed
profit_completed = df_completed[COL_NOM].sum()
total_commitment = total_incoming * COMMITMENT_FEE
total_kpi      = profit_completed + total_commitment


def calculate_tax(nominal: float) -> float:
    if nominal < 150_000:  return 0.0
    if nominal <= 500_000: return nominal * 0.10
    return nominal * 0.12


pajak_df = (
    df_completed.groupby(COL_ID)[COL_NOM]
    .sum().reset_index()
    .rename(columns={COL_ID: "Client ID", COL_NOM: "Gross Accumulation"})
)
pajak_df["Tax Liability"] = pajak_df["Gross Accumulation"].apply(calculate_tax)
pajak_df["Net Revenue"]   = pajak_df["Gross Accumulation"] - pajak_df["Tax Liability"]

accum_gross = pajak_df["Gross Accumulation"].sum()
accum_tax   = pajak_df["Tax Liability"].sum()
accum_net   = pajak_df["Net Revenue"].sum()


# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
st.markdown(f"""
<div class="header-container">
    <div>
        <h1 class="header-title">GSB Administration Dashboard</h1>
        <p class="header-subtitle">Data Analytics Department &middot; KPI & Client Tracking</p>
    </div>
    <div>
        <div class="header-kpi-label">Estimated KPI Valuation</div>
        <div class="header-kpi-value">Rp {total_kpi:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 1: EXECUTIVE SUMMARY
# ---------------------------------------------------------
st.markdown('<div class="section-title">1. Executive Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Incoming Clients</div>
        <div class="cmc-value">{total_incoming}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Completed Clients</div>
        <div class="cmc-value">{total_completed}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    warning_class = "warning" if total_pending < 0 else ""
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Pending Clients</div>
        <div class="cmc-value {warning_class}">{total_pending}</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Base Revenue</div>
        <div class="cmc-value" style="font-size:1.5rem;">Rp {profit_completed:,.0f}</div>
        <div class="cmc-caption">+ Rp {total_commitment:,.0f} (Commitment Fees)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 2: TAX LIABILITY
# ---------------------------------------------------------
st.markdown('<div class="section-title">2. Tax Liability Summary</div>', unsafe_allow_html=True)

# Accumulation Cards (Moved ABOVE the table)
t1, t2, t3 = st.columns(3)
with t1:
    st.markdown(f"""
    <div class="fin-card">
        <div class="cmc-label">Total Gross Accumulation</div>
        <div class="cmc-value" style="font-size:1.5rem; color:#F8FAFC;">Rp {accum_gross:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with t2:
    st.markdown(f"""
    <div class="fin-card" style="border-color:#7F1D1D; background:#450A0A;">
        <div class="cmc-label" style="color:#FCA5A5;">Total Tax Liability</div>
        <div class="cmc-value" style="font-size:1.5rem; color:#F87171;">Rp {accum_tax:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with t3:
    st.markdown(f"""
    <div class="fin-card" style="border-color:#14532D; background:#052E16;">
        <div class="cmc-label" style="color:#86EFAC;">Total Net Revenue</div>
        <div class="cmc-value" style="font-size:1.5rem; color:#4ADE80;">Rp {accum_net:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tax Table formatting
display_pajak = pajak_df.copy()
for col in ["Gross Accumulation", "Tax Liability", "Net Revenue"]:
    display_pajak[col] = display_pajak[col].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(display_pajak, use_container_width=True, hide_index=True)
st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 3: CLIENT SERVICE DISTRIBUTION (PIE CHART)
# ---------------------------------------------------------
st.markdown('<div class="section-title">3. Client Service Distribution</div>', unsafe_allow_html=True)

if COL_LAYANAN and COL_LAYANAN in df_incoming.columns:
    service_dist = df_incoming[COL_LAYANAN].value_counts().reset_index()
    service_dist.columns = ["Service Type", "Number of Clients"]
    
    col_a, col_b = st.columns([1.2, 2])
    with col_a:
        st.dataframe(service_dist, use_container_width=True, hide_index=True)
    with col_b:
        # Plotly Donut Chart optimized for Dark Mode
        fig = px.pie(service_dist, values='Number of Clients', names='Service Type', hole=0.45)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='#F8FAFC'),
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Service column not found in incoming database.")

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION 4: PENDING CLIENTS TRACKER
# ---------------------------------------------------------
st.markdown('<div class="section-title">4. Unrecorded / Pending Clients</div>', unsafe_allow_html=True)

# Tracking Logic: Filter out IDs that already exist in the completed dataframe
completed_ids = df_completed[COL_ID].tolist()
pending_df = df_incoming[~df_incoming['Generated_ID'].isin(completed_ids)].copy()

if pending_df.empty:
    st.success("🎉 All incoming clients have been successfully processed and recorded!")
else:
    # Determine columns to display
    display_cols = ['Generated_ID']
    if COL_NAMA and COL_NAMA in pending_df.columns:
        display_cols.append(COL_NAMA)
    if COL_LAYANAN and COL_LAYANAN in pending_df.columns:
        display_cols.append(COL_LAYANAN)
    
    clean_pending_df = pending_df[display_cols].rename(columns={'Generated_ID': 'Assigned ID'})
    st.dataframe(clean_pending_df, use_container_width=True, hide_index=True)
