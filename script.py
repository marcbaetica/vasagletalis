import ftplib
import os
import requests


    # Citește credențialele din variabilele de mediu


    session = requests.Session()
    session.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/135.0.0.0 Safari/537.36")
    })

    # -------------------------------
    # PASUL A: LOGIN
    # -------------------------------
    login_url = "https://eu.distributor.songmics.com/api/account/login"
    payload = {"email": vasagle_email, "password": vasagle_pass}
    r_login = session.post(login_url, json=payload)
    r_login.raise_for_status()
    print("Login efectuat cu succes.")

    # Extrage cookie-urile importante
    token_cookie = session.cookies.get("token")
    ziel_cookie = session.cookies.get("ziel_distributor_system_eu_session")
    print("Token cookie:", token_cookie)
    print("Cookie 'ziel_distributor_system_eu_session':", ziel_cookie)

    # -------------------------------
    # PASUL B: DESCĂRCARE FIȘIER (export)
    # -------------------------------
    export_url = "https://eu.distributor.songmics.com/api/account/exportStock"
    # Construiește header-ele exact cum apare în cURL-ul original
    export_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ro;q=0.8,hu;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Content-Length": "0",
        "Origin": "https://eu.distributor.songmics.com",
        "Referer": "https://eu.distributor.songmics.com/account",
        "User-Agent": session.headers.get("User-Agent"),
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "token": token_cookie if token_cookie else ""
    }
    # Construiți header-ul Cookie exact, la fel ca în cURL:
    if token_cookie and ziel_cookie:
        export_headers["Cookie"] = f"ziel_distributor_system_eu_session={ziel_cookie}; token={token_cookie}"
    
    # Trimite cererea POST fără corp (data = "" pentru a forța Content-Length 0)
    r_export = session.post(export_url, headers=export_headers, data="")
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

    # -------------------------------
    # PASUL C: URCARE PE FTP ȘI ÎNLOCUIREA FIȘIERULUI EXISTENT
    # -------------------------------
    ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)
    ftp.cwd("Vasagle")
    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi a fost șters.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi:", e)
    with open("vasaglestock.xlsx", "rb") as file:
        ftp.storbinary("STOR vasaglestock_temp.xlsx", file)
    print("Fișierul a fost uploadat ca 'vasaglestock_temp.xlsx'.")
    try:
        ftp.delete("vasaglestock.xlsx")
        print("Fișierul vechi (fallback) a fost șters.")
    except Exception as e:
        print("Nu s-a putut șterge fișierul vechi în fallback:", e)
    ftp.rename("vasaglestock_temp.xlsx", "vasaglestock.xlsx")
    print("Fișierul temporar a fost redenumit în 'vasaglestock.xlsx'.")
    ftp.quit()
    print("Fișierul 'vasaglestock.xlsx' a fost urcat cu succes pe FTP.")

if __name__ == "__main__":
    main()
