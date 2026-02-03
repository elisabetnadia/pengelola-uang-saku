import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data.json"

saldo = 0
transaksi = []
target_tabungan = 0
nama_target = ""

def load_data():
    global saldo, transaksi, target_tabungan, nama_target
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            saldo = int(data.get("saldo", 0))
            transaksi = data.get("transaksi", [])
            target_tabungan = int(data.get("target_tabungan", 0))
            nama_target = data.get("nama_target", "")
    except (FileNotFoundError, json.JSONDecodeError):
        saldo = 0
        transaksi = []
        target_tabungan = 0
        nama_target = ""

def save_data():
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"saldo": saldo, "transaksi": transaksi, "target_tabungan": target_tabungan, "nama_target": nama_target}, f, indent=2)
    os.replace(tmp, DATA_FILE)

def tambah_pemasukan():
    global saldo, transaksi
    try:
        jumlah = int(input("Masukkan jumlah pemasukan: "))
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return

    saldo += jumlah
    transaksi.append({
        "tipe": "pemasukan",
        "jumlah": jumlah,
        "waktu": datetime.now().isoformat()
    })
    save_data()
    print(f"Berhasil menambahkan pemasukan sebesar {jumlah}. Saldo sekarang: {saldo}")

def tambah_pengeluaran():
    global saldo, transaksi
    try:
        jumlah = int(input("Masukkan jumlah pengeluaran: "))
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return

    if jumlah > saldo:
        print("Saldo tidak cukup.")
        return

    kategori = input("Kategori (Makan/Transport/dll): ").strip() or "Lainnya"

    saldo -= jumlah
    transaksi.append({
        "tipe": "pengeluaran",
        "jumlah": jumlah,
        "kategori": kategori,
        "waktu": datetime.now().isoformat()
    })
    save_data()
    print(f"Berhasil mengurangi pengeluaran sebesar {jumlah} (Kategori: {kategori}). Saldo sekarang: {saldo}")

def lihat_saldo():
    global saldo
    print("=== Saldo Saat Ini ===")
    print(f"Rp {saldo:,}")

def cek_peringatan_boros(total_pemasukan, total_pengeluaran, threshold=0.7):
    """Tampilkan peringatan jika pengeluaran melebihi persentase dari pemasukan."""
    if total_pemasukan > 0:
        if total_pengeluaran > total_pemasukan * threshold:
            print(f"⚠️ Peringatan: Pengeluaran sudah melebihi {int(threshold*100)}% pemasukan!")
    else:
        if total_pengeluaran > 0:
            print("⚠️ Peringatan: Belum ada pemasukan namun sudah ada pengeluaran!")

def laporan():
    global saldo, transaksi
    if not transaksi:
        print("Belum ada transaksi.")
        return

    filter_bulan = input("Filter bulan (YYYY-MM) atau tekan Enter untuk semua: ").strip()
    filtered = transaksi
    if filter_bulan:
        try:
            year, month = map(int, filter_bulan.split("-"))
            filtered = [t for t in transaksi if datetime.fromisoformat(t.get("waktu", "")).year == year and datetime.fromisoformat(t.get("waktu", "")).month == month]
            if not filtered:
                print("Tidak ada transaksi pada periode tersebut.")
                return
        except Exception:
            print("Format filter tidak valid. Gunakan YYYY-MM.")
            return

    total_pemasukan = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pemasukan")
    total_pengeluaran = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pengeluaran")
    print("=== Laporan Transaksi ===")
    if filter_bulan:
        print(f"Periode: {filter_bulan}")

    # Ringkasan ringkas dalam tabel
    print("\n+---------------------------+---------------------------+")
    print("| Total pemasukan           | Total pengeluaran         |")
    print("+---------------------------+---------------------------+")
    print(f"| Rp {total_pemasukan:>23,} | Rp {total_pengeluaran:>23,} |")
    print("+---------------------------+---------------------------+")
    print(f"Saldo saat ini: Rp {saldo:,}")

    # Peringatan boros jika pengeluaran > 70% pemasukan
    cek_peringatan_boros(total_pemasukan, total_pengeluaran)

    # Ringkasan per kategori (hanya pengeluaran) sebagai tabel
    kategori_sums = {}
    for t in filtered:
        if t.get("tipe") == "pengeluaran":
            k = t.get("kategori", "Lainnya")
            kategori_sums[k] = kategori_sums.get(k, 0) + t.get("jumlah", 0)

    if kategori_sums:
        print("\n+----------------------+---------------------------+")
        print("| Kategori             | Jumlah                    |")
        print("+----------------------+---------------------------+")
        for k, v in sorted(kategori_sums.items(), key=lambda x: x[1], reverse=True):
            print(f"| {k:<20} | Rp {v:>23,} |")
        print("+----------------------+---------------------------+")
        # Pengeluaran terbanyak
        top_k, top_v = max(kategori_sums.items(), key=lambda x: x[1])
        print(f"\nPengeluaran terbanyak: {top_k} (Rp {top_v:,})")

    # Daftar transaksi sebagai tabel
    print("\n+---------------------+-----------+--------------+---------------------------+")
    print("| Waktu               | Tipe      | Kategori     | Jumlah                    |")
    print("+---------------------+-----------+--------------+---------------------------+")
    for t in sorted(filtered, key=lambda x: x.get("waktu"), reverse=True):
        waktu = datetime.fromisoformat(t.get("waktu")).strftime("%d-%m %H:%M")
        tipe = t.get("tipe", "")
        jumlah = t.get("jumlah", 0)
        kategori = t.get("kategori", "-")
        if tipe == "pengeluaran":
            print(f"| {waktu:<19} | {tipe.title():9} | {kategori:<12} | Rp {jumlah:>23,} |")
        else:
            print(f"| {waktu:<19} | {tipe.title():9} | {'-':12} | Rp {jumlah:>23,} |")
    print("+---------------------+-----------+--------------+---------------------------+")

def set_target():
    global target_tabungan, nama_target
    nama = input("Nama target tabungan: ").strip()
    if not nama:
        print("Nama target tidak boleh kosong.")
        return
    try:
        jumlah = int(input("Jumlah target: "))
        if jumlah <= 0:
            print("Jumlah target harus lebih dari 0.")
            return
    except ValueError:
        print("Input tidak valid. Masukkan angka.")
        return
    nama_target = nama
    target_tabungan = jumlah
    save_data()
    print("Target tabungan berhasil disimpan!")

def lihat_target():
    global saldo, target_tabungan, nama_target
    if target_tabungan == 0:
        print("Belum ada target tabungan.")
        return

    persen = (saldo / target_tabungan) * 100 if target_tabungan else 0
    persen_tampil = min(persen, 100)

    print("=== Target Tabungan ===")
    print(f"Target : {nama_target}")
    print(f"Jumlah target: Rp {target_tabungan:,}")
    print(f"Saldo saat ini: Rp {saldo:,}")
    print(f"Progress: {persen_tampil:.2f}%")

    if saldo >= target_tabungan:
        print("🎉 Selamat! Target tabungan sudah tercapai!")

def riwayat_periode():
    while True:
        print("=== Riwayat Transaksi ===")
        print("1. Hari ini")
        print("2. Mingguan (7 hari terakhir)")
        print("3. Bulanan (bulan ini)")
        print("4. Kembali")
        pilihan = input("Pilih: ")
        if pilihan == "1":
            transaksi_hari_ini()
        elif pilihan == "2":
            transaksi_mingguan()
        elif pilihan == "3":
            transaksi_bulanan()
        elif pilihan == "4":
            break
        else:
            print("Pilihan tidak valid")


def transaksi_hari_ini():
    today = datetime.now().date()
    filtered = [t for t in transaksi if datetime.fromisoformat(t.get("waktu", "")).date() == today]
    print("=== Transaksi Hari Ini ===")
    if not filtered:
        print("Tidak ada transaksi hari ini.")
        return
    total_pemasukan = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pemasukan")
    total_pengeluaran = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pengeluaran")
    print(f"Total pemasukan   : Rp {total_pemasukan:,}")
    print(f"Total pengeluaran : Rp {total_pengeluaran:,}")
    # Peringatan boros untuk periode ini
    cek_peringatan_boros(total_pemasukan, total_pengeluaran)
    print("\nDaftar transaksi:")
    for t in sorted(filtered, key=lambda x: x.get("waktu"), reverse=True):
        waktu = datetime.fromisoformat(t.get("waktu")).strftime("%d-%m-%Y %H:%M")
        tipe = t.get("tipe", "")
        jumlah = t.get("jumlah", 0)
        kategori = t.get("kategori", "-")
        if tipe == "pengeluaran":
            print(f"- {waktu} | {tipe.title():10} | {kategori:10} | Rp {jumlah:,}")
        else:
            print(f"- {waktu} | {tipe.title():10} | Rp {jumlah:,}")


def transaksi_mingguan():
    today = datetime.now().date()
    start = today - timedelta(days=6)
    filtered = [t for t in transaksi if start <= datetime.fromisoformat(t.get("waktu", "")).date() <= today]
    print(f"=== Transaksi Mingguan ({start.strftime('%d-%m-%Y')} - {today.strftime('%d-%m-%Y')}) ===")
    if not filtered:
        print("Tidak ada transaksi dalam periode ini.")
        return
    total_pemasukan = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pemasukan")
    total_pengeluaran = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pengeluaran")
    print(f"Total pemasukan   : Rp {total_pemasukan:,}")
    print(f"Total pengeluaran : Rp {total_pengeluaran:,}")
    # Peringatan boros untuk periode ini
    cek_peringatan_boros(total_pemasukan, total_pengeluaran)
    print("\nDaftar transaksi:")
    for t in sorted(filtered, key=lambda x: x.get("waktu"), reverse=True):
        waktu = datetime.fromisoformat(t.get("waktu")).strftime("%d-%m-%Y %H:%M")
        tipe = t.get("tipe", "")
        jumlah = t.get("jumlah", 0)
        kategori = t.get("kategori", "-")
        if tipe == "pengeluaran":
            print(f"- {waktu} | {tipe.title():10} | {kategori:10} | Rp {jumlah:,}")
        else:
            print(f"- {waktu} | {tipe.title():10} | Rp {jumlah:,}")


def transaksi_bulanan():
    now = datetime.now()
    filtered = [t for t in transaksi if datetime.fromisoformat(t.get("waktu", "")).year == now.year and datetime.fromisoformat(t.get("waktu", "")).month == now.month]
    print(f"=== Transaksi Bulanan ({now.strftime('%B %Y')}) ===")
    if not filtered:
        print("Tidak ada transaksi dalam periode ini.")
        return
    total_pemasukan = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pemasukan")
    total_pengeluaran = sum(t.get("jumlah", 0) for t in filtered if t.get("tipe") == "pengeluaran")
    print(f"Total pemasukan   : Rp {total_pemasukan:,}")
    print(f"Total pengeluaran : Rp {total_pengeluaran:,}")
    # Peringatan boros untuk periode ini
    cek_peringatan_boros(total_pemasukan, total_pengeluaran)
    print("\nDaftar transaksi:")
    for t in sorted(filtered, key=lambda x: x.get("waktu"), reverse=True):
        waktu = datetime.fromisoformat(t.get("waktu")).strftime("%d-%m-%Y %H:%M")
        tipe = t.get("tipe", "")
        jumlah = t.get("jumlah", 0)
        kategori = t.get("kategori", "-")
        if tipe == "pengeluaran":
            print(f"- {waktu} | {tipe.title():10} | {kategori:10} | Rp {jumlah:,}")
        else:
            print(f"- {waktu} | {tipe.title():10} | Rp {jumlah:,}")


def menu():
    print("=== Aplikasi Pengelola Uang Saku ===")
    print("1. Tambah pemasukan")
    print("2. Tambah pengeluaran")
    print("3. Lihat saldo")
    print("4. Set target")
    print("5. Lihat target")
    print("6. Riwayat Transaksi")
    print("7. Laporan")
    print("8. Keluar")

if __name__ == "__main__":
    load_data()
    while True:
        menu()
        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            tambah_pemasukan()
        elif pilihan == "2":
            tambah_pengeluaran()
        elif pilihan == "3":
            lihat_saldo()
        elif pilihan == "4":
            set_target()
        elif pilihan == "5":
            lihat_target()
        elif pilihan == "6":
            riwayat_periode()
        elif pilihan == "7":
            laporan()
        elif pilihan == "8":
            save_data()
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak valid")
