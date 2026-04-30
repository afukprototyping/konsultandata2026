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
@st.cache_data(ttl=600) # Cache data selama 10 menit agar tidak kelebihan limit API
def load_data():
    # Menarik kredensial dari Streamlit Secrets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    
    # Buka Spreadsheet berdasarkan URL atau ID (Ganti URL di bawah ini)
    sheet_sps1 = client.open_by_url(st.secrets["URL_SPS1"]).sheet1
    sheet_sps2 = client.open_by_url(st.secrets["URL_SPS2"]).sheet1
    
    # Ekstraksi ke Pandas DataFrame
    df_sps1 = pd.DataFrame(sheet_sps1.get_all_records())
    df_sps2 = pd.DataFrame(sheet_sps2.get_all_records())
    
    # Pra-pemrosesan Data SPS 2 (Pemotongan baris historis)
    # get_all_records otomatis menjadikan baris 1 sebagai header. 
    # Baris 2 di spreadsheet adalah index 0 di DataFrame. Baris 26 adalah index 24.
    df_sps2 = df_sps2.iloc[24:].copy()
    
    # Pra-pemrosesan Kolom Identitas dan Keuntungan
    # Asumsi nama kolom: 'ID Klien' dan 'Nominal Keuntungan'
    df_sps2['ID Klien'] = df_sps2['ID Klien'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(3)
    df_sps2['Nominal Keuntungan'] = pd.to_numeric(df_sps2['Nominal Keuntungan'], errors='coerce').fillna(0)
    
    return df_sps1, df_sps2

st.title("Dashboard Pelacakan KPI & Administrasi Konsultan Data")

try:
    df_sps1, df_sps2 = load_data()
except Exception as e:
    st.error(f"Gagal memuat data dari Google Sheets: {e}")
    st.stop()

# 3. Kalkulasi Metrik Utama
st.header("1. Tinjauan Eksekutif")

total_incoming = len(df_sps1)
total_finished = len(df_sps2)
total_pending = total_incoming - total_finished

total_profit_sps2 = df_sps2['Nominal Keuntungan'].sum()
total_kpi_profit = total_profit_sps2 + (total_incoming * 50000)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Klien Masuk (SPS 1)", total_incoming)
col2.metric("Klien Selesai (SPS 2)", total_finished)
col3.metric("Klien Belum Terdata", total_pending)
col4.metric("Total Profit & Admin", f"Rp {total_kpi_profit:,.0f}")

st.divider()

# 4. Persebaran Layanan
st.header("2. Distribusi Layanan Klien")
if 'Layanan yang diinginkan' in df_sps1.columns:
    service_dist = df_sps1['Layanan yang diinginkan'].value_counts().reset_index()
    service_dist.columns = ['Jenis Layanan', 'Jumlah']
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.dataframe(service_dist, use_container_width=True)
    with col_b:
        st.bar_chart(service_dist.set_index('Jenis Layanan'))
else:
    st.warning("Nama kolom layanan pada SPS 1 tidak sesuai. Pastikan bernama 'Layanan yang diinginkan'.")

st.divider()

# 5. Kalkulasi Pajak Dinamis Berdasarkan Agregasi ID
st.header("3. Kalkulasi Pajak GSB per Klien")

profit_per_client = df_sps2.groupby('ID Klien')['Nominal Keuntungan'].sum().reset_index()

def calculate_tax(amount):
    if amount < 150000:
        return 0
    elif 150000 <= amount <= 500000:
        return amount * 0.10
    else:
        return amount * 0.12

profit_per_client['Pajak GSB'] = profit_per_client['Nominal Keuntungan'].apply(calculate_tax)

# Pemformatan mata uang
profit_per_client['Nominal Keuntungan'] = profit_per_client['Nominal Keuntungan'].apply(lambda x: f"Rp {x:,.0f}")
profit_per_client['Pajak GSB'] = profit_per_client['Pajak GSB'].apply(lambda x: f"Rp {x:,.0f}")

st.dataframe(profit_per_client, use_container_width=True)

if total_pending < 0:
    st.error("Peringatan Sistem: Jumlah Klien Selesai melebihi Klien Masuk. Terdapat anomali data.")
