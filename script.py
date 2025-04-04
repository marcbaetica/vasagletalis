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

    # Creează o sesiune requests
    session = requests.Session()

    # Setează un User-Agent similar cu cel din browser
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
    print("Login efectuat cu succes, status code:", r_login.status_code)

    # Verificăm și afișăm cookie-urile primite
    token_cookie = session.cookies.get("token")
    ziel_cookie = session.cookies.get("ziel_distributor_system_eu_session")
    print("Cookie token:", token_cookie)
    print("Cookie ziel_distributor_system_eu_session:", ziel_cookie)

    # Dacă token-ul nu a fost extras, nu putem continua
    if not token_cookie or not ziel_cookie:
        raise Exception("Cookie-urile de autentificare nu au fost setate corect.")

    # ------------------------------------------------
    # PASUL B: DESCĂRCARE FIȘIER cu header-e mimice din browser
    # ------------------------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"

    # Setăm header-ele conform cererii cURL din browser
    export_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.8,hu;q=0.7",
        "Origin": "https://eu.distributor.songmics.com",
        "Referer": "https://eu.distributor.songmics.com/account",
        "token": token_cookie  # Folosim token-ul extras
    }
    r_export = session.post(export_url, headers=export_headers)
    r_export.raise_for_status()

    # Verificăm dacă răspunsul pare a fi un fișier Excel (content-type)
    if "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" not in r_export.headers.get("content-type", ""):
        print("Răspunsul la export nu pare a fi un fișier Excel. Conținutul este:")
        print(r_export.text)
        raise Exception("Exportul nu a returnat fișierul așteptat.")

    # Salvează conținutul fișierului ca "vasaglestock.xlsx"
    with open("vasaglestock.xlsx", "wb") as f:
        f.write(r_export.content)
    print("Fișierul a fost descărcat și salvat ca 'vasaglestock.xlsx'.")

    # ------------------------------------------------
    # PASUL C: URCARE PE FTP
    # ------------------------------------------------
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")
    with open("vasaglestock.xlsx", "rb") as file:
        ftp.storbinary("STOR vasaglestock.xlsx", file)
    ftp.quit()
    print("Fișierul 'vasaglestock.xlsx' a fost urcat cu succes pe FTP.")

if __name__ == "__main__":
    main()
