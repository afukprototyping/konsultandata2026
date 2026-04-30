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
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }

.stApp { background: #F5F5F0; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 28px !important; padding-bottom: 40px !important; max-width: 1280px !important; }

/* ── Header ── */
.gsb-header {
    background: linear-gradient(135deg, #C0392B 0%, #E8500A 45%, #F0892A 100%);
    border-radius: 16px; padding: 36px 40px; margin-bottom: 20px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 8px 32px rgba(200,70,20,0.28);
}
.gsb-header-left h1 { color:white !important; font-size:1.9rem !important; font-weight:800 !important; margin:0 0 4px 0 !important; letter-spacing:-0.5px; }
.gsb-header-left p  { color:rgba(255,255,255,0.80) !important; font-size:0.88rem !important; margin:0 !important; font-weight:500; }
.gsb-header-right   { text-align:right; }
.gsb-header-right .lbl { color:rgba(255,255,255,0.72); font-size:0.75rem; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; }
.gsb-header-right .val { color:white; font-size:2.1rem; font-weight:800; letter-spacing:-1px; line-height:1.15; }

/* ── Kartu ── */
.gsb-card {
    background:white; border-radius:14px; padding:26px 30px; margin-bottom:18px;
    box-shadow:0 2px 12px rgba(0,0,0,0.055); border:1px solid rgba(0,0,0,0.04);
}
.section-label {
    font-size:0.71rem; font-weight:700; letter-spacing:1.6px; text-transform:uppercase;
    color:#AAA; margin-bottom:18px; padding-bottom:12px; border-bottom:1px solid #F0EDE8;
}

/* ── Metric Grid ── */
.metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
.metric-item {
    background:#FAFAF8; border-radius:12px; padding:18px 20px;
    border:1px solid #EEECEA; position:relative; overflow:hidden;
}
.metric-item::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg,#E8500A,#F0892A); border-radius:12px 12px 0 0;
}
.metric-item.warn::before { background: linear-gradient(90deg,#C0392B,#E8500A); }
.metric-item .m-label { font-size:0.73rem; font-weight:600; color:#BBB; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px; }
.metric-item .m-value { font-size:1.7rem; font-weight:800; color:#1A1A1A; line-height:1.1; letter-spacing:-0.5px; }
.metric-item .m-value.sm { font-size:1.25rem; color:#C0392B; }
.metric-item .m-sub  { font-size:0.72rem; color:#BBB; margin-top:4px; }

/* ── Tax Summary Bar ── */
.tax-summary { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:16px; }
.tax-box { border-radius:10px; padding:16px 18px; border:1px solid #EEECEA; }
.tax-box.total-nom { background:#FFF8F5; }
.tax-box.total-tax { background:#FFF2F2; }
.tax-box.net       { background:#F5FFF7; }
.tax-box .t-label  { font-size:0.70rem; font-weight:700; color:#BBB; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px; }
.tax-box .t-value  { font-size:1.15rem; font-weight:800; letter-spacing:-0.3px; }
.tax-box.total-nom .t-value { color:#E8500A; }
.tax-box.total-tax .t-value { color:#C0392B; }
.tax-box.net       .t-value { color:#1E8B45; }

/* ── Tabel ── */
.stDataFrame { border-radius:10px !important; overflow:hidden !important; border:1px solid #EEECEA !important; }
.stDataFrame thead tr th { background:#FFF5F0 !important; color:#C0392B !important; font-weight:700 !important; font-size:0.81rem !important; }

/* ── Alert ── */
.stAlert { border-radius:10px !important; border-left:4px solid #E8500A !important; }

/* ── Auth ── */
.auth-wrap { max-width:400px; margin:80px auto; background:white; border-radius:16px; padding:38px; box-shadow:0 8px 32px rgba(0,0,0,0.09); text-align:center; }
.auth-icon  { width:54px; height:54px; background:linear-gradient(135deg,#C0392B,#F0892A); border-radius:14px; margin:0 auto 18px; display:flex; align-items:center; justify-content:center; font-size:1.5rem; }
.auth-wrap h2 { color:#1A1A1A; font-weight:800; font-size:1.45rem; margin-bottom:5px; }
.auth-wrap p  { color:#AAA; font-size:0.88rem; margin-bottom:0; }

/* ── Input & Button ── */
.stTextInput input { border-radius:8px !important; border:1.5px solid #E8E5E2 !important; font-family:'Plus Jakarta Sans',sans-serif !important; font-size:0.91rem !important; }
.stTextInput input:focus { border-color:#E8500A !important; box-shadow:0 0 0 3px rgba(232,80,10,0.11) !important; }
.stButton > button {
    background:linear-gradient(135deg,#C0392B,#E8500A) !important; color:white !important;
    border:none !important; border-radius:10px !important; font-weight:700 !important;
    font-family:'Plus Jakarta Sans',sans-serif !important; padding:10px 28px !important;
    box-shadow:0 4px 14px rgba(200,70,20,0.25) !important;
}
hr { border:none !important; border-top:1px solid #EEECEA !important; margin:6px 0 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────
def check_password():
    def _submit():
        if st.session_state["_pw"] == st.secrets["APP_PASSWORD"]:
            st.session_state["auth_ok"] = True
            del st.session_state["_pw"]
        else:
            st.session_state["auth_ok"] = False

    ok = st.session_state.get("auth_ok")
    if ok:
        return True

    icon  = "🔒" if ok is False else "📊"
    title = "Akses Ditolak" if ok is False else "Dashboard GSB"
    note  = "Password salah. Coba lagi." if ok is False else "Masukkan password untuk melanjutkan."

    st.markdown(f"""
    <div class="auth-wrap">
        <div class="auth-icon">{icon}</div>
        <h2>{title}</h2><p>{note}</p>
    </div>""", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Masukkan password…")
    return False

if not check_password():
    st.stop()


# ─────────────────────────────────────────────
# Resolusi Kolom & Load Data
# Nama kolom dikembalikan langsung sebagai nilai
# — bukan disimpan ke session_state dari dalam
# fungsi yang di-cache (anti-pattern rawan bug)
# ─────────────────────────────────────────────
def _find_col(df: pd.DataFrame, exact: str, keyword: str) -> str | None:
    """Exact match dulu, fallback keyword."""
    if exact in df.columns:
        return exact
    for c in df.columns:
        if keyword in str(c):
            return c
    return None


@st.cache_data(ttl=600)
def load_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    df1 = pd.DataFrame(client.open_by_url(st.secrets["URL_SPS1"]).sheet1.get_all_records())
    df2 = pd.DataFrame(client.open_by_url(st.secrets["URL_SPS2"]).sheet1.get_all_records())

    # Potong 24 baris data historis tahun lalu
    df2 = df2.iloc[24:].copy()

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    col_id      = _find_col(df2, "ID Klien (26.XXX)\nisi 3 angka belakang saja", "ID Klien")
    col_nom     = _find_col(df2, "Nominal yang diberikan", "Nominal yang diberikan")
    col_layanan = _find_col(df1, "Layanan yang diinginkan", "Layanan")

    if not col_id or not col_nom:
        raise ValueError(f"Kolom kritis tidak ditemukan. Kolom SPS2 tersedia: {list(df2.columns)}")

    df2[col_id]  = df2[col_id].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors='coerce').fillna(0)

    return df1, df2, col_id, col_nom, col_layanan


try:
    df_sps1, df_sps2, COL_ID, COL_NOM, COL_LAYANAN = load_data()
except Exception as e:
    st.error(f"Gagal memuat data. Detail: {e}")
    st.stop()


# ─────────────────────────────────────────────
# Kalkulasi Terpusat
# ─────────────────────────────────────────────
BIAYA_KOMITMEN = 50_000  # dibayar di awal oleh klien, sebelum analisis dikerjakan

total_masuk   = len(df_sps1)
total_selesai = len(df_sps2)
total_pending = total_masuk - total_selesai
profit_sps2   = df_sps2[COL_NOM].sum()
total_komitmen = total_masuk * BIAYA_KOMITMEN
total_kpi      = profit_sps2 + total_komitmen


def hitung_pajak(nominal: float) -> float:
    if nominal < 150_000:   return 0.0
    if nominal <= 500_000:  return nominal * 0.10
    return nominal * 0.12


pajak_df = (
    df_sps2.groupby(COL_ID)[COL_NOM]
    .sum()
    .reset_index()
    .rename(columns={COL_ID: "ID Klien", COL_NOM: "Total Nominal"})
)
pajak_df["Pajak GSB"]             = pajak_df["Total Nominal"].apply(hitung_pajak)
pajak_df["Net (Nominal − Pajak)"] = pajak_df["Total Nominal"] - pajak_df["Pajak GSB"]

# Akumulasi
akum_nominal = pajak_df["Total Nominal"].sum()
akum_pajak   = pajak_df["Pajak GSB"].sum()
akum_net     = pajak_df["Net (Nominal − Pajak)"].sum()


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
        <div class="lbl">Total KPI (Profit + Admin)</div>
        <div class="val">Rp {total_kpi:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 1 · Tinjauan Eksekutif ──
# ─────────────────────────────────────────────
pending_class = "warn" if total_pending < 0 else ""
anomali_sub   = (
    '<div class="m-sub">⚠️ Kemungkinan duplikasi di SPS 2 atau penghapusan di SPS 1</div>'
    if total_pending < 0 else ""
)

st.markdown(f"""
<div class="gsb-card">
    <div class="section-label">1. Tinjauan Eksekutif</div>
    <div class="metric-grid">
        <div class="metric-item">
            <div class="m-label">Klien Masuk (SPS 1)</div>
            <div class="m-value">{total_masuk}</div>
        </div>
        <div class="metric-item">
            <div class="m-label">Klien Selesai (SPS 2)</div>
            <div class="m-value">{total_selesai}</div>
        </div>
        <div class="metric-item {pending_class}">
            <div class="m-label">Belum Terdata</div>
            <div class="m-value">{total_pending}</div>
            {anomali_sub}
        </div>
        <div class="metric-item">
            <div class="m-label">Total KPI (Pendapatan + Komitmen)</div>
            <div class="m-value sm">Rp {total_kpi:,.0f}
                <br><span style="font-size:.70rem;color:#BBB;font-weight:500">
                    Rp {profit_sps2:,.0f} pendapatan
                    &nbsp;+&nbsp;
                    Rp {total_komitmen:,.0f} komitmen ({total_masuk}×Rp {BIAYA_KOMITMEN:,.0f})
                </span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 2 · Distribusi Layanan ──
# ─────────────────────────────────────────────
st.markdown('<div class="gsb-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">2. Distribusi Layanan Klien (SPS 1)</div>', unsafe_allow_html=True)

if COL_LAYANAN and COL_LAYANAN in df_sps1.columns:
    service_dist = (
        df_sps1[COL_LAYANAN]
        .value_counts()
        .reset_index()
        .rename(columns={COL_LAYANAN: "Jenis Layanan", "count": "Jumlah Klien"})
    )
    st.dataframe(service_dist, use_container_width=True, hide_index=True)
else:
    st.warning("Kolom 'Layanan yang diinginkan' tidak ditemukan pada SPS 1.")

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ── SECTION 3 · Pajak GSB per Klien ──
# ─────────────────────────────────────────────
st.markdown('<div class="gsb-card">', unsafe_allow_html=True)
st.markdown("""
<div class="section-label">3. Kalkulasi Pajak GSB per Klien</div>
<div style="background:#FFFBF5;border:1px solid #FFE0C0;border-radius:9px;padding:11px 16px;margin-bottom:16px;font-size:0.82rem;color:#7A4A10;line-height:1.55;">
    <strong>Sistem Agregasi Anti-Avoidance:</strong>
    Pajak dihitung dari <em>total akumulasi per ID Klien</em>, bukan per transaksi.
    Klien yang membayar secara cicil atau menambah analisis (multi-baris) tetap dihitung
    pajaknya atas total keseluruhan — mencegah penghindaran bracket pajak.
</div>
""", unsafe_allow_html=True)

# Tabel rincian — format tampilan saja, data numerik di pajak_df tetap utuh
display_pajak = pajak_df.copy()
for col in ["Total Nominal", "Pajak GSB", "Net (Nominal − Pajak)"]:
    display_pajak[col] = display_pajak[col].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(display_pajak, use_container_width=True, hide_index=True)

# ── Akumulasi Total ──
st.markdown(f"""
<div class="tax-summary">
    <div class="tax-box total-nom">
        <div class="t-label">Total Nominal Seluruh Klien</div>
        <div class="t-value">Rp {akum_nominal:,.0f}</div>
    </div>
    <div class="tax-box total-tax">
        <div class="t-label">Total Pajak GSB (Akumulasi)</div>
        <div class="t-value">Rp {akum_pajak:,.0f}</div>
    </div>
    <div class="tax-box net">
        <div class="t-label">Net Diterima (setelah Pajak)</div>
        <div class="t-value">Rp {akum_net:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
