import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman Dasar
st.set_page_config(page_title="Dashboard Administrasi GSB", layout="wide")

# 1. Sistem Proteksi Password
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("Autentikasi Diperlukan")
        st.text_input("Masukkan Password Dashboard:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("Autentikasi Diperlukan")
        st.text_input("Masukkan Password Dashboard:", type="password", on_change=password_entered, key="password")
        st.error("Password salah. Akses ditolak.")
        return False
    return True

if not check_password():
    st.stop()

# 2. Koneksi ke Google Sheets
@st.cache_data(ttl=600)
def load_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    
    sheet_sps1 = client.open_by_url(st.secrets["URL_SPS1"]).sheet1
    sheet_sps2 = client.open_by_url(st.secrets["URL_SPS2"]).sheet1
    
    df_sps1 = pd.DataFrame(sheet_sps1.get_all_records())
    df_sps2 = pd.DataFrame(sheet_sps2.get_all_records())
    
    # Memotong 24 baris pertama (data historis tahun lalu)
    df_sps2 = df_sps2.iloc[24:].copy()
    
    # Pembersihan spasi atau enter tak kasatmata pada nama kolom (mencegah KeyError)
    df_sps1.columns = df_sps1.columns.str.strip()
    df_sps2.columns = df_sps2.columns.str.strip()
    
    # Definisi Nama Kolom Absolut
    # Jika ada karakter Enter (Alt+Enter) di spreadsheet, Pandas membacanya sebagai \n
    NAMA_KOLOM_NOMINAL = "Nominal yang diberikan"
    NAMA_KOLOM_ID = "ID Klien (26.XXX)\nisi 3 angka belakang saja"
    NAMA_KOLOM_LAYANAN = "Layanan yang diinginkan"
    
    # Verifikasi dan fallback jika format nama kolom sedikit berbeda di Sheets
    if NAMA_KOLOM_ID not in df_sps2.columns:
        # Mencari kolom yang mengandung kata "ID Klien" jika nama persis tidak ditemukan
        for col in df_sps2.columns:
            if "ID Klien" in str(col):
                NAMA_KOLOM_ID = col
                break
                
    if NAMA_KOLOM_NOMINAL not in df_sps2.columns:
        for col in df_sps2.columns:
            if "Nominal yang diberikan" in str(col):
                NAMA_KOLOM_NOMINAL = col
                break

    # Standardisasi ID Klien dan Nominal Keuntungan
    df_sps2[NAMA_KOLOM_ID] = df_sps2[NAMA_KOLOM_ID].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(3)
    df_sps2[NAMA_KOLOM_NOMINAL] = pd.to_numeric(df_sps2[NAMA_KOLOM_NOMINAL], errors='coerce').fillna(0)
    
    # Menyimpan variabel nama kolom ke session state
    st.session_state['col_id'] = NAMA_KOLOM_ID
    st.session_state['col_nom'] = NAMA_KOLOM_NOMINAL
    st.session_state['col_layanan'] = NAMA_KOLOM_LAYANAN
    
    return df_sps1, df_sps2

st.title("Dashboard Pelacakan KPI & Administrasi Konsultan Data")

try:
    df_sps1, df_sps2 = load_data()
except Exception as e:
    st.error(f"Gagal memuat data dari Google Sheets. Detail Error: {e}")
    st.stop()

# 3. Kalkulasi Metrik Utama
st.header("1. Tinjauan Eksekutif")

total_incoming = len(df_sps1)
total_finished = len(df_sps2)
total_pending = total_incoming - total_finished

total_profit_sps2 = df_sps2[st.session_state['col_nom']].sum()
total_kpi_profit = total_profit_sps2 + (total_incoming * 50000)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Klien Masuk (SPS 1)", total_incoming)
col2.metric("Klien Selesai (SPS 2)", total_finished)
col3.metric("Klien Belum Terdata", total_pending)
col4.metric("Total Profit & Admin", f"Rp {total_kpi_profit:,.0f}")

st.divider()

# 4. Persebaran Layanan
st.header("2. Distribusi Layanan Klien")
# Pengecekan kolom layanan
col_layanan_aktual = st.session_state['col_layanan']
if col_layanan_aktual not in df_sps1.columns:
    for col in df_sps1.columns:
        if "Layanan" in str(col):
            col_layanan_aktual = col
            break

if col_layanan_aktual in df_sps1.columns:
    service_dist = df_sps1[col_layanan_aktual].value_counts().reset_index()
    service_dist.columns = ['Jenis Layanan', 'Jumlah']
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.dataframe(service_dist, use_container_width=True)
    with col_b:
        st.bar_chart(service_dist.set_index('Jenis Layanan'))
else:
    st.warning("Kolom Layanan tidak ditemukan pada SPS 1.")

st.divider()

# 5. Kalkulasi Pajak Dinamis Berdasarkan Agregasi ID
st.header("3. Kalkulasi Pajak GSB per Klien")

profit_per_client = df_sps2.groupby(st.session_state['col_id'])[st.session_state['col_nom']].sum().reset_index()

def calculate_tax(amount):
    if amount < 150000:
        return 0
    elif 150000 <= amount <= 500000:
        return amount * 0.10
    else:
        return amount * 0.12

profit_per_client['Pajak GSB'] = profit_per_client[st.session_state['col_nom']].apply(calculate_tax)

# Pemformatan mata uang
profit_per_client[st.session_state['col_nom']] = profit_per_client[st.session_state['col_nom']].apply(lambda x: f"Rp {x:,.0f}")
profit_per_client['Pajak GSB'] = profit_per_client['Pajak GSB'].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(profit_per_client, use_container_width=True)

if total_pending < 0:
    st.error("Peringatan Sistem: Jumlah Klien Selesai melebihi Klien Masuk. Terdapat anomali data.")
