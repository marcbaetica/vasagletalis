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
    r_login.raise_for_status()  # Aruncă excepție dacă login-ul eșuează
    print("Login efectuat cu succes.")

    # ------------------------------------------------
    # PASUL B: DESCĂRCARE FIȘIER
    # ------------------------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"
    r_export = session.post(export_url)
    r_export.raise_for_status()

    # Salvează fișierul ca "vasaglestock.xlsx"
    with open("vasaglestock.xlsx", "wb") as f:
        f.write(r_export.content)
    print("Fișierul a fost descărcat și salvat ca 'vasaglestock.xlsx'.")

    # ------------------------------------------------
    # PASUL C: URCARE PE FTP ȘI ÎNLOCUIREA FIȘIERULUI EXISTENT
    # ------------------------------------------------
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")  # Navighează în folderul "Vasagle"

    # Încearcă să ștergi fișierul existent
    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi a fost șters.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi (posibil nu există sau nu permite ștergerea):", e)

    # Încărcare fișier cu nume temporar
    with open("vasaglestock.xlsx", "rb") as file:
        ftp.storbinary("STOR vasaglestock_temp.xlsx", file)
    print("Fișierul a fost uploadat ca 'vasaglestock_temp.xlsx'.")

    # Încearcă din nou să ștergi fișierul vechi, dacă există
    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi (dacă era prezent) a fost șters în etapa de fallback.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi în etapa de fallback:", e)

    # Redenumește fișierul temporar în numele final
    ftp.rename("vasaglestock_temp.xlsx", "vasaglestock.xlsx")
    print("Fișierul temporar a fost redenumit în 'vasaglestock.xlsx'.")

    ftp.quit()
    print("Fișierul 'vasaglestock.xlsx' a fost urcat cu succes pe FTP (înlocuind fișierul vechi).")

if __name__ == "__main__":
    main()
