import os, shutil, glob, ctypes

def _clean_path(path, log):
    if not os.path.exists(path):
        log(f"Yol bulunamadı: {path}")
        return
    log(f"[✔] Temizleniyor: {path}")
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:    os.remove(fp)
            except Exception as e: log(f"  • Hata silerken {fp}: {e}")
        for d in dirs:
            dp = os.path.join(root, d)
            try:    shutil.rmtree(dp)
            except Exception as e: log(f"  • Hata silerken {dp}: {e}")
    log(f"[✔] Tamamlandı: {path}")

def clean(log_callback=print):
    log = log_callback
    log("=== Detaylı Temizleyici Başlıyor ===\n")

    # %TEMP% ve %TMP%
    for var in ("TEMP","TMP"):
        temp = os.getenv(var)
        if temp: _clean_path(temp, log)

    # Windows Temp
    _clean_path(r"C:\Windows\Temp", log)

    # Tarayıcı önbellekleri
    user = os.getenv("USERNAME") or os.getenv("USER")
    patterns = [
        rf"C:\Users\{user}\AppData\Local\Google\Chrome\User Data\Default\Cache",
        rf"C:\Users\{user}\AppData\Local\Mozilla\Firefox\Profiles\*\cache2",
        rf"C:\Users\{user}\AppData\Local\Microsoft\Edge\User Data\Default\Cache"
    ]
    for pat in patterns:
        for p in glob.glob(pat):
            _clean_path(p, log)

    # Uygulama cache’leri
    local = os.getenv("LOCALAPPDATA")
    if local:
        for app in os.listdir(local):
            cdir = os.path.join(local, app, "Cache")
            if os.path.isdir(cdir):
                _clean_path(cdir, log)

    # Çöp kutusu
    log("\n[✔] Çöp kutusu temizleniyor...")
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(
            None, None, 0x00000001|0x00000002|0x00000004
        )
        log("[✔] Çöp kutusu temizlendi.")
    except Exception as e:
        log(f"[!] Çöp kutusu temizlenemedi: {e}")

    log("\n=== Detaylı Temizleyici Tamamlandı ===")