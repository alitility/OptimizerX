# modules/ggpu_info.py

import subprocess
import time
import psutil
from psutil import NoSuchProcess
from subprocess import CREATE_NO_WINDOW

# 1) NVML (NVIDIA) denemesi
try:
    from pynvml import (
        nvmlInit, nvmlShutdown,
        nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetName, nvmlDeviceGetTemperature,
        nvmlDeviceGetFanSpeed, nvmlDeviceGetMemoryInfo,
        nvmlDeviceGetUtilizationRates, nvmlDeviceGetClockInfo,
        NVML_TEMPERATURE_GPU, NVML_CLOCK_GRAPHICS, NVML_CLOCK_MEM
    )
    nvmlInit()
    HAS_NVML    = True
    NV_COUNT    = nvmlDeviceGetCount()
    NV_HANDLES  = [nvmlDeviceGetHandleByIndex(i) for i in range(NV_COUNT)]
except Exception:
    HAS_NVML = False

# 2) AMD/Intel için WMI
try:
    import wmi
    WMI_CONN = wmi.WMI(namespace="root\\CIMV2")
    HAS_WMI  = True
except ImportError:
    HAS_WMI = False

def _smi_query(log):
    """NVML yoksa nvidia-smi ile sorgula, pencere açmadan."""
    cmd = [
        "nvidia-smi",
        "--query-gpu=name,temperature.gpu,fan.speed,utilization.gpu,"
        "utilization.memory,clocks.gr,clocks.mem,memory.total,memory.used,power.draw",
        "--format=csv,noheader,nounits"
    ]
    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
            universal_newlines=True
        )
    except Exception:
        return False

    for idx, line in enumerate(out.strip().splitlines()):
        (
            name, temp, fan, util_gpu, util_mem,
            clk_core, clk_mem, m_total, m_used, p_draw
        ) = [x.strip() for x in line.split(",")]

        log(f"-- NVIDIA GPU #{idx}: {name} --")
        log(f"  Sıcaklık        : {temp} °C")
        log(f"  Fan Hızı        : {fan} %")
        log(f"  GPU Kullanımı   : {util_gpu} %")
        log(f"  VRAM Kullanımı  : {util_mem} %")
        log(f"  Çekirdek Hızı   : {clk_core} MHz")
        log(f"  VRAM Hızı       : {clk_mem} MHz")
        log(f"  Toplam VRAM     : {m_total} MB")
        log(f"  Kullanılan VRAM : {m_used} MB")
        log(f"  Güç Tüketimi    : {p_draw} W\n")

    return True

def show_gpu_info(log_callback=print):
    log = log_callback
    log("=== GPU Bilgisi Başlıyor ===\n")

    # A) NVIDIA — NVML
    if HAS_NVML:
        for i, h in enumerate(NV_HANDLES):
            try:
                name = nvmlDeviceGetName(h).decode()
                temp = nvmlDeviceGetTemperature(h, NVML_TEMPERATURE_GPU)
                fan  = nvmlDeviceGetFanSpeed(h)
                util = nvmlDeviceGetUtilizationRates(h)
                mem  = nvmlDeviceGetMemoryInfo(h)
                core = nvmlDeviceGetClockInfo(h, NVML_CLOCK_GRAPHICS)
                vmem = nvmlDeviceGetClockInfo(h, NVML_CLOCK_MEM)

                log(f"-- NVIDIA GPU #{i}: {name} --")
                log(f"  Sıcaklık        : {temp} °C")
                log(f"  Fan Hızı        : {fan} %")
                log(f"  GPU Kullanımı   : {util.gpu} %")
                log(f"  VRAM Kullanımı  : {util.memory} %")
                log(f"  Toplam VRAM     : {mem.total//(1024**2)} MB")
                log(f"  Kullanılan VRAM : {mem.used//(1024**2)} MB")
                log(f"  Serbest VRAM    : {mem.free//(1024**2)} MB")
                log(f"  Çekirdek Hızı   : {core} MHz")
                log(f"  VRAM Hızı       : {vmem} MHz\n")
            except Exception as e:
                log(f"  • NVML okurken hata: {e}\n")
        nvmlShutdown()
    else:
        # B) NVIDIA — nvidia-smi fallback
        ok = _smi_query(log)
        if not ok:
            log("⚠ NVIDIA bilgisi alınamadı.\n"
                "  • NVML için: pip install nvidia-ml-py3\n"
                "  • nvidia-smi için: NVIDIA sürücüsünü güncelle\n")

    # C) AMD/Intel — WMI
    if HAS_WMI:
        try:
            controllers = WMI_CONN.Win32_VideoController()
        except Exception:
            controllers = []

        for idx, gpu in enumerate(controllers):
            name = getattr(gpu, "Name", "Bilinmiyor")
            # NVML okuduysa NVIDIA’ları atla
            if "nvidia" in name.lower() and HAS_NVML:
                continue

            log(f"-- GPU #{idx}: {name} --")
            # Bellek
            try:
                ram_mb = int(gpu.AdapterRAM) // (1024**2)
            except Exception:
                ram_mb = "Bilinmiyor"
            log(f"  Toplam VRAM      : {ram_mb} MB")
            log(f"  Video İşlemcisi  : {getattr(gpu,'VideoProcessor','-')}")
            log(f"  Sürücü Versiyonu : {getattr(gpu,'DriverVersion','-')}")
            # Diğer alanlar
            for attr in ("AdapterCompatibility","PNPDeviceID","Status","VideoArchitecture"):
                val = getattr(gpu, attr, None)
                if val:
                    log(f"  {attr:<18}: {val}")
            log("")  # boş satır
    else:
        log("⚠ AMD/Intel GPU için WMI eksik. pip install wmi\n")

    log("=== GPU Bilgisi Sonu ===")