import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────
# Konfigurasi Halaman
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Administrasi GSB",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS & Tema Visual
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Background Halaman ── */
.stApp {
    background: #F5F5F0;
}

/* ── Header Gradien ── */
.gsb-header {
    background: linear-gradient(135deg, #C0392B 0%, #E8500A 45%, #F0892A 100%);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 32px rgba(200, 70, 20, 0.30);
}
.gsb-header-left h1 {
    color: white !important;
    font-size: 1.9rem !important;
    font-weight: 800 !important;
    margin: 0 0 4px 0 !important;
    letter-spacing: -0.5px;
}
.gsb-header-left p {
    color: rgba(255,255,255,0.80) !important;
    font-size: 0.9rem !important;
    margin: 0 !important;
    font-weight: 500;
}
.gsb-header-right {
    text-align: right;
}
.gsb-header-right .label {
    color: rgba(255,255,255,0.75);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.gsb-header-right .value {
    color: white;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.1;
}

/* ── Kartu Section ── */
.gsb-card {
    background: white;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
}

/* ── Label Section (berformat "1. JUDUL") ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F0EDE8;
}

/* ── Metric Cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 4px;
}
.metric-item {
    background: #FAFAF8;
    border-radius: 12px;
    padding: 20px 22px;
    border: 1px solid #EEECEA;
    position: relative;
    overflow: hidden;
}
.metric-item::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #E8500A, #F0892A);
    border-radius: 12px 12px 0 0;
}
.metric-item .m-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #AAA;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.metric-item .m-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1A1A1A;
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.metric-item .m-value.profit {
    font-size: 1.35rem;
    color: #C0392B;
}

/* ── Tabel / Dataframe ── */
.stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #EEECEA !important;
}
.stDataFrame thead tr th {
    background: #FFF5F0 !important;
    color: #C0392B !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px;
}

/* ── Bar Chart ── */
.stBarChart > div {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Warning & Error ── */
.stAlert {
    border-radius: 10px !important;
    border-left: 4px solid #E8500A !important;
}

/* ── Password Screen ── */
.auth-box {
    max-width: 420px;
    margin: 80px auto;
    background: white;
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.10);
    text-align: center;
}
.auth-box h2 {
    color: #1A1A1A;
    font-weight: 800;
    font-size: 1.5rem;
    margin-bottom: 6px;
}
.auth-box p {
    color: #999;
    font-size: 0.9rem;
    margin-bottom: 24px;
}
.auth-logo {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, #C0392B, #F0892A);
    border-radius: 14px;
    margin: 0 auto 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem;
}

/* ── Input Fields ── */
.stTextInput input {
    border-radius: 8px !important;
    border: 1.5px solid #E8E5E2 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    color: #1A1A1A !important;
    transition: border-color 0.2s;
}
.stTextInput input:focus {
    border-color: #E8500A !important;
    box-shadow: 0 0 0 3px rgba(232,80,10,0.12) !important;
}

/* ── Tombol ── */
.stButton > button {
    background: linear-gradient(135deg, #C0392B, #E8500A) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 10px 28px !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 14px rgba(200,70,20,0.28) !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #EEECEA !important;
    margin: 8px 0 !important;
}

/* ── Sembunyikan elemen bawaan Streamlit yang tidak perlu ── */
#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 28px !important;
    padding-bottom: 40px !important;
    max-width: 1280px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 1. Sistem Proteksi Password
# ─────────────────────────────────────────────
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
        <div class="auth-box">
            <div class="auth-logo">📊</div>
            <h2>Dashboard GSB</h2>
            <p>Masukkan password untuk mengakses dashboard administrasi.</p>
        </div>
        """, unsafe_allow_html=True)
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            st.text_input("Password Dashboard", type="password",
                          on_change=password_entered, key="password",
                          label_visibility="collapsed",
                          placeholder="Masukkan password…")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("""
        <div class="auth-box">
            <div class="auth-logo">🔒</div>
            <h2>Akses Ditolak</h2>
            <p>Password salah. Silakan coba lagi.</p>
        </div>
        """, unsafe_allow_html=True)
        col_center = st.columns([1, 2, 1])[1]
        with col_center:
            st.text_input("Password Dashboard", type="password",
                          on_change=password_entered, key="password",
                          label_visibility="collapsed",
                          placeholder="Masukkan password…")
        return False
    return True

if not check_password():
    st.stop()


# ─────────────────────────────────────────────
# 2. Koneksi ke Google Sheets
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    sheet_sps1 = client.open_by_url(st.secrets["URL_SPS1"]).sheet1
    sheet_sps2 = client.open_by_url(st.secrets["URL_SPS2"]).sheet1

    df_sps1 = pd.DataFrame(sheet_sps1.get_all_records())
    df_sps2 = pd.DataFrame(sheet_sps2.get_all_records())

    df_sps2 = df_sps2.iloc[24:].copy()

    df_sps1.columns = df_sps1.columns.str.strip()
    df_sps2.columns = df_sps2.columns.str.strip()

    NAMA_KOLOM_NOMINAL  = "Nominal yang diberikan"
    NAMA_KOLOM_ID       = "ID Klien (26.XXX)\nisi 3 angka belakang saja"
    NAMA_KOLOM_LAYANAN  = "Layanan yang diinginkan"

    if NAMA_KOLOM_ID not in df_sps2.columns:
        for col in df_sps2.columns:
            if "ID Klien" in str(col):
                NAMA_KOLOM_ID = col
                break

    if NAMA_KOLOM_NOMINAL not in df_sps2.columns:
        for col in df_sps2.columns:
            if "Nominal yang diberikan" in str(col):
                NAMA_KOLOM_NOMINAL = col
                break

    df_sps2[NAMA_KOLOM_ID] = (
        df_sps2[NAMA_KOLOM_ID].astype(str)
        .str.replace(r'\.0$', '', regex=True)
        .str.zfill(3)
    )
    df_sps2[NAMA_KOLOM_NOMINAL] = pd.to_numeric(
        df_sps2[NAMA_KOLOM_NOMINAL], errors='coerce'
    ).fillna(0)

    st.session_state['col_id']      = NAMA_KOLOM_ID
    st.session_state['col_nom']     = NAMA_KOLOM_NOMINAL
    st.session_state['col_layanan'] = NAMA_KOLOM_LAYANAN

    return df_sps1, df_sps2


# ─────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────
try:
    df_sps1, df_sps2 = load_data()
except Exception as e:
    st.error(f"Gagal memuat data dari Google Sheets. Detail Error: {e}")
    st.stop()


# ─────────────────────────────────────────────
# 3. Kalkulasi Metrik
# ─────────────────────────────────────────────
total_incoming  = len(df_sps1)
total_finished  = len(df_sps2)
total_pending   = total_incoming - total_finished
total_profit    = df_sps2[st.session_state['col_nom']].sum()
total_kpi       = total_profit + (total_incoming * 50_000)


# ─────────────────────────────────────────────
# ── HEADER ──
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="gsb-header">
    <div class="gsb-header-left">
        <h1>Dashboard Administrasi GSB</h1>
        <p>Department of Data Analytics &nbsp;·&nbsp; KPI & Pelacakan Klien</p>
    </div>
    <div class="gsb-header-right">
        <div class="label">Total Profit & Admin</div>
        <div class="value">Rp {total_kpi:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 1 · Tinjauan Eksekutif ──
# ─────────────────────────────────────────────
st.markdown('<div class="gsb-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">1. Tinjauan Eksekutif</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-grid">
    <div class="metric-item">
        <div class="m-label">Klien Masuk</div>
        <div class="m-value">{total_incoming}</div>
    </div>
    <div class="metric-item">
        <div class="m-label">Klien Selesai</div>
        <div class="m-value">{total_finished}</div>
    </div>
    <div class="metric-item">
        <div class="m-label">Belum Terdata</div>
        <div class="m-value">{total_pending}</div>
    </div>
    <div class="metric-item">
        <div class="m-label">Profit Bersih (SPS 2)</div>
        <div class="m-value profit">Rp {total_profit:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 2 · Distribusi Layanan ──
# ─────────────────────────────────────────────
st.markdown('<div class="gsb-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">2. Distribusi Layanan Klien</div>', unsafe_allow_html=True)

col_layanan_aktual = st.session_state['col_layanan']
if col_layanan_aktual not in df_sps1.columns:
    for col in df_sps1.columns:
        if "Layanan" in str(col):
            col_layanan_aktual = col
            break

if col_layanan_aktual in df_sps1.columns:
    service_dist = df_sps1[col_layanan_aktual].value_counts().reset_index()
    service_dist.columns = ['Jenis Layanan', 'Jumlah']

    col_tbl, col_chart = st.columns([1, 2], gap="large")
    with col_tbl:
        st.dataframe(service_dist, use_container_width=True, hide_index=True)
    with col_chart:
        st.bar_chart(
            service_dist.set_index('Jenis Layanan'),
            color="#E8500A",
            use_container_width=True,
        )
else:
    st.warning("Kolom Layanan tidak ditemukan pada SPS 1.")

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 3 · Kalkulasi Pajak GSB ──
# ─────────────────────────────────────────────
st.markdown('<div class="gsb-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">3. Kalkulasi Pajak GSB per Klien</div>', unsafe_allow_html=True)

profit_per_client = (
    df_sps2
    .groupby(st.session_state['col_id'])[st.session_state['col_nom']]
    .sum()
    .reset_index()
)

def calculate_tax(amount):
    if amount < 150_000:
        return 0
    elif amount <= 500_000:
        return amount * 0.10
    else:
        return amount * 0.12

profit_per_client['Pajak GSB'] = profit_per_client[st.session_state['col_nom']].apply(calculate_tax)

# Format tampilan (buat salinan agar data asli tidak berubah)
display_df = profit_per_client.copy()
display_df[st.session_state['col_nom']] = display_df[st.session_state['col_nom']].apply(lambda x: f"Rp {x:,.0f}")
display_df['Pajak GSB']                 = display_df['Pajak GSB'].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Anomali Data
# ─────────────────────────────────────────────
if total_pending < 0:
    st.error("⚠️  Peringatan Sistem: Jumlah Klien Selesai melebihi Klien Masuk — terdapat anomali data.")
