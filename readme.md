# Monitoring Nilai & KRS Siakang

Aplikasi monitoring akademik **Siakang Untirta** berbasis web yang robust dan modern. Kini mendukung pemantauan **Nilai** dan status **Matkul KRS** secara real-time. Memungkinkan Anda memantau banyak akun mahasiswa sekaligus, mengirim notifikasi ke **Telegram** & **WhatsApp**, dan menyediakan dashboard interaktif.

## ✨ Fitur Utama

- 🖥️ **Web Dashboard Modern**: Antarmuka Vue.js responsif dengan Dark Mode.
- 🔄 **Dual Monitoring Mode**:
  - **Monitor Nilai**: Pantau nilai baru, perubahan nilai, IP, dan IPK.
  - **Monitor KRS**: Pantau ketersediaan slot/kelas Matkul incaran saat masa KRS (Livewire Support).
- 📲 **Multi-Channel Notification**: Mendukung **Telegram Bot** dan **WhatsApp** (via WAHA) untuk notifikasi instan.
- 👥 **Multi-Account & Group Support**: Pantau banyak akun sekaligus. Notifikasi WA bisa dikirim ke **Grup WhatsApp**.
- 🖱️ **Smart Reordering**: Atur urutan prioritas monitoring dengan drag & drop yang cerdas per kategori.
- 📋 **One-Click Clone**: Duplikasi konfigurasi task untuk setup cepat.
- 📊 **Visual Data Viewer**:
  - **Nilai**: Lihat transkrip sementara, Mutu, SKS di tabel rapi.
  - **KRS**: Indikator warna (Hijau/Merah) untuk status matkul target (Found/Missing).
- 🛠️ **Full Control**: Start/Stop monitoring, lihat Live Logs, hapus Logs, dan Reset Data scraping langsung dari UI.
- 🐳 **Docker Ready**: Deployment mudah dengan isolasi environment penuh.

## 🚀 Cara Install & Penggunaan

### Opsi 1: Menggunakan Docker (Recommended)

1. **Clone Repository**

   ```bash
   git clone https://github.com/mohfer/monitoring-nilai-siakang
   cd monitoring-nilai-siakang
   ```

2. **Setup Environment Variable**
   Salin `.env.example` ke `.env`:

   ```bash
   cp .env.example .env
   ```

   Isi konfigurasi di dalamnya:
   - `TELEGRAM_TOKEN`: Token bot Telegram (jika pakai).
   - `WAHA_BASE_URL`: URL server WAHA Anda (opsional, untuk WhatsApp).
   - `WAHA_API_KEY`: API Key WAHA (jika ada).

3. **Jalankan Aplikasi**
   ```bash
   docker-compose up -d --build
   ```
   Akses dashboard di: `http://localhost:3000`

### Opsi 2: Instalasi Manual (Developer)

**Prerequisites:** Python 3.10+, Node.js 18+

#### 1. Setup Backend

```bash
python -m venv .venv
# Activate venv (Windows: .venv\Scripts\activate | Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m uvicorn server.main:app --reload --port 8000
```

#### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

## 💡 Panduan Penggunaan

### Membuat Monitor Baru

1. Klik **"+ New Task"**.
2. Pilih Tipe: **Nilai (Grades)** atau **KRS (Plans)**.
3. Masukkan **Login ID** (NIM) & **Password** Siakang.
4. **Notifikasi**:
   - Isi **Telegram Chat ID** untuk notifikasi ke Telegram Personal.
   - Isi **WhatsApp Number** (misal: `62812xxx`) atau **Group ID** (misal: `123...@g.us`) untuk notifikasi WA.
   - _Tips: Cek **Group ID** di Dashboard WAHA Anda (Swagger UI) pada menu **Groups > getGroups**._
5. **Konfigurasi Khusus**:
   - **Mode Nilai**: Klik "Fetch" Semester dan pilih semester aktif.
   - **Mode KRS**: Masukkan nama-nama matkul target (satu per baris) di kolom "Target Courses".
6. Simpan & Klik **Start (▶)**.

### Fitur Lain

- **Clear Logs**: Klik ikon tempat sampah di modal Logs untuk membersihkan log lama.
- **Reset Data**: Klik ikon reset di modal Data untuk menghapus cache hasil scraping agar notifikasi bisa muncul lagi saat data baru masuk.

## ⚠️ Disclaimer

Aplikasi ini menggunakan metode _web scraping_. Perubahan pada website Siakang Untirta dapat mempengaruhi fungsionalitas. Gunakan interval waktu yang wajar (default 300s) agar tidak membebani server kampus.
