import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
import os

st.set_page_config(
    page_title="GSB Operations Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 1. CSS INJECTION (GSB BRANDING: ORANGE & NAVY)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Base App Background */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #F8FAFC !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
}

/* GSB Header (Orange & Navy Accents) */
.header-container {
    background: linear-gradient(135deg, #E8500A 0%, #C0392B 100%);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 15px rgba(232, 80, 10, 0.2);
}
.header-title {
    color: #FFFFFF !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.02em !important;
}
.header-subtitle {
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    font-weight: 500 !important;
}

/* Metric Cards (Navy Borders for Contrast) */
.metric-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid #1E3A8A; /* GSB Navy */
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    height: 100%;
}
.metric-card.orange-accent {
    border-top: 4px solid #E8500A; /* GSB Orange */
}
.metric-label {
    color: #64748B;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.metric-value {
    color: #0F172A;
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1.1;
}
.metric-subtext {
    color: #94A3B8;
    font-size: 0.8rem;
    margin-top: 8px;
    font-weight: 500;
}

/* Section Headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 800;
    color: #1E3A8A; /* GSB Navy */
    margin-top: 32px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #E2E8F0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Streamlit DataFrame Override */
.stDataFrame {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}

/* Login Box */
.login-box {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 6px solid #E8500A;
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    text-align: center;
}
.stTextInput input {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    padding: 14px !important;
    text-align: center !important;
}
.stTextInput input:focus {
    border-color: #1E3A8A !important;
    box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER & AUTHENTICATION
# ==========================================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def check_password():
    def _submit():
        st.session_state["auth_ok"] = (
            st.session_state["_pw"] == st.secrets["APP_PASSWORD"]
        )
        del st.session_state["_pw"]

    if st.session_state.get("auth_ok"):
        return True

    logo_b64 = get_base64_image("logo gsb.png")
    img_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 100px; width: auto; margin-bottom: 24px;">' if logo_b64 else ''

    _, mid, _ = st.columns([1, 1.2, 1])
    
    with mid:
        st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-box">
            {img_html}
            <h2 style="margin:0 0 8px; font-weight:800; font-size:1.75rem; color:#1E3A8A;">GSB Operations</h2>
            <p style="margin:0 0 24px; color:#64748B; font-size:0.95rem;">Authentication Required</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top:-70px; padding: 0 40px;">', unsafe_allow_html=True)
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Enter Password...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    return False

if not check_password():
    st.stop()

# ==========================================
# 3. DATA EXTRACTION & CLEANING
# ==========================================
def _find_col(df: pd.DataFrame, exact: str, keyword: str) -> str | None:
    if exact in df.columns: return exact
    for c in df.columns:
        if keyword.lower() in str(c).lower(): return c
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
    col_konsul  = _find_col(df1, "Konsultan", "Konsultan")

    if not col_id or not col_nom:
        raise ValueError("Critical columns missing in SPS 2.")

    df2[col_id]  = df2[col_id].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    col_id_sps1 = _find_col(df1, "ID Klien", "ID Klien")
    if not col_id_sps1:
        raise ValueError("Critical column 'ID Klien' missing in SPS 1.")
    
    df1['Generated_ID'] = df1[col_id_sps1].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)

    return df1, df2, col_id, col_nom, col_layanan, col_nama, col_konsul

try:
    df_incoming, df_completed, COL_ID, COL_NOM, COL_LAYANAN, COL_NAMA, COL_KONSULTAN = load_data()
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()

# ==========================================
# 4. METRICS CALCULATION
# ==========================================
COMMITMENT_FEE = 50_000

# Client & Revenue Metrics
total_incoming   = len(df_incoming)
total_completed  = len(df_completed)
total_pending    = total_incoming - total_completed
profit_completed = df_completed[COL_NOM].sum()
total_commitment = total_incoming * COMMITMENT_FEE
total_valuation  = profit_completed + total_commitment

# Tax Calculations
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


# ==========================================
# 5. SINGLE PAGE DASHBOARD RENDERING
# ==========================================

# -- HEADER --
logo_b64_header = get_base64_image("logo gsb.png")
img_header = f'<img src="data:image/png;base64,{logo_b64_header}" style="height: 48px; margin-right: 16px;">' if logo_b64_header else ''

st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center;">
        {img_header}
        <div>
            <h1 class="header-title">GSB Workspace</h1>
            <p class="header-subtitle">Data Analytics Department &middot; Operations Dashboard</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -- SECTION 1: EXECUTIVE METRICS --
st.markdown('<div class="section-header">1. Executive Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Incoming Clients</div>
        <div class="metric-value">{total_incoming}</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Completed Clients</div>
        <div class="metric-value">{total_completed}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    alert_class = "orange-accent" if total_pending > 0 else ""
    st.markdown(f"""
    <div class="metric-card {alert_class}">
        <div class="metric-label" style="color: {'#E8500A' if total_pending > 0 else '#64748B'};">Pending Clients</div>
        <div class="metric-value" style="color: {'#E8500A' if total_pending > 0 else '#0F172A'};">{total_pending}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card orange-accent">
        <div class="metric-label">Total Est. Value</div>
        <div class="metric-value" style="font-size: 1.5rem;">Rp {total_valuation:,.0f}</div>
        <div class="metric-subtext">Base: Rp {profit_completed:,.0f} <br> Admin: Rp {total_commitment:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)
with t1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Gross Tax Accumulation</div>
        <div class="metric-value">Rp {accum_gross:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with t2:
    st.markdown(f"""
    <div class="metric-card orange-accent">
        <div class="metric-label" style="color: #E8500A;">Total Tax Liability</div>
        <div class="metric-value" style="color: #E8500A;">Rp {accum_tax:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with t3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Net Revenue</div>
        <div class="metric-value">Rp {accum_net:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)


# -- SECTION 2: OPERATIONAL DISTRIBUTION (SIDE BY SIDE TABLES) --
st.markdown('<div class="section-header">2. Operational Workload</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown('<p style="font-weight: 700; color: #0F172A; margin-bottom: 8px;">Client Service Distribution</p>', unsafe_allow_html=True)
    if COL_LAYANAN and COL_LAYANAN in df_incoming.columns:
        service_dist = df_incoming[COL_LAYANAN].value_counts().reset_index()
        service_dist.columns = ["Service Type", "Clients Count"]
        st.dataframe(service_dist, use_container_width=True, hide_index=True)
    else:
        st.warning("Service column not found.")

with col_right:
    st.markdown('<p style="font-weight: 700; color: #0F172A; margin-bottom: 8px;">Consultant Workload Mapping</p>', unsafe_allow_html=True)
    CONSULTANTS_LIST = [
        "Helmi Falah", "Nyayu Azzahra Nabila", "Cut Ashifa Sawallida", "Retno Sari", 
        "Rizky Arif Wicaksono", "Pascal Arya Nugroho", "Muhammad Khayruhanif", 
        "Qanita Basimah Kurnia", "Afiq Dzakwan Anasti", "Azka Raditya Hafidz", 
        "Cameliya Ulya Hidayah", "Intan Aisa", "Varel Geo Syah Putra", 
        "Muhammad Shira Pramudita", "Nabeel Muhammad Diaz"
    ]
    consultant_df = pd.DataFrame({"Consultant Name": CONSULTANTS_LIST, "Clients Handled": 0})

    if COL_KONSULTAN and COL_KONSULTAN in df_incoming.columns:
        actual_counts = df_incoming[COL_KONSULTAN].astype(str).str.strip().value_counts().reset_index()
        actual_counts.columns = ["Consultant Name", "Count"]

        for idx, row in consultant_df.iterrows():
            match = actual_counts[actual_counts['Consultant Name'].str.lower() == row['Consultant Name'].lower()]
            if not match.empty:
                consultant_df.at[idx, 'Clients Handled'] = match['Count'].values[0]

        consultant_df = consultant_df.sort_values(by="Clients Handled", ascending=False).reset_index(drop=True)
        st.dataframe(consultant_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Consultant column not found.")


# -- SECTION 3: PENDING ACTION ITEMS --
st.markdown('<div class="section-header">3. Action Items: Pending Clients</div>', unsafe_allow_html=True)

completed_ids = df_completed[COL_ID].tolist()
pending_df = df_incoming[~df_incoming['Generated_ID'].isin(completed_ids)].copy()

if pending_df.empty:
    st.success("All incoming clients have been completed and recorded.")
else:
    display_cols = ['Generated_ID']
    rename_dict = {'Generated_ID': 'Client ID'}
    
    if COL_NAMA and COL_NAMA in pending_df.columns:
        display_cols.append(COL_NAMA)
        rename_dict[COL_NAMA] = 'Client Name'
    if COL_LAYANAN and COL_LAYANAN in pending_df.columns:
        display_cols.append(COL_LAYANAN)
        rename_dict[COL_LAYANAN] = 'Service Required'
    if COL_KONSULTAN and COL_KONSULTAN in pending_df.columns:
        display_cols.append(COL_KONSULTAN)
        rename_dict[COL_KONSULTAN] = 'Assigned Consultant'
    
    clean_pending_df = pending_df[display_cols].rename(columns=rename_dict)
    st.dataframe(clean_pending_df, use_container_width=True, hide_index=True)
