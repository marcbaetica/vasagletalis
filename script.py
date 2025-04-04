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
    # Trimite request-ul POST cu payload-ul JSON
    r_login = session.post(login_url, json=payload)
    r_login.raise_for_status()  # Dacă login-ul eșuează, se va arunca o excepție

    print("Login efectuat cu succes.")
    
    # Acum, cookie-urile (de ex. token și ziel_distributor_system_eu_session) sunt setate în sesiune

    # ------------------------------------------------
    # PASUL B: DESCĂRCARE FIȘIER
    # ------------------------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"
    r_export = session.post(export_url)
    r_export.raise_for_status()

    # Salvează fișierul ca vasaglestock.xlsx
    with open("vasaglestock.xlsx", "wb") as f:
        f.write(r_export.content)
    print("Fișierul a fost descărcat și salvat ca 'vasaglestock.xlsx'.")

    # ------------------------------------------------
    # PASUL C: URCARE PE FTP ȘI ÎNLOCUIREA FIȘIERULUI EXISTENT
    # ------------------------------------------------
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")  # Schimbă directorul în folderul "Vasagle"
    
    # Șterge fișierul existent dacă există
    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi a fost șters.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi sau nu există:", e)
    
    # Urcă fișierul nou pe FTP
    with open("vasaglestock.xlsx", "rb") as file:
        ftp.storbinary("STOR vasaglestock.xlsx", file)
    ftp.quit()
    print("Fișierul 'vasaglestock.xlsx' a fost urcat cu succes pe FTP.")

if __name__ == "__main__":
    main()
