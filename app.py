import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials
import base64
import os

st.set_page_config(
    page_title="GSB Admin Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 1. CSS Injection: Ultra-Modern Dark Theme & Glassmorphism
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp {
    background-color: #020617; /* Deep Slate 950 for premium dark mode */
}
#MainMenu, footer, header {
    visibility: hidden;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
}

/* Glassmorphism Header */
.header-container {
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 32px 48px;
    margin-bottom: 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
}
.header-title {
    color: #F8FAFC;
    font-size: 2.25rem;
    font-weight: 800;
    margin: 0 0 6px 0;
    letter-spacing: -0.03em;
}
.header-subtitle {
    color: #94A3B8;
    font-size: 0.95rem;
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.02em;
}
.header-kpi-label {
    color: #64748B;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    text-align: right;
    margin-bottom: 8px;
}
.header-kpi-value {
    background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.75rem;
    font-weight: 800;
    line-height: 1;
    text-align: right;
    letter-spacing: -0.02em;
}

/* Typography & Sections */
.section-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    letter-spacing: -0.01em;
}

/* Modern Hover Cards */
.custom-metric-card {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    height: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.custom-metric-card:hover {
    transform: translateY(-4px);
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.4);
}
.cmc-label {
    color: #94A3B8;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}
.cmc-value {
    color: #F8FAFC;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.cmc-caption {
    color: #64748B;
    font-size: 0.85rem;
    margin-top: 12px;
    font-weight: 400;
}
.cmc-value.warning {
    color: #F43F5E;
}

/* Financial Tax Cards with subtle colored gradients */
.fin-card {
    border-radius: 16px;
    padding: 24px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    background: linear-gradient(145deg, rgba(15,23,42,0.6) 0%, rgba(2,6,23,0.8) 100%);
    transition: transform 0.3s ease;
}
.fin-card:hover { transform: translateY(-2px); }
.fin-card.danger {
    background: linear-gradient(145deg, rgba(69,10,10,0.3) 0%, rgba(2,6,23,0.8) 100%);
    border-color: rgba(248,113,113,0.15);
}
.fin-card.success {
    background: linear-gradient(145deg, rgba(5,46,22,0.3) 0%, rgba(2,6,23,0.8) 100%);
    border-color: rgba(74,222,128,0.15);
}

/* Streamlit Dataframe Clean Up */
.stDataFrame {
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

/* Custom Navigation Menu Styling (Transforming Radio Buttons) */
div[role="radiogroup"] {
    gap: 12px;
}
div[role="radiogroup"] > label {
    background: rgba(15, 23, 42, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 14px 20px;
    cursor: pointer;
    transition: all 0.2s ease;
}
div[role="radiogroup"] > label:hover {
    background: rgba(30, 41, 59, 0.6);
    border-color: rgba(255, 255, 255, 0.1);
}
/* Hide the native radio circle */
div[role="radiogroup"] span[data-baseweb="radio"] {
    display: none;
}
div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {
    font-size: 0.95rem;
    font-weight: 600;
    color: #CBD5E1;
    margin: 0;
}

/* Login Box Glassmorphism */
.login-box {
    max-width: 440px;
    margin: 10vh auto;
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 48px 40px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# 2. Base64 Image Helper
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 3. Authentication System (Upgraded Logo Size)
def check_password():
    def _submit():
        st.session_state["auth_ok"] = (
            st.session_state["_pw"] == st.secrets["APP_PASSWORD"]
        )
        del st.session_state["_pw"]

    if st.session_state.get("auth_ok"):
        return True

    failed = st.session_state.get("auth_ok") is False
    title  = "Access Denied" if failed else "Secure Login"
    note   = "Invalid credentials." if failed else "Enter your password to access the workspace."

    # Logo max-height significantly increased to 180px
    logo_b64 = get_base64_image("logo gsb.png")
    img_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 180px; margin-bottom: 32px; display: block; margin-left: auto; margin-right: auto; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));">' if logo_b64 else ''

    st.markdown(
        f'<div class="login-box">'
        f'{img_html}'
        f'<h2 style="margin:0 0 8px;font-weight:800;font-size:1.75rem;color:#F8FAFC;letter-spacing:-0.03em;">{title}</h2>'
        f'<p style="margin:0 0 32px;color:#94A3B8;font-size:0.95rem;">{note}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown('<div style="margin-top:-95px;"></div>', unsafe_allow_html=True)
        st.text_input("pw", type="password", on_change=_submit, key="_pw",
                      label_visibility="collapsed", placeholder="Enter Password...")
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
    col_konsul  = _find_col(df1, "Konsultan", "Konsultan")

    if not col_id or not col_nom:
        raise ValueError(f"Critical columns not found. SPS2 Columns: {list(df2.columns)}")

    df2[col_id]  = df2[col_id].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)
    df2[col_nom] = pd.to_numeric(df2[col_nom], errors="coerce").fillna(0)

    col_id_sps1 = _find_col(df1, "ID Klien", "ID Klien")
    if not col_id_sps1:
        raise ValueError(f"Critical column 'ID Klien' not found in SPS1. Columns: {list(df1.columns)}")
    
    df1['Generated_ID'] = df1[col_id_sps1].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(3)

    return df1, df2, col_id, col_nom, col_layanan, col_nama, col_konsul


try:
    df_incoming, df_completed, COL_ID, COL_NOM, COL_LAYANAN, COL_NAMA, COL_KONSULTAN = load_data()
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
# HEADER SECTION (Always visible)
# ---------------------------------------------------------
st.markdown(f"""
<div class="header-container">
    <div>
        <h1 class="header-title">GSB Workspace</h1>
        <p class="header-subtitle">Data Analytics Department &middot; Operations Dashboard</p>
    </div>
    <div>
        <div class="header-kpi-label">Estimated KPI Valuation</div>
        <div class="header-kpi-value">Rp {total_kpi:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# LAYOUT STRUCTURE: Main Content (Left) + Menu (Right)
# ---------------------------------------------------------
content_col, menu_col = st.columns([3.5, 1], gap="large")

with menu_col:
    st.markdown('<div class="section-title" style="font-size: 1rem; border: none; margin-bottom: 8px;">Navigation Menu</div>', unsafe_allow_html=True)
    selected_view = st.radio(
        "Select View:",
        ["Executive Summary", "Tax Liability", "Service Distribution", "Pending Clients", "Consultant Workload"],
        label_visibility="collapsed"
    )

with content_col:
    
    # --- VIEW 1: EXECUTIVE SUMMARY ---
    if selected_view == "Executive Summary":
        st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="custom-metric-card" style="margin-bottom: 20px;">
                <div class="cmc-label">Incoming Clients</div>
                <div class="cmc-value">{total_incoming}</div>
            </div>
            """, unsafe_allow_html=True)
            
            warning_class = "warning" if total_pending < 0 else ""
            st.markdown(f"""
            <div class="custom-metric-card">
                <div class="cmc-label">Pending Clients</div>
                <div class="cmc-value {warning_class}">{total_pending}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="custom-metric-card" style="margin-bottom: 20px;">
                <div class="cmc-label">Completed Clients</div>
                <div class="cmc-value">{total_completed}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="custom-metric-card">
                <div class="cmc-label">Base Revenue</div>
                <div class="cmc-value">Rp {profit_completed:,.0f}</div>
                <div class="cmc-caption">+ Rp {total_commitment:,.0f} (Commitment Fees)</div>
            </div>
            """, unsafe_allow_html=True)

    # --- VIEW 2: TAX LIABILITY ---
    elif selected_view == "Tax Liability":
        st.markdown('<div class="section-title">Tax Liability Overview</div>', unsafe_allow_html=True)
        
        t1, t2, t3 = st.columns(3)
        with t1:
            st.markdown(f"""
            <div class="fin-card">
                <div class="cmc-label" style="color: #94A3B8;">Total Gross Accumulation</div>
                <div class="cmc-value" style="font-size:1.5rem; color:#F8FAFC;">Rp {accum_gross:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with t2:
            st.markdown(f"""
            <div class="fin-card danger">
                <div class="cmc-label" style="color: #FCA5A5;">Total Tax Liability</div>
                <div class="cmc-value" style="font-size:1.5rem; color:#F87171;">Rp {accum_tax:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with t3:
            st.markdown(f"""
            <div class="fin-card success">
                <div class="cmc-label" style="color: #86EFAC;">Total Net Revenue</div>
                <div class="cmc-value" style="font-size:1.5rem; color:#4ADE80;">Rp {accum_net:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        display_pajak = pajak_df.copy()
        for col in ["Gross Accumulation", "Tax Liability", "Net Revenue"]:
            display_pajak[col] = display_pajak[col].apply(lambda x: f"Rp {x:,.0f}")

        st.dataframe(display_pajak, use_container_width=True, hide_index=True)

    # --- VIEW 3: SERVICE DISTRIBUTION ---
    elif selected_view == "Service Distribution":
        st.markdown('<div class="section-title">Client Service Distribution</div>', unsafe_allow_html=True)
        
        if COL_LAYANAN and COL_LAYANAN in df_incoming.columns:
            service_dist = df_incoming[COL_LAYANAN].value_counts().reset_index()
            service_dist.columns = ["Service Type", "Number of Clients"]
            
            col_a, col_b = st.columns([1, 1.5])
            with col_a:
                st.dataframe(service_dist, use_container_width=True, hide_index=True)
            with col_b:
                fig = px.pie(service_dist, values='Number of Clients', names='Service Type', hole=0.55)
                fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#020617', width=2)))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    font=dict(color='#F8FAFC', family='Plus Jakarta Sans'),
                    margin=dict(t=0, b=0, l=0, r=0),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Service column not found in incoming database.")

    # --- VIEW 4: PENDING CLIENTS ---
    elif selected_view == "Pending Clients":
        st.markdown('<div class="section-title">Unrecorded / Pending Clients</div>', unsafe_allow_html=True)
        
        completed_ids = df_completed[COL_ID].tolist()
        pending_df = df_incoming[~df_incoming['Generated_ID'].isin(completed_ids)].copy()

        if pending_df.empty:
            st.success("All incoming clients have been successfully processed and recorded.")
        else:
            display_cols = ['Generated_ID']
            rename_dict = {'Generated_ID': 'Client ID'}
            
            if COL_NAMA and COL_NAMA in pending_df.columns:
                display_cols.append(COL_NAMA)
                rename_dict[COL_NAMA] = 'Client Name'
            if COL_LAYANAN and COL_LAYANAN in pending_df.columns:
                display_cols.append(COL_LAYANAN)
                rename_dict[COL_LAYANAN] = 'Service Type'
            if COL_KONSULTAN and COL_KONSULTAN in pending_df.columns:
                display_cols.append(COL_KONSULTAN)
                rename_dict[COL_KONSULTAN] = 'Assigned Consultant'
            
            clean_pending_df = pending_df[display_cols].rename(columns=rename_dict)
            st.dataframe(clean_pending_df, use_container_width=True, hide_index=True)

    # --- VIEW 5: CONSULTANT WORKLOAD ---
    elif selected_view == "Consultant Workload":
        st.markdown('<div class="section-title">Consultant Workload Metrics</div>', unsafe_allow_html=True)
        
        CONSULTANTS_LIST = [
            "Helmi Falah", "Nyayu Azzahra Nabila", "Cut Ashifa Sawallida", "Retno Sari", 
            "Rizky Arif Wicaksono", "Pascal Arya Nugroho", "Muhammad Khayruhanif", 
            "Qanita Basimah Kurnia", "Afiq Dzakwan Anasti", "Azka Raditya Hafidz", 
            "Cameliya Ulya Hidayah", "Intan Aisa", "Varel Geo Syah Putra", 
            "Muhammad Shira Pramudita", "Nabeel Muhammad Diaz"
        ]

        consultant_df = pd.DataFrame({"Consultant": CONSULTANTS_LIST, "Clients Handled": 0})

        if COL_KONSULTAN and COL_KONSULTAN in df_incoming.columns:
            actual_counts = df_incoming[COL_KONSULTAN].astype(str).str.strip().value_counts().reset_index()
            actual_counts.columns = ["Consultant", "Count"]

            for idx, row in consultant_df.iterrows():
                match = actual_counts[actual_counts['Consultant'].str.lower() == row['Consultant'].lower()]
                if not match.empty:
                    consultant_df.at[idx, 'Clients Handled'] = match['Count'].values[0]

            consultant_df = consultant_df.sort_values(by="Clients Handled", ascending=False).reset_index(drop=True)

            c_table, c_chart = st.columns([1, 1.5])
            with c_table:
                st.dataframe(consultant_df, use_container_width=True, hide_index=True)
            with c_chart:
                fig2 = px.bar(consultant_df, x='Clients Handled', y='Consultant', orientation='h')
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#F8FAFC', family='Plus Jakarta Sans'),
                    yaxis={'categoryorder':'total ascending'},
                    margin=dict(t=0, b=0, l=0, r=0),
                    xaxis_title="Total Clients Handled",
                    yaxis_title=""
                )
                fig2.update_traces(marker_color='#38BDF8', marker_line_color='#020617', marker_line_width=1.5)
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Consultant column not found in incoming database.")
