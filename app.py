import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Dashboard Administrasi GSB",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Google Fonts dipisah dari style block agar tidak mengganggu parser
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans'
    ':wght@400;500;600;700;800&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# PENTING: tidak ada komentar /* */ di dalam <style>
# Tanda * di komentar CSS dibaca Streamlit sebagai sintaks bold markdown
# sehingga seluruh blok <style> bocor sebagai teks biasa
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background: #F2F1ED;
}
#MainMenu, footer, header {
    visibility: hidden;
}
.block-container {
    padding-top: 24px !important;
    padding-bottom: 40px !important;
    max-width: 1260px !important;
}
.gsb-header {
    background: linear-gradient(135deg, #C0392B 0%, #E8500A 50%, #F0892A 100%);
    border-radius: 16px;
    padding: 32px 38px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 28px rgba(192,57,43,0.30);
}
.gsb-header h1 {
    color: white !important;
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    margin: 0 0 3px 0 !important;
    letter-spacing: -0.4px;
}
.gsb-header p {
    color: rgba(255,255,255,0.78) !important;
    font-size: 0.87rem !important;
    margin: 0 !important;
}
.gsb-header-kpi {
    text-align: right;
}
.gsb-header-kpi .kpi-label {
    color: rgba(255,255,255,0.70);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
}
.gsb-header-kpi .kpi-value {
    color: white;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.15;
}
.gsb-section {
    background: white;
    border-radius: 14px;
    padding: 24px 28px 28px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.04);
}
.gsb-section-label {
    font-size: 0.69rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #BDBDBD;
    padding-bottom: 12px;
    margin-bottom: 18px;
    border-bottom: 1px solid #F0EDE8;
}
.metric-card {
    background: #FAFAF8;
    border: 1px solid #EBEBEA;
    border-radius: 12px;
    padding: 18px 20px 14px;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #E8500A, #F0892A);
    border-radius: 12px 12px 0 0;
}
.metric-card.warn::after {
    background: linear-gradient(90deg, #C0392B, #E8500A);
}
.mc-label {
    font-size: 0.70rem;
    font-weight: 700;
    color: #C0BEBB;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 2px;
}
.info-banner {
    background: #FFFBF4;
    border: 1px solid #FFE0B2;
    border-radius: 9px;
    padding: 11px 15px;
    font-size: 0.81rem;
    color: #7A4A10;
    line-height: 1.55;
    margin-bottom: 14px;
}
div[data-testid="stMetricValue"] {
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: #1A1A1A !important;
    letter-spacing: -0.5px !important;
}
div[data-testid="stMetricLabel"] {
    display: none !important;
}
.stDataFrame {
    border-radius: 10px !important;
    border: 1px solid #EBEBEA !important;
}
.stAlert {
    border-radius: 10px !important;
}
.stTextInput input {
    border-radius: 8px !important;
    border: 1.5px solid #E0DDD9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #E8500A !important;
    box-shadow: 0 0 0 3px rgba(232,80,10,0.10) !important;
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
    icon   = "🔒" if failed else "📊"
    title  = "Akses Ditolak" if failed else "Dashboard GSB"
    note   = "Password salah. Silakan coba lagi." if failed else "Masukkan password untuk melanjutkan."

    st.markdown(
        f'<div style="max-width:380px;margin:72px auto;background:white;border-radius:16px;'
        f'padding:36px;box-shadow:0 6px 28px rgba(0,0,0,0.09);text-align:center;">'
        f'<div style="width:52px;height:52px;background:linear-gradient(135deg,#C0392B,#F0892A);'
        f'border-radius:13px;margin:0 auto 16px;font-size:1.4rem;line-height:52px;">{icon}</div>'
        f'<h2 style="margin:0 0 6px;font-weight:800;font-size:1.4rem;color:#1A1A1A;">{title}</h2>'
        f'<p style="margin:0;color:#AAA;font-size:0.86rem;">{note}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Masukkan password…")
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


# HEADER — hanya teks statis di dalam HTML
st.markdown("""
<div class="gsb-header">
    <div>
        <h1>Dashboard Administrasi GSB</h1>
        <p>Department of Data Analytics &nbsp;&middot;&nbsp; KPI &amp; Pelacakan Klien</p>
    </div>
    <div class="gsb-header-kpi">
        <div class="kpi-label">Total KPI</div>
    </div>
</div>
""", unsafe_allow_html=True)

_, col_kpi = st.columns([3, 1])
with col_kpi:
    st.markdown(
        f'<div style="text-align:right;margin-top:-68px;padding-right:4px;'
        f'font-size:1.55rem;font-weight:800;color:white;letter-spacing:-0.5px;">'
        f'Rp {total_kpi:,.0f}</div>',
        unsafe_allow_html=True,
    )


# SECTION 1
st.markdown('<div class="gsb-section"><div class="gsb-section-label">1. Tinjauan Eksekutif</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    st.markdown('<div class="metric-card"><div class="mc-label">Klien Masuk (SPS 1)</div></div>', unsafe_allow_html=True)
    st.metric("a", total_masuk, label_visibility="collapsed")

with c2:
    st.markdown('<div class="metric-card"><div class="mc-label">Klien Selesai (SPS 2)</div></div>', unsafe_allow_html=True)
    st.metric("b", total_selesai, label_visibility="collapsed")

with c3:
    cls = "metric-card warn" if total_pending < 0 else "metric-card"
    st.markdown(f'<div class="{cls}"><div class="mc-label">Belum Terdata</div></div>', unsafe_allow_html=True)
    st.metric("c", total_pending, label_visibility="collapsed")
    if total_pending < 0:
        st.caption("Kemungkinan duplikasi di SPS 2 atau penghapusan di SPS 1")

with c4:
    st.markdown('<div class="metric-card"><div class="mc-label">Pendapatan + Biaya Komitmen</div></div>', unsafe_allow_html=True)
    st.metric("d", f"Rp {total_kpi:,.0f}", label_visibility="collapsed")
    st.caption(
        f"Rp {profit_sps2:,.0f} pendapatan + "
        f"Rp {total_komitmen:,.0f} komitmen "
        f"({total_masuk} x Rp {BIAYA_KOMITMEN:,.0f})"
    )

st.markdown('</div>', unsafe_allow_html=True)


# SECTION 2
st.markdown('<div class="gsb-section"><div class="gsb-section-label">2. Distribusi Layanan Klien (SPS 1)</div>', unsafe_allow_html=True)

if COL_LAYANAN and COL_LAYANAN in df_sps1.columns:
    service_dist = df_sps1[COL_LAYANAN].value_counts().reset_index()
    service_dist.columns = ["Jenis Layanan", "Jumlah Klien"]
    st.dataframe(service_dist, use_container_width=True, hide_index=True)
else:
    st.warning("Kolom 'Layanan yang diinginkan' tidak ditemukan pada SPS 1.")

st.markdown('</div>', unsafe_allow_html=True)


# SECTION 3
st.markdown('<div class="gsb-section"><div class="gsb-section-label">3. Kalkulasi Pajak GSB per Klien</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-banner">
    <strong>Sistem Agregasi Anti-Avoidance:</strong>
    Pajak dihitung dari total akumulasi per ID Klien, bukan per transaksi.
    Klien yang membayar cicil atau menambah analisis tetap dikenakan pajak atas total
    keseluruhan &mdash; mencegah penghindaran bracket pajak.
</div>
""", unsafe_allow_html=True)

display_pajak = pajak_df.copy()
for col in ["Total Nominal", "Pajak GSB", "Net (Nominal - Pajak)"]:
    display_pajak[col] = display_pajak[col].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(display_pajak, use_container_width=True, hide_index=True)

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3, gap="small")

with t1:
    st.markdown('<div style="background:#FFF8F5;border:1px solid #EBEBEA;border-radius:10px;padding:14px 16px;"><div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#C0BEBB;margin-bottom:4px;">Total Nominal Seluruh Klien</div></div>', unsafe_allow_html=True)
    st.metric("t1", f"Rp {akum_nominal:,.0f}", label_visibility="collapsed")

with t2:
    st.markdown('<div style="background:#FFF2F2;border:1px solid #EBEBEA;border-radius:10px;padding:14px 16px;"><div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#C0BEBB;margin-bottom:4px;">Total Pajak GSB (Akumulasi)</div></div>', unsafe_allow_html=True)
    st.metric("t2", f"Rp {akum_pajak:,.0f}", label_visibility="collapsed")

with t3:
    st.markdown('<div style="background:#F4FFF7;border:1px solid #EBEBEA;border-radius:10px;padding:14px 16px;"><div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#C0BEBB;margin-bottom:4px;">Net Diterima (setelah Pajak)</div></div>', unsafe_allow_html=True)
    st.metric("t3", f"Rp {akum_net:,.0f}", label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)
