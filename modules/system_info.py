import platform
import psutil
import socket

def show_info(log_callback=print):
    log = log_callback
    log("=== Sistem Bilgisi ===\n")

    # İşletim Sistemi
    uname = platform.uname()
    log(f"OS       : {uname.system} {uname.release} ({uname.version})")
    log(f"Mimari   : {uname.machine}\n")

    # CPU Bilgileri
    phys = psutil.cpu_count(logical=False)
    total = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    log(f"CPU Çekirdek  : Fiziksel={phys}, Mantıksal={total}")
    if freq:
        log(f"CPU Frekans   : {freq.current:.2f}MHz (min={freq.min:.2f}, max={freq.max:.2f})")

    # Bellek
    mem = psutil.virtual_memory()
    log(f"\nRAM Toplam    : {mem.total // (1024**2)} MB")
    log(f"RAM Kullanılan: {mem.used  // (1024**2)} MB")
    log(f"RAM Boş       : {mem.available // (1024**2)} MB")

    # Takas (Swap)
    swap = psutil.swap_memory()
    log(f"\nSwap Toplam   : {swap.total // (1024**2)} MB")
    log(f"Swap Kullanılan: {swap.used // (1024**2)} MB")

    # Disk Bölümleri
    log("\nDisk Bölümleri:")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            log(f"  • {part.device} @ {part.mountpoint} → "
                f"{usage.total//(1024**3)} GB (Kullanılan: {usage.used//(1024**3)} GB, "
                f"Boş: {usage.free//(1024**3)} GB, Tip: {part.fstype})")
        except PermissionError:
            log(f"  • {part.device} @ {part.mountpoint} → erişim reddedildi")

    # Ağ Arayüzleri
    log("\nAğ Arayüzleri (IPv4):")
    for iface, addrs in psutil.net_if_addrs().items():
        for snic in addrs:
            if snic.family == socket.AF_INET:
                log(f"  • {iface}: {snic.address}")

    log("\n=== Sistem Bilgisi Sonu ===")