"""
Script Monitoring Nilai Siakang
-------------------------------
Script ini memantau halaman nilai di Siakang Untirta secara berkala.
Jika terdeteksi perubahan nilai (nilai baru keluar atau berubah),
script akan mengirim notifikasi ke Telegram.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

URL_LOGIN = os.getenv("URL_LOGIN")
URL_TARGET = os.getenv("URL_TARGET")
LOGIN_ID = os.getenv("LOGIN_ID")
PASSWORD = os.getenv("PASSWORD")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FILE_DATA = os.getenv("FILE_DATA")
INTERVAL = int(os.getenv("INTERVAL", 300))

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

def send_telegram(message):
    """
    Mengirim pesan teks ke bot Telegram yang dikonfigurasi.
    
    Args:
        message (str): Isi pesan yang akan dikirim (format Markdown).
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Gagal kirim Telegram: {e}")

def do_login():
    """Melakukan proses login untuk mendapatkan session cookie."""
    try:
        print("🔑 Mencoba login ke Siakang...")
        res_page = session.get(URL_LOGIN)
        soup = BeautifulSoup(res_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': '_token'})['value']
        
        login_data = {
            '_token': csrf_token,
            'email': LOGIN_ID,
            'username': LOGIN_ID,
            'password': PASSWORD
        }
        
        response = session.post(URL_LOGIN, data=login_data)
        if response.ok:
            print("✅ Login berhasil.")
            return True
    except Exception as e:
        print(f"❌ Error saat login: {e}")
    return False

def get_data():
    """Mengambil data nilai menggunakan session yang ada."""
    try:
        res = session.get(URL_TARGET)
        
        if res.status_code != 200:
            print(f"⚠️ Server Kampus memberikan respon tidak normal: {res.status_code}")
            return []

        soup_target = BeautifulSoup(res.text, 'html.parser')
        tbody = soup_target.find('tbody')

        if not tbody:
            if "auth/login" in res.url:
                print("⚠️ Sesi habis (Redirect ke login).")
            else:
                print("⚠️ Tabel tidak ditemukan (Sesi gantung/halaman error).")
            
            print("🔄 Memaksa login ulang untuk menyegarkan sesi...")
            if do_login():
                res = session.get(URL_TARGET)
                soup_target = BeautifulSoup(res.text, 'html.parser')
                tbody = soup_target.find('tbody')
            
            if not tbody:
                print("❌ Masih gagal mendapatkan tabel setelah login ulang. Server mungkin sedang down.")
                return []

        results = []
        rows = tbody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6 and not row.get('class'):
                matkul_cell = cols[2]
                for badge in matkul_cell.find_all('span', class_='badge'):
                    badge.decompose()
                matkul = matkul_cell.get_text(strip=True)
                
                col_nilai = cols[4]
                col_mutu = cols[5]
                
                is_placeholder = "placeholder" in str(col_nilai)
                is_empty = not col_nilai.get_text(strip=True)
                
                results.append({
                    "matkul": matkul,
                    "nilai": "---" if (is_placeholder or is_empty) else col_nilai.get_text(strip=True),
                    "mutu": "---" if (is_placeholder or is_empty) else col_mutu.get_text(strip=True)
                })
        return results

    except Exception as e:
        print(f"❌ Error serius di get_data: {e}")
        return []

def monitor():
    """
    Loop utama monitoring.
    1. Login ke sistem.
    2. Cek data nilai secara berkala (sesuai INTERVAL).
    3. Bandingkan dengan data lama (last_values.json).
    4. Kirim notifikasi jika ada perubahan.
    """
    print("🚀 Monitoring Siakang Dimulai...")
    send_telegram("🤖 Bot Monitoring Siakang Aktif!") 
    
    if not do_login():
        print("❌ Login awal gagal. Hentikan script.")
        return

    while True:
        try:
            current_data = get_data()
            
            next_check = time.strftime('%H:%M:%S', time.localtime(time.time() + INTERVAL))
            
            if not current_data:
                print(f"⚠️ Data kosong. Akan dicoba lagi pada: {next_check}")
            elif os.path.exists(FILE_DATA):
                with open(FILE_DATA, "r") as f:
                    old_data = json.load(f)
                
                changes = []
                for cur, old in zip(current_data, old_data):
                    if old['nilai'] != cur['nilai']:
                        msg = (f"🔔 *NILAI KELUAR!*\n\n"
                                f"📚 *Matkul:* {cur['matkul']}\n"
                                f"📊 *Nilai:* `{cur['nilai']}`\n"
                                f"✨ *Mutu:* `{cur['mutu']}`\n\n"
                                f"Cek di: [Siakang Untirta]({URL_TARGET})")
                        changes.append(msg)
                
                if changes:
                    for change in changes:
                        send_telegram(change)
                    print(f"✅ Terdeteksi {len(changes)} perubahan nilai! (Cek lagi: {next_check})")
                else:
                    print(f"😴 Tidak ada perubahan. (Terakhir: {time.strftime('%H:%M:%S')} | Berikutnya: {next_check})")
            
            if current_data:
                with open(FILE_DATA, "w") as f:
                    json.dump(current_data, f, indent=4)
                
        except Exception as e:
            print(f"❌ Error di loop monitor: {e}")
            
        time.sleep(INTERVAL)

if __name__ == "__main__":
    monitor()