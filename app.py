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

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

is_dark = st.session_state.dark_mode

if is_dark:
    APP_BG  = "#0F172A"
    CARD_BG = "rgba(30,41,59,0.95)"
    CARD_BD = "rgba(51,65,85,0.8)"
    T1 = "#F1F5F9"; T2 = "#94A3B8"
    TH = "#1E293B"; TB = "#334155"; PB = "#334155"
    BD_BG = "#1E293B"; BD_C = "#94A3B8"
    RL = "transparent"
else:
    APP_BG  = "#F8FAFC"
    CARD_BG = "rgba(255,255,255,0.92)"
    CARD_BD = "rgba(226,232,240,0.9)"
    T1 = "#0F172A"; T2 = "#64748B"
    TH = "#F1F5F9"; TB = "#E2E8F0"; PB = "#E2E8F0"
    BD_BG = "#F1F5F9"; BD_C = "#475569"
    RL = "#E2E8F0"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

*:not([class*="material-symbols"]):not([data-testid="stIconMaterial"]) {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}}
[data-testid="stIconMaterial"],
span[class*="material-symbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
}}

.stApp {{
    background-color: {APP_BG} !important;
    background-image:
        radial-gradient(circle at 10% 10%, rgba(232,80,10,0.04) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(30,58,138,0.04) 0%, transparent 40%) !important;
    background-attachment: fixed !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {{ background: transparent !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding-top: 0.6rem !important;
    padding-bottom: 0.6rem !important;
    max-width: 1400px !important;
}}

[data-testid="InputInstructions"] {{ display: none !important; }}

button[data-testid="stTextInputPasswordToggle"] {{
    width: 36px !important;
    min-width: 36px !important;
    max-width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
button[data-testid="stTextInputPasswordToggle"] svg {{
    width: 18px !important;
    height: 18px !important;
}}
button[data-testid="stTextInputPasswordToggle"] span {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
    font-size: 18px !important;
    color: {T2} !important;
}}

.login-box {{
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(226,232,240,0.9);
    border-top: 6px solid #E8500A;
    border-radius: 16px;
    padding: 40px 40px 32px;
    box-shadow: 0 20px 40px -10px rgba(232,80,10,0.12);
    text-align: center;
}}
.stTextInput input {{
    background-color: rgba(248,250,252,0.9) !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    padding: 14px !important;
    text-align: center !important;
    font-size: 1rem !important;
}}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, #F97316, #EA580C) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 14px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    width: 100% !important;
    cursor: pointer !important;
    letter-spacing: 0.02em !important;
}}

.st-key-mode_light button, .st-key-mode_dark button {{
    padding: 4px 0 !important;
    min-height: 0 !important;
    height: 42px !important;
    border-radius: 12px !important;
    font-size: 1.3rem !important;
    line-height: 1 !important;
    margin-bottom: 0 !important;
}}
div[data-testid="stVerticalBlock"]:has(> .st-key-mode_light) {{
    gap: 0.4rem !important;
    height: 100% !important;
    justify-content: center !important;
}}
.st-key-mode_light button[kind="primary"], .st-key-mode_dark button[kind="primary"],
.st-key-mode_light [data-testid="stBaseButton-primary"],
.st-key-mode_dark [data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg,#F97316,#EA580C) !important;
    border: 1px solid #EA580C !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(234,88,12,0.30) !important;
}}
.st-key-mode_light button[kind="secondary"], .st-key-mode_dark button[kind="secondary"],
.st-key-mode_light [data-testid="stBaseButton-secondary"],
.st-key-mode_dark [data-testid="stBaseButton-secondary"] {{
    background: rgba(148,163,184,0.18) !important;
    border: 1px solid rgba(148,163,184,0.35) !important;
    opacity: 0.6 !important;
}}

.mc {{
    background: {CARD_BG};
    backdrop-filter: blur(12px);
    border: 1px solid {CARD_BD};
    border-top: 4px solid #1E3A8A;
    border-radius: 10px;
    padding: 16px 16px;
    min-height: 148px;
    height: 100%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.2s;
}}
.mc:hover {{ transform: translateY(-2px); }}
.mc.g {{ border-top-color: #10B981; }}
.mc.r {{ border-top-color: #DC2626; }}
.mc.a {{ border-top-color: #F59E0B; }}
.mc.k {{ border-top-color: #64748B; }}
.ml {{
    color: {T2};
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
    line-height: 1.2;
}}
.mv {{
    color: {T1};
    font-size: 1.25rem;
    font-weight: 800;
    line-height: 1.1;
    white-space: nowrap;
}}
.mv-center {{
    color: {T1};
    font-size: 1.8rem;
    font-weight: 800;
    line-height: 1;
    text-align: center;
    margin: 4px 0;
}}
.pb {{ background: {PB}; border-radius: 999px; height: 5px; overflow: hidden; margin: 9px 0 4px; }}
.pf {{ height: 100%; background: #10B981; border-radius: 999px; }}
.pl {{ color: {T2}; font-size: 0.68rem; font-weight: 600; text-align: center; }}

.sc {{
    background: {CARD_BG};
    border: 1px solid {CARD_BD};
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
.sh {{
    font-size: 0.72rem;
    font-weight: 800;
    color: #EA580C;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.ct {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
.ct thead th {{
    background: {TH};
    color: {T2};
    font-size: 0.64rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 8px 10px;
    text-align: left;
    border-bottom: 1px solid {RL};
}}
.ct tbody tr {{ border-bottom: 1px solid {RL}; }}
.ct tbody td {{ padding: 8px 10px; color: {T1}; vertical-align: middle; }}

.rt {{ table-layout: fixed; }}
.rt th, .rt td {{ overflow-wrap: break-word; word-break: normal; padding: 7px 7px !important; }}
.rt td.idc {{ white-space: nowrap; }}

.cr {{ display: flex; align-items: center; gap: 8px; }}
.cn {{ flex: 1; color: {T1}; font-weight: 600; font-size: 0.82rem; }}
.cb {{ width: 60px; height: 4px; background: {PB}; border-radius: 999px; overflow: hidden; flex-shrink: 0; }}
.cf {{ height: 100%; background: linear-gradient(90deg,#F97316,#C2410C); border-radius: 999px; }}
.cnum {{ font-weight: 800; color: {T1}; font-size: 0.86rem; min-width: 18px; text-align: right; }}
.czero {{ color: {T2}; font-weight: 400; font-style: italic; font-size: 0.78rem; }}

.bdg, .stb {{ display: inline-block; padding: 3px 9px; border-radius: 999px;
              font-size: 0.66rem; font-weight: 700; white-space: nowrap; }}
.ba {{ background: #CCFBF1; color: #0F766E; }}
.bk {{ background: #EDE9FE; color: #6D28D9; }}
.bp {{ background: #FEF9C3; color: #92400E; }}
.bd {{ background: {BD_BG}; color: {BD_C}; }}
.st-ong {{ background: #DBEAFE; color: #1D4ED8; }}
.st-unr {{ background: #FEF3C7; color: #B45309; }}
.st-cmp {{ background: #D1FAE5; color: #047857; }}
.st-cnc {{ background: #E2E8F0; color: #475569; }}
.st-def {{ background: {BD_BG}; color: {BD_C}; }}

.pc {{ background: #FEE2E2; color: #DC2626; padding: 3px 9px; border-radius: 999px; font-size: 0.68rem; font-weight: 700; }}
</style>
""", unsafe_allow_html=True)


def get_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


def mk_badge(text):
    t = str(text).strip().lower()
    if "analisis" in t:   cls = "ba"
    elif "konsultasi" in t or "konsultan" in t: cls = "bk"
    elif "pengajaran" in t: cls = "bp"
    else: cls = "bd"
    return f'<span class="bdg {cls}">{text}</span>'


def mk_status(text):
    s = str(text).strip().lower()
    if s == "ongoing":       return '<span class="stb st-ong">Ongoing</span>'
    if s == "unresponsive":  return '<span class="stb st-unr">Unresponsive</span>'
    if s == "completed":     return '<span class="stb st-cmp">Completed</span>'
    if s == "canceled":      return '<span class="stb st-cnc">Canceled</span>'
    return f'<span class="stb st-def">{text or "-"}</span>'


def check_password():
    def _submit():
        st.session_state["auth_ok"] = (
            st.session_state["_pw"] == st.secrets["APP_PASSWORD"]
        )
        del st.session_state["_pw"]

    if st.session_state.get("auth_ok"):
        return True

    logo_b64 = get_b64("logo gsb.png")
    img_html  = (f'<img src="data:image/png;base64,{logo_b64}" '
                 f'style="max-height:80px;width:auto;margin-bottom:20px;">'
                 if logo_b64 else '')

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div style='margin-top:10vh;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="login-box">
            {img_html}
            <h2 style="margin:0 0 4px;font-weight:800;font-size:1.5rem;color:#1E3A8A;">
                GSB Data Consulting</h2>
            <p style="margin:0 0 24px;color:#64748B;font-size:0.88rem;">
                Authentication Required</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="margin-top:-52px;padding:0 40px;">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.text_input("pw", type="password", key="_pw",
                          label_visibility="collapsed",
                          placeholder="Enter password...")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                _submit()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    return False


if not check_password():
    st.stop()


def _find_col(df, exact, keyword):
    if exact in df.columns:
        return exact
    for c in df.columns:
        if keyword.lower() in str(c).lower():
            return c
    return None


@st.cache_data(ttl=60)
def load_data():
    scope  = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    creds  = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)

    df1 = pd.DataFrame(
        client.open_by_url(st.secrets["URL_SPS1"]).sheet1.get_all_records())
    df2 = pd.DataFrame(
        client.open_by_url(st.secrets["URL_SPS2"]).sheet1.get_all_records())

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    df2 = df2.iloc[24:].reset_index(drop=True).copy()

    col_id     = _find_col(df2, "ID Klien (26.XXX)\nisi 3 angka belakang saja", "ID Klien")
    col_nom    = _find_col(df2, "Nominal yang diberikan", "Nominal")
    col_layan  = _find_col(df1, "Layanan yang diinginkan", "Layanan")
    col_nama   = _find_col(df1, "Nama Klien", "Nama")
    col_kon    = _find_col(df1, "Konsultan", "Konsultan")
    col_topik  = _find_col(df2, "Materi Analisis", "Materi")
    col_kon2   = _find_col(df2, "Nama Konsultan", "Konsultan")
    col_status = _find_col(df1, "Status", "status")

    if not col_id or not col_nom:
        raise ValueError("Critical columns missing in SPS 2.")

    df2[col_id]  = (df2[col_id].astype(str).str.strip()
                    .str.replace(r"\.0$", "", regex=True).str.zfill(3))
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    col_id1 = _find_col(df1, "ID Klien", "ID Klien")
    if not col_id1:
        raise ValueError("Critical column 'ID Klien' missing in SPS 1.")
    df1['Generated_ID'] = (df1[col_id1].astype(str).str.strip()
                           .str.replace(r"\.0$", "", regex=True).str.zfill(3))

    return (df1, df2, col_id, col_nom, col_layan, col_nama,
            col_kon, col_topik, col_kon2, col_status)


try:
    (df_in, df_done, C_ID, C_NOM, C_LAYAN, C_NAMA,
     C_KON, C_TOPIK, C_KON2, C_STATUS) = load_data()
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()


status_ok = bool(C_STATUS and C_STATUS in df_in.columns)
if status_ok:
    status_series  = df_in[C_STATUS].astype(str).str.strip().str.lower()
    n_completed    = int((status_series == "completed").sum())
    n_ongoing      = int((status_series == "ongoing").sum())
    n_unresponsive = int((status_series == "unresponsive").sum())
    n_canceled     = int((status_series == "canceled").sum())
    active_mask    = status_series.isin(["ongoing", "unresponsive"])
else:
    done_ids       = df_done[C_ID].tolist()
    active_mask    = ~df_in['Generated_ID'].isin(done_ids)
    status_series  = pd.Series("ongoing", index=df_in.index)
    n_completed    = int((~active_mask).sum())
    n_ongoing      = int(active_mask.sum())
    n_unresponsive = 0
    n_canceled     = 0

n_in     = len(df_in)
n_done   = n_completed
n_pend   = n_ongoing + n_unresponsive
pct_done = round(n_done / n_in * 100) if n_in else 0


FEE = 50_000
valuation = df_done[C_NOM].sum() + n_in * FEE


def calc_tax(x):
    if x < 150_000:   return 0.0
    if x <= 500_000:  return x * 0.10
    return x * 0.12


tax_df        = (df_done.groupby(C_ID)[C_NOM].sum().reset_index()
                 .rename(columns={C_ID: "ID", C_NOM: "Gross"}))
tax_df["Tax"] = tax_df["Gross"].apply(calc_tax)
tax_df["Net"] = tax_df["Gross"] - tax_df["Tax"]
gross_t = tax_df["Gross"].sum()
tax_t   = tax_df["Tax"].sum()
net_t   = tax_df["Net"].sum()


logo_b64  = get_b64("logo gsb.png")
logo_html = (f'<img src="data:image/png;base64,{logo_b64}" '
             f'style="height:46px;border-radius:50%;margin-right:12px;">'
             if logo_b64 else '')

hdr_col, btn_col = st.columns([13, 1])

with hdr_col:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#F97316 0%,#EA580C 50%,#C2410C 100%);
         border-radius:12px; padding:20px 26px;
         display:flex; justify-content:space-between; align-items:center;
         box-shadow:0 8px 24px rgba(234,88,12,0.22);">
        <div style="display:flex; align-items:center;">
            {logo_html}
            <div>
                <div style="color:#fff; font-size:1.4rem; font-weight:800;
                     line-height:1.2; letter-spacing:-0.02em;">
                    GSB Data Consulting Services</div>
                <div style="color:rgba(255,255,255,0.88); font-size:0.72rem;
                     font-weight:700; text-transform:uppercase; letter-spacing:0.09em;
                     margin-top:3px;">
                    Department of Data Analytics</div>
            </div>
        </div>
        <div style="border-left:2px solid rgba(255,255,255,0.25);
             padding-left:22px; margin-left:8px;">
            <div style="color:rgba(255,255,255,0.85); font-size:0.66rem; font-weight:700;
                 text-transform:uppercase; letter-spacing:0.09em; margin-bottom:3px;">
                Total Estimated Value</div>
            <div style="display:flex; align-items:baseline; gap:9px;">
                <div style="color:#fff; font-size:1.8rem; font-weight:800;
                     line-height:1; letter-spacing:-0.02em;">
                    Rp {valuation:,.0f}</div>
                <div style="color:rgba(255,255,255,0.55); font-size:0.7rem;
                     font-weight:300; letter-spacing:0.02em;">
                    after adm</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with btn_col:
    if st.button("☀️", key="mode_light", use_container_width=True, help="Light mode",
                 type=("primary" if not is_dark else "secondary")):
        st.session_state.dark_mode = False
        st.rerun()
    if st.button("🌙", key="mode_dark", use_container_width=True, help="Dark mode",
                 type=("primary" if is_dark else "secondary")):
        st.session_state.dark_mode = True
        st.rerun()

st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)


c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="mc">
        <div class="ml">Gross Revenue Before Tax</div>
        <div class="mv">Rp {gross_t:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="mc g">
        <div class="ml" style="color:#10B981;">Total Net Revenue</div>
        <div class="mv" style="color:#10B981;">Rp {net_t:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="mc r">
        <div class="ml" style="color:#DC2626;">Total Tax Liability</div>
        <div class="mv" style="color:#DC2626;">Rp {tax_t:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="mc g">
        <div class="ml" style="color:#10B981;">Completed Clients</div>
        <div class="mv-center" style="color:#10B981;">
            {n_done}
            <span style="font-size:0.95rem;color:{T2};font-weight:600;">/ {n_in}</span>
        </div>
        <div class="pb"><div class="pf" style="width:{pct_done}%;"></div></div>
        <div class="pl">{pct_done}% completion rate</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="mc a">
        <div class="ml" style="color:#D97706;">Pending Clients</div>
        <div class="mv-center" style="color:#D97706;margin-top:6px;">{n_pend}</div>
        <div class="pl">ongoing + unresponsive</div>
    </div>""", unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="mc k">
        <div class="ml" style="color:#64748B;">Canceled Clients</div>
        <div class="mv-center" style="color:#64748B;margin-top:6px;">{n_canceled}</div>
        <div class="pl">dibatalkan</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)


MH = 330

CONS_LIST = [
    "Helmi Falah", "Nyayu Azzahra Nabila", "Cut Ashifa Sawallida", "Retno Sari",
    "Rizky Arif Wicaksono", "Pascal Arya Nugroho", "Muhammad Khayruhanif",
    "Qanita Basimah Kurnia", "Afiq Dzakwan Anasti", "Azka Raditya Hafidz",
    "Cameliya Ulya Hidayah", "Intan Aisa", "Varel Geo Syah Putra",
    "Muhammad Shira Pramudita", "Nabeel Muhammad Diaz",
]

col_a, col_b, col_c, col_d = st.columns([1.1, 1.1, 1.1, 2.7], gap="small")


with col_a:
    cdf = pd.DataFrame({"Consultant": CONS_LIST, "N": 0})
    if C_KON and C_KON in df_in.columns:
        counts = (df_in[C_KON].astype(str).str.split(r'[,;\n]+')
                  .explode().str.strip().value_counts().reset_index())
        counts.columns = ["Consultant", "Count"]
        for i, row in cdf.iterrows():
            m = counts[counts['Consultant'].str.lower() == row['Consultant'].lower()]
            if m.empty:
                last = row['Consultant'].split()[-1].lower()
                m = counts[counts['Consultant'].str.lower().str.endswith(last)]
            if not m.empty:
                cdf.at[i, 'N'] = int(m['Count'].values[0])
    cdf = cdf.sort_values('N', ascending=False).reset_index(drop=True)
    mx  = cdf['N'].max() if cdf['N'].max() > 0 else 1

    rows_html = ""
    for _, r in cdf.iterrows():
        if r['N'] > 0:
            pct_bar = int(r['N'] / mx * 100)
            rows_html += f"""<tr><td><div class="cr">
                <span class="cn">{r['Consultant']}</span>
                <div class="cb"><div class="cf" style="width:{pct_bar}%;"></div></div>
                <span class="cnum">{int(r['N'])}</span>
            </div></td></tr>"""
        else:
            rows_html += f"""<tr><td><div class="cr">
                <span class="cn">{r['Consultant']}</span>
                <span class="czero">— 0 klien</span>
            </div></td></tr>"""

    st.markdown(f"""
    <div class="sc" style="height:{MH}px;overflow-y:auto;">
        <div class="sh">Consultant Workload</div>
        <table class="ct">
            <thead><tr><th>Consultant</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)


with col_b:
    if C_LAYAN and C_LAYAN in df_in.columns and n_in > 0:
        svc = df_in[C_LAYAN].value_counts().reset_index()
        svc.columns = ["Service", "Qty"]
        colors = ["#7C3AED", "#059669", "#F59E0B", "#3B82F6", "#EF4444"]
        total_svc = int(svc["Qty"].sum())

        segs = ""
        offset = 25.0
        for i, (_, r) in enumerate(svc.iterrows()):
            p = (r["Qty"] / total_svc * 100) if total_svc else 0
            color = colors[i % len(colors)]
            segs += (f'<circle cx="21" cy="21" r="15.9155" fill="transparent" '
                     f'stroke="{color}" stroke-width="5" '
                     f'stroke-dasharray="{p:.2f} {100 - p:.2f}" '
                     f'stroke-dashoffset="{offset:.2f}"></circle>')
            offset -= p

        donut = (
            f'<svg viewBox="0 0 42 42" style="width:148px;height:148px;">'
            f'<circle cx="21" cy="21" r="15.9155" fill="transparent" stroke="{TB}" stroke-width="5"></circle>'
            f'{segs}'
            f'<text x="21" y="20.5" text-anchor="middle" font-size="7" font-weight="800" fill="{T1}">{n_in}</text>'
            f'<text x="21" y="26" text-anchor="middle" font-size="3.2" fill="{T2}">total</text>'
            f'</svg>'
        )

        legend = ""
        for i, (_, r) in enumerate(svc.iterrows()):
            color = colors[i % len(colors)]
            pc = round(r["Qty"] / n_in * 100) if n_in else 0
            legend += (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'padding:5px 0;border-bottom:1px solid {RL};">'
                f'<div style="display:flex;align-items:center;gap:8px;">'
                f'<div style="width:9px;height:9px;border-radius:50%;background:{color};flex-shrink:0;"></div>'
                f'<span style="color:{T1};font-size:0.8rem;font-weight:500;">{r["Service"]}</span></div>'
                f'<div style="display:flex;align-items:center;gap:8px;">'
                f'<span style="color:{T1};font-weight:700;font-size:0.8rem;">{int(r["Qty"])}</span>'
                f'<span style="color:{T2};font-size:0.74rem;min-width:32px;text-align:right;">{pc}%</span>'
                f'</div></div>'
            )

        st.markdown(f"""
        <div class="sc" style="height:{MH}px;overflow-y:auto;">
            <div class="sh">Service Distribution</div>
            <div style="display:flex;justify-content:center;margin:2px 0 10px;">{donut}</div>
            {legend}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="sc" style="height:{MH}px;"><div class="sh">Service Distribution</div>
        <p style="color:{T2};font-size:0.82rem;">Data layanan tidak ditemukan.</p></div>""",
                    unsafe_allow_html=True)


with col_c:
    t_rows = ""
    if C_TOPIK and C_TOPIK in df_done.columns:
        topic_df = (df_done[C_TOPIK].replace('', pd.NA).dropna()
                    .value_counts().reset_index())
        topic_df.columns = ["Topic", "Qty"]
        t_rows = "".join(
            f"""<tr>
                <td style="font-weight:500;">{r['Topic']}</td>
                <td style="text-align:right;font-weight:700;">{int(r['Qty'])}</td>
            </tr>"""
            for _, r in topic_df.iterrows()
        )

    empty_row = (f'<tr><td colspan="2" style="text-align:center;color:{T2};'
                 f'padding:20px;">No data</td></tr>')

    st.markdown(f"""
    <div class="sc" style="height:{MH}px;overflow-y:auto;">
        <div class="sh">Topic Distribution</div>
        <table class="ct">
            <thead>
                <tr>
                    <th>Topic</th>
                    <th style="text-align:right;">Qty</th>
                </tr>
            </thead>
            <tbody>{t_rows or empty_row}</tbody>
        </table>
    </div>""", unsafe_allow_html=True)


with col_d:
    active_df = df_in[active_mask].copy()
    active_df["_status"] = status_series[active_mask].values

    p_rows = ""
    for _, row in active_df.iterrows():
        id_v = row['Generated_ID']
        nm_v = row[C_NAMA]  if (C_NAMA  and C_NAMA  in active_df.columns) else '-'
        sv_v = row[C_LAYAN] if (C_LAYAN and C_LAYAN in active_df.columns) else '-'
        kn_v = row[C_KON]   if (C_KON   and C_KON   in active_df.columns) else '-'
        stt  = row['_status']
        p_rows += f"""<tr>
            <td class="idc" style="font-weight:700;color:#EA580C;">{id_v}</td>
            <td style="font-weight:600;">{nm_v}</td>
            <td>{mk_badge(sv_v)}</td>
            <td style="color:{T2};font-size:0.77rem;">{kn_v}</td>
            <td>{mk_status(stt)}</td>
        </tr>"""

    n_active = len(active_df)
    chip = (f'<span class="pc">{n_active} active</span>' if n_active > 0
            else f'<span style="color:#10B981;font-size:0.72rem;font-weight:700;">✓ All clear</span>')

    body = (f"""<table class="ct rt">
                <colgroup>
                    <col style="width:9%">
                    <col style="width:24%">
                    <col style="width:20%">
                    <col style="width:25%">
                    <col style="width:22%">
                </colgroup>
                <thead>
                    <tr>
                        <th>ID</th><th>Client</th>
                        <th>Service</th><th>Consultant</th><th>Status</th>
                    </tr>
                </thead>
                <tbody>{p_rows}</tbody>
            </table>"""
            if not active_df.empty
            else f"<p style='text-align:center;color:#10B981;font-weight:600;"
                 f"padding:20px 0;'>✓ Semua klien sudah tertangani.</p>")

    st.markdown(f"""
    <div class="sc" style="height:{MH}px;overflow-y:auto;overflow-x:hidden;">
        <div class="sh">Active Clients {chip}</div>
        {body}
    </div>""", unsafe_allow_html=True)
