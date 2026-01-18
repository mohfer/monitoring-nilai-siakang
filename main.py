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
import sys
from dotenv import load_dotenv
import socket
import builtins
from datetime import datetime

def print(*args, **kwargs):
    now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    builtins.print(f"{now}", *args, **kwargs)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

URL_LOGIN = os.getenv("URL_LOGIN")
URL_TARGET = os.getenv("URL_TARGET")
URL_LIST_SEMESTER = os.getenv("URL_LIST_SEMESTER")
LOGIN_ID = os.getenv("LOGIN_ID")
PASSWORD = os.getenv("PASSWORD")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

FILE_DATA = os.getenv("FILE_DATA")
INTERVAL = int(os.getenv("INTERVAL", 300))
TARGET_SEMESTER_CODE = os.getenv("TARGET_SEMESTER_CODE")

SELECTED_SEMESTER_URL = None

orig_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = getaddrinfo_ipv4

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
    
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            response.raise_for_status() 
            return
            
        except requests.exceptions.Timeout:
            print(f"⏳ Timeout pada percobaan {attempt+1}/3. Mencoba lagi...")
        except requests.exceptions.ConnectionError:
            print(f"🌐 Masalah koneksi/Reset pada percobaan {attempt+1}/3. Mencoba lagi...")
        except Exception as e:
            print(f"⚠️ Gagal kirim Telegram (Percobaan {attempt+1}/3): {e}")
        
        if attempt < 2:
            time.sleep(5)
    
    print("❌ Gagal kirim Telegram setelah 3 kali percobaan.")

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
            if "Identitas tersebut tidak cocok dengan data kami" in response.text:
                print("❌ Login gagal: Identitas (NIM/Password) salah.")
                return False
                
            print("✅ Login berhasil.")
            if SELECTED_SEMESTER_URL:
                print("🔄 Mengaktifkan kembali semester terpilih...")
                try:
                    session.get(SELECTED_SEMESTER_URL)
                    print("✅ Semester berhasil diaktifkan ulang.")
                except Exception as e:
                    print(f"⚠️ Gagal mengaktifkan ulang semester: {e}")
            return True
    except Exception as e:
        print(f"❌ Error saat login: {e}")
    return False

def get_all_semesters():
    """Mengambil semua daftar semester yang tersedia dengan pagination."""
    print("🔄 Mengambil daftar semester...")
    semesters = []
    current_url = URL_LIST_SEMESTER
    
    while current_url:
        try:
            res = session.get(current_url)
            if res.status_code != 200:
                print(f"⚠️ Gagal akses list semester: {res.status_code}")
                break

            soup = BeautifulSoup(res.text, 'html.parser')
            
            cards = soup.find_all('div', class_='col-12 col-md-6 col-lg-4')
            for card in cards:
                title_elm = card.find('h5', class_='card-title')
                if not title_elm: continue
                
                title = title_elm.get_text(strip=True)
                
                code_elm = card.find('p', class_='card-text')
                code = code_elm.get_text(strip=True).replace("Kode Semester #", "") if code_elm else ""
                
                link_elm = card.find('a', class_='btn-primary')
                url = link_elm['href'] if link_elm else None
                
                if title and url:
                    semesters.append({
                        'title': title,
                        'code': code,
                        'url': url
                    })

            next_link = soup.find('a', rel='next')
            if next_link and next_link.has_attr('href'):
                current_url = next_link['href']
                if not current_url.startswith('http'):
                    pass
            else:
                current_url = None
                
        except Exception as e:
            print(f"⚠️ Error parsing list semester: {e}")
            break
            
    return semesters

def get_data():
    """Mengambil data nilai menggunakan session yang ada."""
    try:
        res = session.get(URL_TARGET)
        
        if res.status_code != 200:
            print(f"⚠️ Server Kampus memberikan respon tidak normal: {res.status_code}")
            return []

        soup_target = BeautifulSoup(res.text, 'html.parser')

        try:
            hitung_ips_link = None
            for a_tag in soup_target.find_all('a'):
                if "Hitung IPS" in a_tag.get_text():
                    hitung_ips_link = a_tag['href']
                    break
            
            if hitung_ips_link:
                print("🔄 Menjalankan proses Hitung IPS...")
                session.get(hitung_ips_link)
                res = session.get(URL_TARGET)
                soup_target = BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            print(f"⚠️ Gagal menjalankan Hitung IPS: {e}")

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
        total_sks = 0
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 6 and not row.get('class'):
                matkul_cell = cols[2]
                
                sks_val = 0
                for badge in matkul_cell.find_all('span', class_='badge'):
                    badge_text = badge.get_text(strip=True)
                    if "SKS" in badge_text:
                        try:
                            sks_val = int(badge_text.replace("SKS", "").strip())
                        except:
                            pass
                    badge.decompose()
                
                total_sks += sks_val
                matkul = matkul_cell.get_text(strip=True)
                
                col_nilai = cols[4]
                col_mutu = cols[5]
                
                is_placeholder = "placeholder" in str(col_nilai)
                is_empty = not col_nilai.get_text(strip=True)
                
                results.append({
                    "matkul": matkul,
                    "sks": sks_val,
                    "nilai": "---" if (is_placeholder or is_empty) else col_nilai.get_text(strip=True),
                    "mutu": "---" if (is_placeholder or is_empty) else col_mutu.get_text(strip=True)
                })

        ip_val = "-"
        ipk_val = "-"
        try:
            for p in soup_target.find_all('p'):
                text = p.get_text(strip=True)
                if "IP :" in text and "IPK" not in text:
                    ip_val = text.split(":")[-1].strip()
                elif "IPK :" in text:
                    ipk_val = text.split(":")[-1].strip()
        except Exception as e:
            print(f"⚠️ Gagal parsing IP/IPK: {e}")
        
        user_name = "-"
        user_nim = LOGIN_ID
        
        try:
            name_elem = soup_target.select_one('.pro-user-name')
            if name_elem:
                full_text = name_elem.get_text(strip=True)
                user_name = full_text
            else:
                user_box_name = soup_target.select_one('.user-box .dropdown-toggle')
                if user_box_name:
                    user_name = user_box_name.get_text(strip=True)
                    
            user_name = user_name.replace("", "").strip()
                
        except Exception as e:
            print(f"⚠️ Gagal parsing Nama User: {e}")

        final_data = {
            "nama": user_name,
            "nim": user_nim,
            "ips": ip_val,
            "ipk": ipk_val,
            "total_sks": total_sks,
            "nilai": results
        }

        return final_data

    except Exception as e:
        print(f"❌ Error serius di get_data: {e}")
        return None

def monitor():
    """
    Loop utama monitoring.
    1. Login ke sistem.
    2. Pilih semester (User Input) -> Set SELECTED_SEMESTER_URL.
    3. Cek data nilai secara berkala (sesuai INTERVAL).
    4. Bandingkan dengan data lama (last_values.json).
    5. Kirim notifikasi jika ada perubahan.
    """
    global SELECTED_SEMESTER_URL
    print("🚀 Monitoring Siakang Dimulai...")
    
    if not do_login():
        print("❌ Login awal gagal. Hentikan script.")
        return

    semesters = get_all_semesters()
    if not semesters:
        print("❌ Tidak dapat menemukan daftar semester. Menggunakan default sistem.")
    else:
        selected = None
        
        if TARGET_SEMESTER_CODE:
            print(f"⚙️ Mencari semester dengan kode konfigurasi: {TARGET_SEMESTER_CODE}")
            for sem in semesters:
                if sem['code'] == TARGET_SEMESTER_CODE:
                    selected = sem
                    break
            
            if not selected:
                print(f"❌ Semester dengan kode '{TARGET_SEMESTER_CODE}' tidak ditemukan dalam daftar.")
        
        if not selected:
            print("\n📋 Daftar Semester Tersedia:")
            for idx, sem in enumerate(semesters):
                print(f"{idx+1}. {sem['title']} (Kode: {sem['code']})")
                
            while True:
                try:
                    choice = int(input("\n👉 Pilih nomor semester yang ingin dipantau: "))
                    if 1 <= choice <= len(semesters):
                        selected = semesters[choice-1]
                        break
                    else:
                        print("🚫 Pilihan tidak valid.")
                except ValueError:
                    print("🚫 Masukkan angka.")
        
        if selected:
            SELECTED_SEMESTER_URL = selected['url']
            print(f"✅ Memilih: {selected['title']}")
            print("🔄 Mengaktifkan semester...")
            session.get(SELECTED_SEMESTER_URL)

    send_telegram("🤖 Bot Monitoring Siakang Aktif!") 

    while True:
        old_data = None
        try:
            current_data = get_data()
            
            next_check = time.strftime('%H:%M:%S', time.localtime(time.time() + INTERVAL))
            
            if not current_data:
                print(f"⚠️ Data kosong atau gagal diambil. Akan dicoba lagi pada: {next_check}")
            elif os.path.exists(FILE_DATA):
                try:
                    with open(FILE_DATA, "r") as f:
                        old_data = json.load(f)
                except Exception:
                    old_data = None
                
                old_courses = []
                if isinstance(old_data, list):
                     old_courses = old_data
                elif isinstance(old_data, dict):
                     old_courses = old_data.get('nilai', [])

                current_courses = current_data.get('nilai', [])

                changes = []
                for cur, old in zip(current_courses, old_courses):
                    if old['nilai'] != cur['nilai']:
                        msg = (f"🔔 *NILAI KELUAR!*\n\n"
                                f"📚 *Matkul:* {cur['matkul']}\n"
                                f"📊 *Nilai:* `{cur['nilai']}`\n"
                                f"✨ *Mutu:* `{cur['mutu']}`\n\n"
                                f"Cek di: [Siakang Untirta]({URL_TARGET})")
                        changes.append(msg)
                
                if isinstance(old_data, dict):
                    if old_data.get('ips') != current_data.get('ips') and current_data.get('ips') != "-":
                         changes.append(f"📈 *IPS Berubah*: {old_data.get('ips')} -> {current_data.get('ips')}")
                    if old_data.get('ipk') != current_data.get('ipk') and current_data.get('ipk') != "-":
                         changes.append(f"📈 *IPK Berubah*: {old_data.get('ipk')} -> {current_data.get('ipk')}")

                if changes:
                    for change in changes:
                        send_telegram(change)
                    print(f"✅ Terdeteksi {len(changes)} perubahan nilai! (Cek lagi: {next_check})")
                else:
                    print(f"😴 Tidak ada perubahan. (Terakhir: {time.strftime('%H:%M:%S')} | Berikutnya: {next_check})")
            
            if current_data:
                current_courses = current_data.get('nilai', [])
                is_complete = all(d['nilai'] != "---" for d in current_courses)
                
                was_complete = False
                if old_data:
                     old_courses = old_data if isinstance(old_data, list) else old_data.get('nilai', [])
                     was_complete = all(d['nilai'] != "---" for d in old_courses)
                
                if is_complete and not was_complete:
                    msg_complete = (f"🎉 *SEMUA NILAI SUDAH KELUAR!*\n\n"
                                    f"👤 *{current_data.get('nama')}*\n"
                                    f"📈 *IPS:* {current_data.get('ips')} | *IPK:* {current_data.get('ipk')}\n"
                                    f"Silakan cek portal Siakang untuk detail lengkap.\n"
                                    f"[Login Siakang]({URL_TARGET})")
                    send_telegram(msg_complete)
                    print("✅ Notifikasi semua nilai keluar telah dikirim!")

            if current_data:
                with open(FILE_DATA, "w") as f:
                    json.dump(current_data, f, indent=4)
                
        except Exception as e:
            print(f"❌ Error di loop monitor: {e}")
            import traceback
            traceback.print_exc()
            
        time.sleep(INTERVAL)

if __name__ == "__main__":
    monitor()