import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import base64
import os

st.set_page_config(
    page_title="GSB Consulting Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 1. CSS INJECTION (ULTRA-COMPACT, GSB BRANDING)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #F8FAFC !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* Mengompres ruang kosong layar secara ekstrem */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 1360px !important;
}

/* Header Kompak */
.header-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 16px 24px;
    margin-bottom: 16px;
    display: flex;
    justify-content: flex-start; /* Justify Kiri */
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}
.header-title {
    color: #1E3A8A !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    margin: 0 0 2px 0 !important;
    letter-spacing: -0.02em !important;
}
.header-subtitle {
    color: #64748B !important;
    font-size: 0.85rem !important;
    margin: 0 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
}

/* Pemisah Vertikal untuk Total Value */
.header-divider {
    height: 48px;
    width: 2px;
    background-color: #E2E8F0;
    margin: 0 32px;
}

/* Kotak Metrik Super Padat */
.metric-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid #1E3A8A; /* Default Navy */
    border-radius: 6px;
    padding: 16px;
    height: 100%;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}
.metric-card.accent-red { border-top-color: #DC2626; }
.metric-card.accent-green { border-top-color: #10B981; }
.metric-card.accent-orange { border-top-color: #E8500A; }

.metric-label {
    color: #64748B;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.metric-value {
    color: #0F172A;
    font-size: 1.6rem;
    font-weight: 800;
    line-height: 1.1;
}

/* Section Mini Header */
.mini-header {
    font-size: 0.85rem;
    font-weight: 800;
    color: #1E3A8A;
    margin-bottom: 8px;
    text-transform: uppercase;
}

/* Streamlit DataFrame Override untuk ruang sempit */
.stDataFrame {
    border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
}

/* Login Box (Dibiarkan Proporsional) */
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
    img_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 90px; width: auto; margin-bottom: 24px;">' if logo_b64 else ''

    _, mid, _ = st.columns([1, 1.2, 1])
    
    with mid:
        st.markdown("<div style='margin-top: 15vh;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-box">
            {img_html}
            <h2 style="margin:0 0 8px; font-weight:800; font-size:1.6rem; color:#1E3A8A;">GSB Data Consulting</h2>
            <p style="margin:0 0 24px; color:#64748B; font-size:0.9rem;">Authentication Required</p>
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
# 3. DATA EXTRACTION
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

    if not col_id or not col_nom: raise ValueError("Critical columns missing in SPS 2.")

    df2[col_id]  = df2[col_id].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    col_id_sps1 = _find_col(df1, "ID Klien", "ID Klien")
    if not col_id_sps1: raise ValueError("Critical column 'ID Klien' missing in SPS 1.")
    
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

total_incoming   = len(df_incoming)
total_completed  = len(df_completed)
total_pending    = total_incoming - total_completed
profit_completed = df_completed[COL_NOM].sum()
total_commitment = total_incoming * COMMITMENT_FEE
total_valuation  = profit_completed + total_commitment

def calculate_tax(nominal: float) -> float:
    if nominal < 150_000:  return 0.0
    if nominal <= 500_000: return nominal * 0.10
    return nominal * 0.12

pajak_df = (
    df_completed.groupby(COL_ID)[COL_NOM].sum().reset_index()
    .rename(columns={COL_ID: "Client ID", COL_NOM: "Gross Accumulation"})
)
pajak_df["Tax Liability"] = pajak_df["Gross Accumulation"].apply(calculate_tax)
pajak_df["Net Revenue"]   = pajak_df["Gross Accumulation"] - pajak_df["Tax Liability"]

accum_gross = pajak_df["Gross Accumulation"].sum()
accum_tax   = pajak_df["Tax Liability"].sum()
accum_net   = pajak_df["Net Revenue"].sum()

# ==========================================
# 5. SINGLE-VIEW ULTRA COMPACT LAYOUT
# ==========================================

# -- Header Terpusat Kiri --
logo_b64_header = get_base64_image("logo gsb.png")
img_header = f'<img src="data:image/png;base64,{logo_b64_header}" style="height: 44px; margin-right: 16px;">' if logo_b64_header else ''

st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center;">
        {img_header}
        <div>
            <h1 class="header-title">GSB Data Consulting Services</h1>
            <p class="header-subtitle">Department of Data Analytics</p>
        </div>
    </div>
    <div class="header-divider"></div>
    <div>
        <div class="metric-label">Total Estimated Value</div>
        <div class="metric-value" style="color: #E8500A; font-size: 1.85rem;">Rp {total_valuation:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -- Metrik 1 Baris Penuh --
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Gross Tax Accum.</div><div class="metric-value">Rp {accum_gross:,.0f}</div></div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-card accent-green"><div class="metric-label" style="color:#10B981;">Total Net Revenue</div><div class="metric-value" style="color:#10B981;">Rp {accum_net:,.0f}</div></div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="metric-card accent-red"><div class="metric-label" style="color:#DC2626;">Total Tax Liability</div><div class="metric-value" style="color:#DC2626;">Rp {accum_tax:,.0f}</div></div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""<div class="metric-card accent-green"><div class="metric-label" style="color:#10B981;">Completed Clients</div><div class="metric-value" style="color:#10B981;">{total_completed} <span style="font-size:0.8rem; color:#64748B;">/ {total_incoming}</span></div></div>""", unsafe_allow_html=True)
with m5:
    alert_color = "#DC2626" if total_pending > 0 else "#10B981"
    st.markdown(f"""<div class="metric-card {'accent-red' if total_pending > 0 else 'accent-green'}"><div class="metric-label" style="color:{alert_color};">Pending Clients</div><div class="metric-value" style="color:{alert_color};">{total_pending}</div></div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

# -- Tabel 3 Kolom Berdampingan --
col_left, col_mid, col_right = st.columns([1, 1, 1.5], gap="medium")

with col_left:
    st.markdown('<div class="mini-header">Service Distribution</div>', unsafe_allow_html=True)
    if COL_LAYANAN and COL_LAYANAN in df_incoming.columns:
        service_dist = df_incoming[COL_LAYANAN].value_counts().reset_index()
        service_dist.columns = ["Service Type", "Qty"]
        st.dataframe(service_dist, use_container_width=True, hide_index=True)
    else:
        st.warning("N/A")

with col_mid:
    st.markdown('<div class="mini-header">Consultant Workload</div>', unsafe_allow_html=True)
    CONSULTANTS_LIST = [
        "Helmi Falah", "Nyayu Azzahra Nabila", "Cut Ashifa Sawallida", "Retno Sari", 
        "Rizky Arif Wicaksono", "Pascal Arya Nugroho", "Muhammad Khayruhanif", 
        "Qanita Basimah Kurnia", "Afiq Dzakwan Anasti", "Azka Raditya Hafidz", 
        "Cameliya Ulya Hidayah", "Intan Aisa", "Varel Geo Syah Putra", 
        "Muhammad Shira Pramudita", "Nabeel Muhammad Diaz"
    ]
    consultant_df = pd.DataFrame({"Consultant": CONSULTANTS_LIST, "Handled": 0})
    if COL_KONSULTAN and COL_KONSULTAN in df_incoming.columns:
        actual_counts = df_incoming[COL_KONSULTAN].astype(str).str.strip().value_counts().reset_index()
        actual_counts.columns = ["Consultant", "Count"]
        for idx, row in consultant_df.iterrows():
            match = actual_counts[actual_counts['Consultant'].str.lower() == row['Consultant'].lower()]
            if not match.empty: consultant_df.at[idx, 'Handled'] = match['Count'].values[0]
        consultant_df = consultant_df.sort_values(by="Handled", ascending=False).reset_index(drop=True)
        st.dataframe(consultant_df, use_container_width=True, hide_index=True)
    else:
        st.warning("N/A")

with col_right:
    st.markdown('<div class="mini-header">Pending Clients Roster</div>', unsafe_allow_html=True)
    completed_ids = df_completed[COL_ID].tolist()
    pending_df = df_incoming[~df_incoming['Generated_ID'].isin(completed_ids)].copy()
    if pending_df.empty:
        st.success("Operational clear. All incoming clients have been processed.")
    else:
        display_cols = ['Generated_ID']
        rename_dict = {'Generated_ID': 'ID'}
        if COL_NAMA and COL_NAMA in pending_df.columns:
            display_cols.append(COL_NAMA)
            rename_dict[COL_NAMA] = 'Client'
        if COL_LAYANAN and COL_LAYANAN in pending_df.columns:
            display_cols.append(COL_LAYANAN)
            rename_dict[COL_LAYANAN] = 'Service'
        if COL_KONSULTAN and COL_KONSULTAN in pending_df.columns:
            display_cols.append(COL_KONSULTAN)
            rename_dict[COL_KONSULTAN] = 'Consultant'
        
        clean_pending_df = pending_df[display_cols].rename(columns=rename_dict)
        st.dataframe(clean_pending_df, use_container_width=True, hide_index=True)
