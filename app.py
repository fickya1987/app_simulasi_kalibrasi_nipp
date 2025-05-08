import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulasi Kalibrasi Kinerja", layout="wide")
st.title("🔁 Simulasi Kalibrasi Kinerja Individu")

# Upload Excel
uploaded_file = st.file_uploader("📥 Upload file KPI Excel (misalnya kpi_cleaned.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Filter dan bersihkan
    df = df.dropna(subset=["NIPP PEKERJA", "NAMA KPI", "TARGET", "REALISASI (%)", "BOBOT (%)", "POLARITAS"]).copy()
    df["TARGET"] = pd.to_numeric(df["TARGET"], errors="coerce")
    df["REALISASI (%)"] = pd.to_numeric(df["REALISASI (%)"], errors="coerce")
    df["BOBOT (%)"] = pd.to_numeric(df["BOBOT (%)"], errors="coerce")
    df["NIPP PEKERJA"] = df["NIPP PEKERJA"].astype(str)

    # Hitung capaian
    def hitung_capaian(row):
        t, r, p = row["TARGET"], row["REALISASI (%)"], str(row["POLARITAS"]).strip().lower()
        if t == 0 or (p == "negatif" and r == 0): return 0
        return (r / t) * 100 if p == "positif" else (t / r) * 100

    df["CAPAIAN"] = df.apply(hitung_capaian, axis=1)
    df["SKOR TERTIMBANG"] = df["CAPAIAN"] * df["BOBOT (%)"] / 100

    # Dropdown NIPP
    nipp_list = sorted(df["NIPP PEKERJA"].unique())
    selected_nipp = st.selectbox("🆔 Pilih NIPP Pekerja", nipp_list)

    df_nipp = df[df["NIPP PEKERJA"] == selected_nipp].copy()

    # Sidebar simulasi
    st.sidebar.header("⚙️ Parameter Simulasi")
    bobot_kinerja = st.sidebar.slider("Bobot KPI (%)", 50, 100, 80)
    bobot_perilaku = 100 - bobot_kinerja
    nilai_akhlak = st.sidebar.slider("Nilai AKHLAK (%)", 50, 120, 100)

    # Hitung skor akhir
    total_bobot = df_nipp["BOBOT (%)"].sum()
    skor_kinerja = df_nipp["SKOR TERTIMBANG"].sum() / total_bobot * 100 if total_bobot > 0 else 0
    final_score = (skor_kinerja * bobot_kinerja + nilai_akhlak * bobot_perilaku) / 100

    def kategori(skor):
        if skor > 110:
            return "ISTIMEWA"
        elif skor > 105:
            return "SANGAT BAIK"
        elif skor >= 90:
            return "BAIK"
        elif skor >= 80:
            return "CUKUP"
        else:
            return "KURANG"

    kategori_akhir = kategori(final_score)

    # Tabel KPI
    st.subheader("📋 Data KPI Pekerja")
    st.dataframe(df_nipp[["NAMA KPI", "BOBOT (%)", "TARGET", "REALISASI (%)", "CAPAIAN", "SKOR TERTIMBANG"]])

    # Hasil Kalibrasi
    st.subheader("📊 Hasil Simulasi Kalibrasi")
    st.write(f"**Skor Kinerja:** {skor_kinerja:.2f} (Bobot: {bobot_kinerja}%)")
    st.write(f"**Nilai AKHLAK:** {nilai_akhlak} (Bobot: {bobot_perilaku}%)")
    st.success(f"🎯 **Final Skor Gabungan**: {final_score:.2f}")
    st.info(f"🏅 **Kategori Kinerja:** {kategori_akhir}")
