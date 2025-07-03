import psutil, time, win32serviceutil
from psutil import NoSuchProcess

# Durdurulacak hizmetler
SERVICES = [
    "DiagTrack","WSearch","SysMain",
    "WpnUserService","XblAuthManager",
    "XboxNetApiSvc","PcaSvc","WaaSMedicSvc","DmEnrollmentSvc"
]

# Öldürülecek süreçler
PROCS = [
    "OneDrive.exe","Teams.exe","Cortana.exe",
    "SkypeApp.exe","YourPhone.exe","People.exe"
]

def boost(log_callback=print):
    log = log_callback

    # Başlangıç boş RAM
    before = psutil.virtual_memory().available // (1024**2)
    log(f"🔧 Game Booster başladı — Boş RAM: {before} MB\n")

    # 1) Hizmetleri durdur
    stopped = []
    log("🛑 Hizmetler durduruluyor...")
    for svc in SERVICES:
        try:
            win32serviceutil.StopService(svc)
            stopped.append(svc)
            log(f"  • Durduruldu: {svc}")
        except Exception as e:
            log(f"  • Atlandı: {svc} ({e})")

    # 2) Süreçleri öldür
    killed = []
    log("\n💀 Gereksiz süreçler sonlandırılıyor...")
    for p in psutil.process_iter():
        try:
            name = p.name()
            if name in PROCS:
                p.kill()
                killed.append(name)
                log(f"  • Sonlandırıldı: {name}")
        except NoSuchProcess:
            pass
        except Exception as e:
            log(f"  • Hata ({name}): {e}")

    # 3) Serbest kalan RAM
    time.sleep(1)
    after = psutil.virtual_memory().available // (1024**2)
    freed = after - before
    log(f"\n✅ İşlem tamamlandı — Serbest kalan RAM: {freed} MB")
    log(f"Hizmetler: {len(stopped)} durduruldu ({', '.join(stopped)})")
    log(f"Süreçler: {len(killed)} sonlandırıldı ({', '.join(killed)})")