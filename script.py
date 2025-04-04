import os
import requests
import ftplib

def main():
    # Citește credențialele din variabilele de mediu (setate ca secrete în GitHub)
    vasagle_email = os.getenv("VASAGLE_EMAIL")
    vasagle_pass = os.getenv("VASAGLE_PASSWORD")
    ftp_host = os.getenv("FTP_HOST")
    ftp_user = os.getenv("FTP_USER")
    ftp_pass = os.getenv("FTP_PASS")

    # Creează o sesiune requests pentru a păstra cookie-urile
    session = requests.Session()

    # Setează un User-Agent pentru a imita browserul
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    })

    # ------------------------------------------------
    # PASUL A: LOGIN
    # ------------------------------------------------
    login_url = "https://eu.distributor.songmics.com/api/account/login"
    payload = {
        "email": vasagle_email,
        "password": vasagle_pass
    }
    r_login = session.post(login_url, json=payload)
    r_login.raise_for_status()
    print("Login efectuat cu succes.")

    # Extrage token-ul din cookie și setează-l ca header
    token_cookie = session.cookies.get("token")
    if token_cookie:
        session.headers.update({"token": token_cookie})
        print("Token header set:", token_cookie)
    else:
        print("Token cookie nu a fost găsit!")
    
    # ------------------------------------------------
    # PASUL B: DESCĂRCARE FIȘIER cu header-ele de export
    # ------------------------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"
    export_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.8,hu;q=0.7",
        "Origin": "https://eu.distributor.songmics.com",
        "Referer": "https://eu.distributor.songmics.com/account",
        "User-Agent": session.headers.get("User-Agent"),
        "token": token_cookie,
        "Content-Length": "0"
    }

    # Trimite o cerere POST cu un corp gol
    r_export = session.post(export_url, headers=export_headers, data="")

    try:
        r_export.raise_for_status()
    except Exception as e:
        print("Eroare la export:", e)
        print("Conținutul
