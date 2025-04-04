import os
import requests
import ftplib

def main():
    # Citește credențialele din variabilele de mediu
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
        "token": token_cookie
    }

    r_export = session.post(export_url, headers=export_headers)
    try:
        r_export.raise_for_status()
    except Exception as e:
        print("Eroare la export:", e)
        print("Conținutul răspunsului:", r_export.text)
        return

    # Verifică dacă răspunsul este fișier Excel
    content_type = r_export.headers.get("content-type", "")
    if "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" not in content_type:
        print("Content-Type neașteptat:", content_type)
        print("Previzualizare răspuns:", r_export.content[:500])
        return

    with open("vasaglestock.xlsx", "wb") as f:
        f.write(r_export.content)
    print("Fișierul a fost descărcat și salvat ca 'vasaglestock.xlsx'.")

    # ------------------------------------------------
    # PASUL C: URCARE PE FTP ȘI ÎNLOCUIREA FIȘIERULUI EXISTENT
    # ------------------------------------------------
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")

    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi a fost șters.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi:", e)

    # Urcă fișierul cu nume temporar
    with open("vasaglestock.xlsx", "rb") as file:
        ftp.storbinary("STOR vasaglestock_temp.xlsx", file)
    print("Fișierul a fost uploadat ca 'vasaglestock_temp.xlsx'.")

    # Încercăm din nou să ștergem fișierul existent (dacă ar fi rămas)
    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi (fallback) a fost șters.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi în fallback:", e)

    # Redenumește fișierul temporar
    ftp.rename("vasaglestock_temp.xlsx", "vasaglestock.xlsx")
    print("Fișierul temporar a fost redenumit în 'vasaglestock.xlsx'.")

    ftp.quit()
    print("Fișierul 'vasaglestock.xlsx' a fost urcat cu succes pe FTP.")

if __name__ == "__main__":
    main()
