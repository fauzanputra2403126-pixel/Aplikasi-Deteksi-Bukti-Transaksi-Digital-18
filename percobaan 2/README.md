# Deteksi Bukti Pembayaran (dHash + Jarak Hamming)

## Persiapan
1. Buka folder ini di VS Code (File > Open Folder). Pasang ekstensi Python bila belum.
2. Buka terminal VS Code (Ctrl+`) lalu jalankan:
   pip install -r requirements.txt
3. Taruh bukti ASLI di folder `referensi/`.
4. Taruh bukti yang diuji di folder `uji/`.

## Menjalankan
- Tekan F5 (atau tombol Run) pada `deteksi.py`, atau
- Terminal: `python deteksi.py`  (semua gambar di uji/)
- Satu file: `python deteksi.py bukti_baru.jpg`

## Mengatur ambang
Ubah T1, T2, T3 di bagian atas `deteksi.py`.

Catatan: hasil hanya indikasi kemiripan tampilan dengan templat, bukan bukti transaksi.
Cocokkan dengan mutasi rekening untuk transaksi penting.
