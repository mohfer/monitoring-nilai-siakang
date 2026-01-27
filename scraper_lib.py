"""Scraper Library untuk Siakang Untirta.

Library ini menyediakan class SiakangScraper untuk interaksi dengan sistem Siakang.

Fungsi Utama:
- Login ke sistem Siakang Untirta dengan validasi kredensial
- Mengambil daftar semester yang tersedia dengan pagination support

Fitur:
- Session Management: Mengelola cookie dan session login
- IPv4 Enforcement: Memaksa koneksi menggunakan IPv4 untuk menghindari timeout
- Pagination Support: Mendukung pengambilan data dari multiple pages

Digunakan oleh:
- server/main.py: Untuk validasi login dan fetch semester di API endpoint
- main.py: Socket patch dijalankan saat import untuk memperbaiki koneksi
"""

import requests
from bs4 import BeautifulSoup
import socket

orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4

class SiakangScraper:
    def __init__(self, login_id, password):
        self.login_id = login_id
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.url_login = "https://siakang.untirta.ac.id/auth/login"
        self.url_list_semester = "https://siakang.untirta.ac.id/dashboard/list-semester"

    def login(self):
        try:
            res_page = self.session.get(self.url_login)
            soup = BeautifulSoup(res_page.text, 'html.parser')
            
            csrf_token_el = soup.find('input', {'name': '_token'})
            if not csrf_token_el:
                return False, "CSRF token not found"
                
            login_data = {
                '_token': csrf_token_el['value'],
                'email': self.login_id,
                'username': self.login_id,
                'password': self.password
            }
            
            response = self.session.post(self.url_login, data=login_data)
            if response.ok:
                if "Identitas tersebut tidak cocok dengan data kami" in response.text:
                    return False, "Identitas Salah"
                return True, "Success"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def get_semesters(self):
        """Mengambil semua daftar semester dengan pagination support.
        
        Returns:
            list: List of dict dengan keys 'title', 'code', dan 'url'
        """
        semesters = []
        current_url = self.url_list_semester
        
        while current_url:
            try:
                res = self.session.get(current_url)
                if res.status_code != 200:
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
                    
                    if title and code:
                        semesters.append({
                            'title': title,
                            'code': code,
                            'url': url
                        })

                next_link = soup.find('a', rel='next')
                if next_link and next_link.has_attr('href'):
                    current_url = next_link['href']
                else:
                    current_url = None
            except Exception as e:
                break
        return semesters
