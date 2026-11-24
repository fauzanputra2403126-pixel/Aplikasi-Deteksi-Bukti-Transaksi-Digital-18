"""
Deteksi bukti pembayaran: dHash + jarak Hamming.

Cara pakai (di VS Code tinggal tekan Run / F5):
  1. Taruh bukti yang pasti ASLI di folder  referensi/
  2. Taruh bukti yang mau diuji di folder   uji/
  3. Jalankan:  python deteksi.py

Atau lewat terminal untuk satu file:
  python deteksi.py bukti_baru.jpg
"""
import os
import sys
from PIL import Image, ImageOps

# ---------- Pengaturan ----------
GW, GH, BN = 16, 16, 4          # hash global 16x16 = 256 bit, blok 4x4
T1 = 0.20                       # ambang jarak global (0-1)
T2 = 0.20                       # ambang jarak per blok (0-1)
T3 = 2                          # maksimal blok menyimpang yang ditoleransi
FOLDER_REF = "referensi"
FOLDER_UJI = "uji"
EKSTENSI = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


# ---------- Fungsi dasar ----------
def buka(path):
    """Buka gambar: putar sesuai EXIF, latar transparan jadi putih."""
    img = ImageOps.exif_transpose(Image.open(path))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    return img.convert("RGB")


def dhash(img, w, h):
    """Perkecil ke abu-abu (w+1 x h); bit 1 jika piksel kiri > kanan."""
    px = list(img.convert("L").resize((w + 1, h), Image.LANCZOS).getdata())
    return "".join(
        "1" if px[y * (w + 1) + x] > px[y * (w + 1) + x + 1] else "0"
        for y in range(h) for x in range(w)
    )


def hashes(path):
    """Hash global (256 bit) + 16 hash blok (64 bit per blok)."""
    img = buka(path)
    W, H = img.size
    blocks = []
    for by in range(BN):
        for bx in range(BN):
            box = (bx * W // BN, by * H // BN, (bx + 1) * W // BN, (by + 1) * H // BN)
            blocks.append(dhash(img.crop(box), 8, 8))
    return {"name": os.path.basename(path), "gl": dhash(img, GW, GH), "blocks": blocks}


def ham(a, b):
    """Jarak Hamming = jumlah bit yang berbeda."""
    return sum(x != y for x, y in zip(a, b))


def daftar_gambar(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith(EKSTENSI)
    )


# ---------- Pengujian satu gambar ----------
def uji(path, refs):
    h = hashes(path)

    best = min(refs, key=lambda r: ham(h["gl"], r["gl"]))      # referensi terdekat
    dg = ham(h["gl"], best["gl"])
    gp = dg / 256

    bd = [ham(a, b) for a, b in zip(h["blocks"], best["blocks"])]
    bad = sum(1 for d in bd if d / 64 > T2)

    if gp <= T1 and bad <= T3:
        verdict = "ASLI"
    elif gp <= T1 * 1.5 and bad <= T3 + 3:
        verdict = "MENCURIGAKAN"
    else:
        verdict = "PALSU"

    print(f"\n=== {os.path.basename(path)} ===")
    print(f"Hasil              : {verdict}")
    print(f"Referensi terdekat : {best['name']}")
    print(f"Jarak Hamming      : {dg} dari 256 bit ({gp * 100:.1f}%)")
    print(f"Blok menyimpang    : {bad} dari 16 (batas {T3})")
    print("Jarak per blok (0-64), tanda * = menyimpang:")
    for i in range(0, 16, 4):
        print("   ", "  ".join(f"{d:2d}{'*' if d / 64 > T2 else ' '}" for d in bd[i:i + 4]))
    return verdict


def main():
    ref_files = daftar_gambar(FOLDER_REF)
    if not ref_files:
        sys.exit(f"Folder '{FOLDER_REF}' kosong. Taruh bukti pembayaran ASLI di sana dulu.")
    refs = [hashes(f) for f in ref_files]
    print(f"{len(refs)} referensi dimuat dari '{FOLDER_REF}'.")

    # satu file lewat argumen, atau semua file di folder uji
    targets = sys.argv[1:] or daftar_gambar(FOLDER_UJI)
    if not targets:
        sys.exit(f"Tidak ada gambar uji. Taruh gambar di folder '{FOLDER_UJI}' atau beri nama file.")

    ringkas = {}
    for t in targets:
        ringkas[os.path.basename(t)] = uji(t, refs)

    print("\n--- RINGKASAN ---")
    for nama, v in ringkas.items():
        print(f"{nama:30s} {v}")


if __name__ == "__main__":
    main()
