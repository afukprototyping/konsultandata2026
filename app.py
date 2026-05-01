import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
import base64
import os

st.set_page_config(
    page_title="GSB Workspace",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 1. CSS INJECTION (CLEAN, MODERN, 1-PAGE)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Background Super Bersih */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #F8FAFC !important;
    background-image: none !important; 
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1280px !important; /* Diperlebar untuk layout 1 halaman */
}

/* Header Utama (Sangat Minimalis & Elegan) */
.header-container {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}
.header-title {
    color: #0F172A !important;
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.02em !important;
}
.header-subtitle {
    color: #64748B !important;
    font-size: 0.9rem !important;
    margin: 0 !important;
    font-weight: 500 !important;
}

/* Kotak Metrik Level Tinggi (Atas) */
.kpi-card {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    text-align: left !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    height: 100%;
}
.kpi-label {
    color: #64748B !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 8px !important;
}
.kpi-value {
    color: #0F172A !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    line-height: 1 !important;
    letter-spacing: -0.03em !important;
}
.kpi-subtext {
    color: #94A3B8 !important;
    font-size: 0.75rem !important;
    margin-top: 8px !important;
    font-weight: 500 !important;
}

/* Pemisah Antar Sesi / Judul Sesi */
.section-divider {
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    margin-top: 40px !important;
    margin-bottom: 20px !important;
    padding-bottom: 8px !important;
    border-bottom: 2px solid #E2E8F0 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Modifikasi Warna untuk Status/Metrik */
.text-danger { color: #DC2626 !important; }
.text-success { color: #059669 !important; }
.text-primary { color: #2563EB !important; }

/* Streamlit DataFrame Override */
.stDataFrame {
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
}

/* Form Login */
.login-box {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px;
    padding: 48px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    text-align: center;
}
.stTextInput input {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
    padding: 16px !important;
    font-size: 1rem !important;
    text-align: center !important;
}
.stTextInput input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
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
    img_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 120px; width: auto; object-fit: contain; margin-bottom: 24px;">' if logo_b64 else ''

    _, mid, _ = st.columns([1, 1.2, 1])
    
    with mid:
        st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-box">
            {img_html}
            <h2 style="margin:0 0 8px; font-weight:800; font-size:2rem; color:#0F172A;">GSB Workspace</h2>
            <p style="margin:0 0 32px; color:#64748B; font-size:1rem;">Otentikasi Diperlukan</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top:-90px; padding: 0 48px;">', unsafe_allow_html=True)
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Masukkan Password...")
        st.markdown('</div>', unsafe_allow_html=True)
        
    return False

if not check_password():
    st.stop()

# ==========================================
# 3. DATA PIPELINE
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
        raise ValueError("Kolom kritis tidak ditemukan di Sheets SPS 2.")

    df2[col_id]  = df2[col_id].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    col_id_sps1 = _find_col(df1, "ID Klien", "ID Klien")
    if not col_id_sps1:
        raise ValueError("Kolom 'ID Klien' tidak ditemukan di SPS 1.")
    
    df1['Generated_ID'] = df1[col_id_sps1].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)

    return df1, df2, col_id, col_nom, col_layanan, col_nama, col_konsul

try:
    df_incoming, df_completed, COL_ID, COL_NOM, COL_LAYANAN, COL_NAMA, COL_KONSULTAN = load_data()
except Exception as e:
    st.error(f"Gagal memuat data. Error: {e}")
    st.stop()

# ==========================================
# 4. DATA CALCULATION
# ==========================================
COMMITMENT_FEE = 50_000

# Metrik Eksekutif
total_incoming = len(df_incoming)
total_completed = len(df_completed)
total_pending  = total_incoming - total_completed
profit_completed = df_completed[COL_NOM].sum()
total_commitment = total_incoming * COMMITMENT_FEE
total_kpi      = profit_completed + total_commitment

# Kalkulasi Pajak
def calculate_tax(nominal: float) -> float:
    if nominal < 150_000:  return 0.0
    if nominal <= 500_000: return nominal * 0.10
    return nominal * 0.12

pajak_df = (
    df_completed.groupby(COL_ID)[COL_NOM]
    .sum().reset_index()
    .rename(columns={COL_ID: "ID Klien", COL_NOM: "Akumulasi Bruto"})
)
pajak_df["Pajak GSB"] = pajak_df["Akumulasi Bruto"].apply(calculate_tax)
pajak_df["Net Diterima"] = pajak_df["Akumulasi Bruto"] - pajak_df["Pajak GSB"]

accum_gross = pajak_df["Akumulasi Bruto"].sum()
accum_tax   = pajak_df["Pajak GSB"].sum()
accum_net   = pajak_df["Net Diterima"].sum()


# ==========================================
# 5. DASHBOARD UI (Satu Halaman Penuh)
# ==========================================

# -- HEADER --
logo_b64_header = get_base64_image("logo gsb.png")
img_header = f'<img src="data:image/png;base64,{logo_b64_header}" style="height: 48px; margin-right: 16px;">' if logo_b64_header else ''

st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center;">
        {img_header}
        <div>
            <h1 class="header-title">GSB Operations Board</h1>
            <p class="header-subtitle">Data Analytics Department</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -- BARIS 1: METRIK KEUANGAN & PAJAK --
st.markdown('<div class="section-divider">1. Finansial & Perpajakan</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Valuasi KPI (Bruto + Komitmen)</div>
        <div class="kpi-value text-primary">Rp {total_kpi:,.0f}</div>
        <div class="kpi-subtext">Dari Rp {profit_completed:,.0f} + Rp {total_commitment:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with f2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label text-danger">Kewajiban Pajak GSB</div>
        <div class="kpi-value text-danger">Rp {accum_tax:,.0f}</div>
        <div class="kpi-subtext">Dari Total Bruto Rp {accum_gross:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
with f3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label text-success">Estimasi Netto Masuk</div>
        <div class="kpi-value text-success">Rp {accum_net:,.0f}</div>
        <div class="kpi-subtext">Setelah dipotong pajak</div>
    </div>
    """, unsafe_allow_html=True)


# -- BARIS 2: STATUS KLIEN & BEBAN KERJA (KIRI & KANAN) --
st.markdown('<div class="section-divider">2. Status Klien & Operasional</div>', unsafe_allow_html=True)

col_kiri, col_kanan = st.columns([1.2, 2], gap="large")

with col_kiri:
    # Status Klien
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(f"""
        <div class="kpi-card" style="padding: 16px !important; margin-bottom: 16px;">
            <div class="kpi-label">Klien Masuk</div>
            <div class="kpi-value" style="font-size: 1.8rem !important;">{total_incoming}</div>
        </div>
        """, unsafe_allow_html=True)
        
        warn_color = "text-danger" if total_pending > 0 else "text-success"
        st.markdown(f"""
        <div class="kpi-card" style="padding: 16px !important;">
            <div class="kpi-label {warn_color}">Belum Selesai</div>
            <div class="kpi-value {warn_color}" style="font-size: 1.8rem !important;">{total_pending}</div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
        <div class="kpi-card" style="padding: 16px !important; height: 100%;">
            <div class="kpi-label text-success">Selesai (SPS 2)</div>
            <div class="kpi-value text-success" style="font-size: 3.5rem !important; margin-top: 10px;">{total_completed}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Distribusi Layanan (Pie Chart)
    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#0F172A; margin-bottom:12px;">DISTRIBUSI LAYANAN</div>', unsafe_allow_html=True)
    if COL_LAYANAN and COL_LAYANAN in df_incoming.columns:
        service_dist = df_incoming[COL_LAYANAN].value_counts().reset_index()
        service_dist.columns = ["Jenis Layanan", "Jumlah"]
        
        fig1 = px.pie(service_dist, values='Jumlah', names='Jenis Layanan', hole=0.5, 
                      color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#EC4899'])
        fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                           font=dict(family='Plus Jakarta Sans', color='#0F172A', size=11),
                           margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
        st.plotly_chart(fig1, use_container_width=True, theme=None)
    else:
        st.warning("Data layanan tidak ditemukan.")

with col_kanan:
    # Tabel Beban Kerja Konsultan (Bar Chart)
    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#0F172A; margin-bottom:12px;">BEBAN KERJA KONSULTAN</div>', unsafe_allow_html=True)
    
    CONSULTANTS_LIST = [
        "Helmi Falah", "Nyayu Azzahra Nabila", "Cut Ashifa Sawallida", "Retno Sari", 
        "Rizky Arif Wicaksono", "Pascal Arya Nugroho", "Muhammad Khayruhanif", 
        "Qanita Basimah Kurnia", "Afiq Dzakwan Anasti", "Azka Raditya Hafidz", 
        "Cameliya Ulya Hidayah", "Intan Aisa", "Varel Geo Syah Putra", 
        "Muhammad Shira Pramudita", "Nabeel Muhammad Diaz"
    ]
    consultant_df = pd.DataFrame({"Konsultan": CONSULTANTS_LIST, "Klien": 0})

    if COL_KONSULTAN and COL_KONSULTAN in df_incoming.columns:
        actual_counts = df_incoming[COL_KONSULTAN].astype(str).str.strip().value_counts().reset_index()
        actual_counts.columns = ["Konsultan", "Count"]

        for idx, row in consultant_df.iterrows():
            match = actual_counts[actual_counts['Konsultan'].str.lower() == row['Konsultan'].lower()]
            if not match.empty:
                consultant_df.at[idx, 'Klien'] = match['Count'].values[0]

        consultant_df = consultant_df.sort_values(by="Klien", ascending=False).reset_index(drop=True)
        
        fig2 = px.bar(consultant_df, x='Klien', y='Konsultan', orientation='h')
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Plus Jakarta Sans', color='#0F172A', size=11),
            yaxis={'categoryorder':'total ascending'},
            margin=dict(t=0, b=0, l=0, r=0), height=350,
            xaxis_title="", yaxis_title=""
        )
        fig2.update_traces(marker_color='#3B82F6')
        st.plotly_chart(fig2, use_container_width=True, theme=None)
    else:
        st.warning("Kolom konsultan tidak ditemukan.")


# -- BARIS 3: TABEL DAFTAR KLIEN PENDING --
st.markdown('<div class="section-divider">3. Action Item: Klien Belum Selesai</div>', unsafe_allow_html=True)

completed_ids = df_completed[COL_ID].tolist()
pending_df = df_incoming[~df_incoming['Generated_ID'].isin(completed_ids)].copy()

if pending_df.empty:
    st.success("✨ Luar biasa! Semua klien masuk telah diselesaikan dan terdata di SPS 2.")
else:
    display_cols = ['Generated_ID']
    rename_dict = {'Generated_ID': 'ID Klien'}
    
    if COL_NAMA and COL_NAMA in pending_df.columns:
        display_cols.append(COL_NAMA)
        rename_dict[COL_NAMA] = 'Nama Klien'
    if COL_LAYANAN and COL_LAYANAN in pending_df.columns:
        display_cols.append(COL_LAYANAN)
        rename_dict[COL_LAYANAN] = 'Layanan'
    if COL_KONSULTAN and COL_KONSULTAN in pending_df.columns:
        display_cols.append(COL_KONSULTAN)
        rename_dict[COL_KONSULTAN] = 'Konsultan Bertugas'
    
    clean_pending_df = pending_df[display_cols].rename(columns=rename_dict)
    st.dataframe(clean_pending_df, use_container_width=True, hide_index=True)
