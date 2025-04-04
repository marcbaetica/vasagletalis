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

    # ------------------------------------------------
    # PASUL A: LOGIN folosind endpoint-ul corect
    # ------------------------------------------------
    login_url = "https://eu.distributor.songmics.com/api/account/login"
    payload = {
        "email": vasagle_email,
        "password": vasagle_pass
    }
    r_login = session.post(login_url, json=payload)
    r_login.raise_for_status()  # Verifică că login-ul a fost efectuat cu succes
    print("Login efectuat cu succes:", r_login.status_code)

    # ------------------------------------------------
    # PASUL B: Extrage token-ul din cookie și setează-l ca header
    # ------------------------------------------------
    token_cookie = session.cookies.get("token")
    if token_cookie:
        session.headers.update({"token": token_cookie})
        print("Header-ul 'token' a fost setat la:", token_cookie)
    else:
        print("Tokenul nu a fost găsit în cookie-uri.")

    # ------------------------------------------------
    # PASUL C: DESCĂRCARE FIȘIER
    # ------------------------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"
    r_export = session.post(export_url)
    r_export.raise_for_status()

    # Salvează conținutul fișierului ca "vasaglestock.xlsx"
    with open("vasaglestock.xlsx", "wb") as f:
        f.write(r_export.content)
    print("Fișierul a fost descărcat și salvat ca 'vasaglestock.xlsx'.")

    # ------------------------------------------------
    # PASUL D: URCARE PE FTP
    # ------------------------------------------------
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")  # Navighează în folderul "Vasagle"

    with open("vasaglestock.xlsx", "rb") as file:
        ftp.storbinary("STOR vasaglestock.xlsx", file)
    ftp.quit()
    print("Fișierul 'vasaglestock.xlsx' a fost urcat cu succes pe FTP.")

if __name__ == "__main__":
    main()
