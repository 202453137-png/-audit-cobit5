import streamlit as st
import pandas as pd
import json

st.set_page_config(
    page_title="Audit COBIT 5",
    page_icon="📋",
    layout="wide"
)

st.title("Form Audit Sistem Informasi COBIT 5")
st.subheader("PT Aneka Rembang (Perseroda)")
st.write("Audit sistem informasi penjualan dan persediaan barang")
st.info("Aplikasi prototipe untuk pembelajaran. Hasil pengisian bukan hasil audit resmi perusahaan.")

# Membaca data pertanyaan
with open("pertanyaan.json", "r", encoding="utf-8") as f:
    pertanyaan = json.load(f)

st.divider()
st.header("Identitas Audit")

with st.form("form_audit"):

    nama = st.text_input("Nama Auditor")
    responden = st.text_input("Nama Responden")
    bagian = st.text_input("Bagian atau Unit Kerja")
    tanggal = st.date_input("Tanggal Audit")

    st.divider()
    st.header("Daftar Pertanyaan Audit")

    jawaban = {}
    bukti = {}
    catatan = {}

    for domain in ["EDM", "APO", "BAI", "DSS", "MEA"]:

        st.subheader(f"Domain {domain}")

        daftar = [
            p for p in pertanyaan
            if p["domain"] == domain
        ]

        for item in daftar:
            nomor = item["no"]

            st.markdown(
                f"**{nomor}. [{item['kode']}] "
                f"{item['pertanyaan']}**"
            )

            jawaban[nomor] = st.selectbox(
                "Jawaban",
                ["Belum dijawab", "Ya", "Tidak", "N/A"],
                key=f"jawaban_{nomor}"
            )

            bukti[nomor] = st.text_input(
                "Bukti Pendukung",
                key=f"bukti_{nomor}"
            )

            catatan[nomor] = st.text_area(
                "Catatan Auditor",
                key=f"catatan_{nomor}",
                height=70
            )

            st.divider()

    submit = st.form_submit_button(
        "Proses Hasil Audit",
        type="primary"
    )

if submit:

    hasil = []

    for item in pertanyaan:
        nomor = item["no"]

        hasil.append({
            "Tanggal": str(tanggal),
            "Auditor": nama,
            "Responden": responden,
            "Unit Kerja": bagian,
            "No": nomor,
            "Domain": item["domain"],
            "Kode": item["kode"],
            "Pertanyaan": item["pertanyaan"],
            "Jawaban": jawaban[nomor],
            "Bukti": bukti[nomor],
            "Catatan": catatan[nomor]
        })

    st.session_state["hasil"] = hasil

if "hasil" in st.session_state:

    df = pd.DataFrame(st.session_state["hasil"])

    st.header("Hasil Audit COBIT 5")

    rekap = pd.crosstab(
        df["Domain"],
        df["Jawaban"]
    )

    rekap = rekap.reindex(
        index=["EDM", "APO", "BAI", "DSS", "MEA"],
        columns=["Ya", "Tidak", "N/A", "Belum dijawab"],
        fill_value=0
    )

    rekap["Total"] = rekap.sum(axis=1)

    pembagi = rekap["Ya"] + rekap["Tidak"]

    rekap["Kepatuhan (%)"] = (
        rekap["Ya"] / pembagi.where(pembagi != 0)
        * 100
    ).round(2)

    st.subheader("Rekapitulasi per Domain")
    st.dataframe(rekap, use_container_width=True)

    st.subheader("Grafik Hasil Audit")
    st.bar_chart(
        rekap[["Ya", "Tidak", "N/A", "Belum dijawab"]]
    )

    belum = int((df["Jawaban"] == "Belum dijawab").sum())

    if belum:
        st.warning(
            f"Masih ada {belum} pertanyaan yang belum dijawab."
        )
    else:
        st.success("Semua pertanyaan sudah dijawab.")

    st.caption(
        "Persentase ini adalah indikator sederhana "
        "berdasarkan jawaban, bukan capability level resmi COBIT 5."
    )

    csv = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Unduh Hasil Audit CSV",
        data=csv,
        file_name="hasil_audit_cobit5.csv",
        mime="text/csv"
    )
