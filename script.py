import os
import requests
import ftplib
import re

def main():
    # 1) Citește credențialele din variabilele de mediu (secrete GitHub)
    vasagle_email = os.getenv("VASAGLE_EMAIL")
    vasagle_pass = os.getenv("VASAGLE_PASSWORD")
    ftp_host = os.getenv("FTP_HOST")
    ftp_user = os.getenv("FTP_USER")
    ftp_pass = os.getenv("FTP_PASS")

    # 2) Creează o sesiune requests pentru menținerea cookie-urilor
    session = requests.Session()

    # ------------------------------------------------
    # PASUL A: LOGIN
    # ------------------------------------------------
    login_url = "https://eu.distributor.songmics.com/login"
    # Unele site-uri cer și un token CSRF. Dacă da, îl extragi din HTML (ex: <input name="_token" value="...">).
    # Exemplu (dacă e Laravel):
    #
    #   r_login_page = session.get(login_url)
    #   # parse HTML cu regex sau BeautifulSoup
    #   csrf_token = re.search(r'name="_token" value="([^"]+)"', r_login_page.text).group(1)
    #
    # Apoi la post data includem `_token: csrf_token`.
    #
    # Pentru un site simplu, poate e suficient:
    payload = {
        "email": vasagle_email,
        "password": vasagle_pass
    }
    # Trimite datele de login
    r_login = session.post(login_url, data=payload)
    r_login.raise_for_status()

    # Verificăm dacă suntem logați, de exemplu că nu ne redirecționează la /login
    if "login" in r_login.url.lower():
        raise Exception("Login a eșuat. Verifică dacă e nevoie de token CSRF sau parametri suplimentari.")

    # ------------------------------------------------
    # PASUL B: DESCĂRCARE FIȘIER
    # ------------------------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"
    # Endpoint-ul menționat. Este un POST care returnează direct fișierul Excel
    r_export = session.post(export_url)
    r_export.raise_for_status()

    # Salvează fișierul ca vasaglestock.xlsx
    # (Poți să verifici header-ul content-disposition dacă vrei să detectezi numele original)
    with open("vasaglestock.xlsx", "wb") as f:
        f.write(r_export.content)

    print("Fișierul a fost descărcat și salvat local ca vasaglestock.xlsx.")

    # ------------------------------------------------
    # PASUL C: URCARE PE FTP
    # ------------------------------------------------
    # Ne conectăm la FTP, mergem în folderul "Vasagle", încărcăm fișierul
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")  # intră în folderul "Vasagle"

    # Deschidem fișierul local și îl trimitem pe server
    with open("vasaglestock.xlsx", "rb") as file:
        # "STOR vasaglestock.xlsx" -> suprascrie fișierul dacă există deja
        ftp.storbinary("STOR vasaglestock.xlsx", file)

    ftp.quit()
    print("Fișierul vasaglestock.xlsx a fost urcat cu succes în folderul Vasagle de pe FTP.")

if __name__ == "__main__":
    main()
