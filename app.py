import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Dashboard Administrasi GSB",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Injeksi CSS Modern & Minimalis
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background-color: #F8FAFC;
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
    background-color: #0F172A;
    border-radius: 12px;
    padding: 32px 40px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.header-title {
    color: #FFFFFF;
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
    color: #334155;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #E2E8F0;
}

/* Metric Cards HTML */
.custom-metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    height: 100%;
}
.cmc-label {
    color: #64748B;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.cmc-value {
    color: #0F172A;
    font-size: 1.875rem;
    font-weight: 800;
    line-height: 1.2;
}
.cmc-caption {
    color: #94A3B8;
    font-size: 0.75rem;
    margin-top: 8px;
    font-weight: 500;
}
.cmc-value.warning {
    color: #EF4444;
}

/* Alert/Banner Styling */
.info-banner {
    background-color: #EFF6FF;
    border-left: 4px solid #3B82F6;
    padding: 16px;
    border-radius: 6px;
    color: #1E3A8A;
    font-size: 0.875rem;
    margin-bottom: 20px;
}

/* Streamlit Overrides */
.stDataFrame {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
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
    title  = "Akses Ditolak" if failed else "Autentikasi GSB"
    note   = "Kredensial tidak valid. Silakan coba lagi." if failed else "Masukkan kata sandi untuk mengakses dasbor."

    st.markdown(
        f'<div style="max-width:400px;margin:80px auto;background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;'
        f'padding:40px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);text-align:center;">'
        f'<h2 style="margin:0 0 8px;font-weight:800;font-size:1.5rem;color:#0F172A;">{title}</h2>'
        f'<p style="margin:0 0 24px;color:#64748B;font-size:0.875rem;">{note}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        # Form input diletakkan sedikit di atas menggunakan margin negatif ringan khusus untuk input
        st.markdown('<div style="margin-top:-75px;"></div>', unsafe_allow_html=True)
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Kata Sandi...")
    return False

if not check_password():
    st.stop()


def _find_col(df: pd.DataFrame, exact: str, keyword: str) -> str | None:
    if exact in df.columns:
        return exact
    for c in df.columns:
        if keyword in str(c):
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
    col_nom     = _find_col(df2, "Nominal yang diberikan", "Nominal yang diberikan")
    col_layanan = _find_col(df1, "Layanan yang diinginkan", "Layanan")

    if not col_id or not col_nom:
        raise ValueError(f"Kolom kritis tidak ditemukan. Kolom SPS2: {list(df2.columns)}")

    df2[col_id]  = df2[col_id].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    return df1, df2, col_id, col_nom, col_layanan


try:
    df_sps1, df_sps2, COL_ID, COL_NOM, COL_LAYANAN = load_data()
except Exception as e:
    st.error(f"Gagal memuat data. Detail: {e}")
    st.stop()


BIAYA_KOMITMEN = 50_000

total_masuk    = len(df_sps1)
total_selesai  = len(df_sps2)
total_pending  = total_masuk - total_selesai
profit_sps2    = df_sps2[COL_NOM].sum()
total_komitmen = total_masuk * BIAYA_KOMITMEN
total_kpi      = profit_sps2 + total_komitmen


def hitung_pajak(nominal: float) -> float:
    if nominal < 150_000:  return 0.0
    if nominal <= 500_000: return nominal * 0.10
    return nominal * 0.12


pajak_df = (
    df_sps2.groupby(COL_ID)[COL_NOM]
    .sum().reset_index()
    .rename(columns={COL_ID: "ID Klien", COL_NOM: "Total Nominal"})
)
pajak_df["Pajak GSB"]             = pajak_df["Total Nominal"].apply(hitung_pajak)
pajak_df["Net (Nominal - Pajak)"] = pajak_df["Total Nominal"] - pajak_df["Pajak GSB"]

akum_nominal = pajak_df["Total Nominal"].sum()
akum_pajak   = pajak_df["Pajak GSB"].sum()
akum_net     = pajak_df["Net (Nominal - Pajak)"].sum()


# HEADER UTAMA
st.markdown(f"""
<div class="header-container">
    <div>
        <h1 class="header-title">Dasbor Administrasi GSB</h1>
        <p class="header-subtitle">Departemen Data Analytics &middot; Pelacakan KPI & Klien</p>
    </div>
    <div>
        <div class="header-kpi-label">Estimasi Valuasi KPI</div>
        <div class="header-kpi-value">Rp {total_kpi:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# SECTION 1: Tinjauan Eksekutif
st.markdown('<div class="section-title">1. Tinjauan Eksekutif</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Klien Masuk (SPS 1)</div>
        <div class="cmc-value">{total_masuk}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Klien Selesai (SPS 2)</div>
        <div class="cmc-value">{total_selesai}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    warning_class = "warning" if total_pending < 0 else ""
    caption_html = '<div class="cmc-caption" style="color:#EF4444;">Anomali Data Terdeteksi</div>' if total_pending < 0 else ''
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Belum Terdata</div>
        <div class="cmc-value {warning_class}">{total_pending}</div>
        {caption_html}
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="custom-metric-card">
        <div class="cmc-label">Pendapatan Total</div>
        <div class="cmc-value" style="font-size:1.5rem;">Rp {profit_sps2:,.0f}</div>
        <div class="cmc-caption">+ Rp {total_komitmen:,.0f} (Biaya Komitmen)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# SECTION 2: Distribusi Layanan
st.markdown('<div class="section-title">2. Distribusi Layanan Klien (SPS 1)</div>', unsafe_allow_html=True)

if COL_LAYANAN and COL_LAYANAN in df_sps1.columns:
    service_dist = df_sps1[COL_LAYANAN].value_counts().reset_index()
    service_dist.columns = ["Jenis Layanan", "Jumlah Klien"]
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.dataframe(service_dist, use_container_width=True, hide_index=True)
    with col_b:
        st.bar_chart(service_dist.set_index("Jenis Layanan"), color="#3B82F6")
else:
    st.warning("Kolom Layanan tidak ditemukan pada basis data SPS 1.")

st.markdown("<br>", unsafe_allow_html=True)


# SECTION 3: Kalkulasi Pajak
st.markdown('<div class="section-title">3. Rekapitulasi Kewajiban Pajak GSB</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-banner">
    <strong>Protokol Agregasi Aktif:</strong> Pajak dihitung berdasarkan akumulasi identitas klien, bukan entri transaksi individual. Hal ini mencegah manipulasi margin pajak melalui pemecahan tagihan (split invoicing).
</div>
""", unsafe_allow_html=True)

display_pajak = pajak_df.copy()
for col in ["Total Nominal", "Pajak GSB", "Net (Nominal - Pajak)"]:
    display_pajak[col] = display_pajak[col].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(display_pajak, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3)

with t1:
    st.markdown(f"""
    <div class="custom-metric-card" style="background:#F8FAFC;">
        <div class="cmc-label">Akumulasi Bruto</div>
        <div class="cmc-value" style="font-size:1.5rem;">Rp {akum_nominal:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown(f"""
    <div class="custom-metric-card" style="background:#FEF2F2; border-color:#FCA5A5;">
        <div class="cmc-label" style="color:#DC2626;">Kewajiban Pajak</div>
        <div class="cmc-value" style="font-size:1.5rem; color:#991B1B;">Rp {akum_pajak:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown(f"""
    <div class="custom-metric-card" style="background:#F0FDF4; border-color:#86EFAC;">
        <div class="cmc-label" style="color:#16A34A;">Penerimaan Bersih</div>
        <div class="cmc-value" style="font-size:1.5rem; color:#166534;">Rp {akum_net:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)
