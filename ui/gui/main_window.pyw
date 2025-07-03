# ui/gui/main_window.py

import sys
import os
import importlib
from datetime import datetime

# 🚩 1) Win32 API global hotkey imports & filter
import ctypes
from ctypes import wintypes
from PyQt5.QtCore import QAbstractNativeEventFilter
from PyQt5.QtGui  import QGuiApplication

user32    = ctypes.windll.user32
MOD_ALTGR = 0x40
WM_HOTKEY  = 0x0312

class HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, window):
        super().__init__()
        self.win = window

    def nativeEventFilter(self, eventType, message):
        msg = ctypes.wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY:
            if msg.wParam == 1:     # ID=1 → kayıt başlat
                self.win._ctrl_recorder("start")
            elif msg.wParam == 2:   # ID=2 → kayıt durdur
                self.win._ctrl_recorder("stop")
        return False, 0

# global hotkeys
try:
    import keyboard
    _HAS_KEYBOARD = True
except ImportError:
    _HAS_KEYBOARD = False

from PyQt5.QtCore    import (
    QThread, pyqtSignal, QObject,
    Qt, QEvent, QTimer
)
from PyQt5.QtGui     import QKeySequence, QIcon, QGuiApplication
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QPushButton,
    QTextEdit, QShortcut, QToolBar,
    QAction, QFileDialog, QMessageBox, QComboBox,
    QSystemTrayIcon, QMenu, QStyle
)

# TÜM MODÜL ÇIKTILARINI KAPLAYAN ÇEVİRİ TABLOSU
LOG_TRANSLATIONS = {
    # Detailed Cleaner
    "=== Detaylı Temizleyici Başlıyor ===":    "=== Detailed Cleaner Starting ===",
    "=== Detaylı Temizleyici Tamamlandı ===":  "=== Detailed Cleaner Completed ===",
    "[✔] Temizleniyor":                       "[✔] Cleaning",
    "[✔] Tamamlandı":                         "[✔] Completed",
    "Yol bulunamadı:":                       "Path not found:",
    "Hata silerken":                          "Error deleting",
    "[✔] Çöp kutusu temizleniyor...":        "[✔] Emptying Recycle Bin...",
    "[✔] Çöp kutusu temizlendi.":             "[✔] Recycle Bin emptied.",
    "[!] Çöp kutusu temizlenemedi:":          "[!] Could not empty Recycle Bin:",

    # Game Booster
    "🔧 Game Booster başladı. Boş RAM:":      "🔧 Game Booster starting. Free RAM:",
    "🛑 Hizmetler durduruluyor...":          "🛑 Stopping services...",
    "• Durduruldu:":                          "• Stopped:",
    "• Atlandı:":                             "• Skipped:",
    "💀 Gereksiz süreçler sonlandırılıyor...":"💀 Killing unnecessary processes...",
    "✅ İşlem tamamlandı. Serbest kalan RAM:":"✅ Completed. Freed RAM:",
    "Hizmetler durduruldu:":                  "Services stopped:",
    "sonlandırıldı":                          "killed",

    # System Info
    "=== Sistem Bilgisi ===":                "=== System Info ===",
    "OS       :":                            "OS       :",
    "Mimari   :":                            "Architecture:",
    "CPU Çekirdek  : Fiziksel=":             "CPU Cores: Physical=",
    ", Mantıksal=":                           ", Logical=",
    "CPU Frekans   :":                       "CPU Frequency:",
    "RAM Toplam    :":                       "RAM Total:",
    "RAM Kullanılan:":                       "RAM Used:",
    "RAM Boş       :":                       "RAM Available:",
    "Swap Toplam   :":                       "Swap Total:",
    "Swap Kullanılan:":                      "Swap Used:",
    "Disk Bölümleri:":                       "Disk Partitions:",
    "(Kullanılan:":                           "(Used:",
    "Boş:":                                   "Free:",
    "Tip:":                                   "Type:",
    "Ağ Arayüzleri (IPv4):":                 "Network Interfaces (IPv4):",

    # GPU Info
    "=== GPU Bilgisi Başlıyor ===":          "=== GPU Info Starting ===",
    "=== GPU Bilgisi Sonu ===":              "=== GPU Info Completed ===",
    "Sıcaklık        :":                     "Temperature        :",
    "Fan Hızı        :":                     "Fan Speed        :",
    "GPU Kullanımı   :":                     "GPU Utilization   :",
    "VRAM Kullanımı  :":                     "VRAM Utilization  :",
    "Toplam VRAM     :":                     "Total VRAM     :",
    "Kullanılan VRAM :":                     "Used VRAM :",
    "Serbest VRAM    :":                     "Free VRAM    :",
    "Çekirdek Hızı   :":                     "Core Clock   :",
    "VRAM Hızı       :":                     "Memory Clock :",
    "Güç Tüketimi    :":                     "Power Draw    :",

    # Common / UI
    "❌ Modül hatası":                        "❌ Module error",
    "❌ Ekran bulunamadı.":                   "❌ No screen found.",
    "📸 Ekran görüntüsü kaydedildi:":        "📸 Screenshot saved:",
}

class ModuleWorker(QObject):
    log    = pyqtSignal(str)
    finish = pyqtSignal()

    def __init__(self, module, func):
        super().__init__()
        self.module = module
        self.func   = func

    def run(self):
        try:
            m = importlib.import_module(f"modules.{self.module}")
            getattr(m, self.func)(log_callback=self.log.emit)
        except Exception as e:
            self.log.emit(f"❌ Modül hatası: {e}")
        finally:
            self.finish.emit()

class OptimizerXWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang           = 'tr'
        self.current_module = None
        self.current_func   = None

        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("recordings",  exist_ok=True)

        self._threads      = []
        self._workers      = []
        self._translations = {
            'tr': {
                'title':      "OptimizerX | Alitility ile Güçlendirilmiş",
                'detailed':   "Detaylı Temizleyici",
                'booster':    "Game Booster",
                'sysinfo':    "Sistem Bilgisi",
                'gpuinfo':    "GPU Bilgisi",
                'network':    "Ağ Hızı",
                'ping':       "Ping Test",
                'clear_log':  "Log'u Temizle",
                'save_log':   "Log'u Kaydet",
                'refresh':    "Yenile",
                'about':      "Hakkında"
            },
            'en': {
                'title':      "OptimizerX | Powered by Alitility",
                'detailed':   "Detailed Cleaner",
                'booster':    "Game Booster",
                'sysinfo':    "System Info",
                'gpuinfo':    "GPU Info",
                'network':    "Network Speed",
                'ping':       "Ping Test",
                'clear_log':  "Clear Log",
                'save_log':   "Save Log",
                'refresh':    "Refresh",
                'about':      "About"
            }
        }

        # pencere ikonu
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(icon)

        self._init_ui()
        self._init_toolbar()
        self._bind_shortcuts()
        self._update_texts()
        self._init_tray()

        # 🚩 2) Global hotkey’leri Windows’a kaydet
        user32.RegisterHotKey(None, 1, MOD_ALTGR, ord('1'))
        user32.RegisterHotKey(None, 2, MOD_ALTGR, ord('2'))

        # 🚩 Native event filter’ı yükle
        self._hk_filter = HotkeyFilter(self)
        QGuiApplication.instance().installNativeEventFilter(self._hk_filter)

        if _HAS_KEYBOARD:
            self._init_global_hotkeys()

    def _init_ui(self):
        self.resize(1000, 600)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Sol panel: butonlar
        left = QWidget()
        vlay = QVBoxLayout(left)
        vlay.setContentsMargins(10,10,10,10)
        vlay.setSpacing(8)

        # Butonlar
        self.btn_clean   = QPushButton()
        self.btn_boost   = QPushButton()
        self.btn_sysinfo = QPushButton()
        self.btn_gpu     = QPushButton()
        self.btn_net     = QPushButton()
        self.btn_ping    = QPushButton()
        for btn in (
            self.btn_clean, self.btn_boost,
            self.btn_sysinfo, self.btn_gpu,
            self.btn_net,   self.btn_ping
        ):
            vlay.addWidget(btn)
        vlay.addStretch()

        # Sağ panel: log
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addWidget(left, 0)
        layout.addWidget(self.log, 1)

        # yerel screenshot kısayolu
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self.take_screenshot)

        # button signals
        self.btn_clean.clicked.connect(lambda: self.launch("system_cleaner","clean"))
        self.btn_boost.clicked.connect(lambda: self.launch("game_booster","boost"))
        self.btn_sysinfo.clicked.connect(lambda: self.launch("system_info","show_info"))
        self.btn_gpu.clicked.connect(lambda: self.launch("gpu_info","show_gpu_info"))
        self.btn_net.clicked.connect(lambda: self.launch("network_speed","test_speed"))
        self.btn_ping.clicked.connect(lambda: self.launch("ping_test","ping_test"))

    def _init_toolbar(self):
        tb = QToolBar("Tools", self)
        self.addToolBar(tb)
        combo = QComboBox()
        combo.addItem("Türkçe", 'tr')
        combo.addItem("English", 'en')
        combo.currentIndexChanged.connect(self._on_lang_change)
        tb.addWidget(combo)
        tb.addSeparator()
        self.act_clear = QAction(QIcon.fromTheme("edit-clear"), "", self)
        self.act_clear.triggered.connect(self.log.clear)
        tb.addAction(self.act_clear)
        self.act_save = QAction(QIcon.fromTheme("document-save"), "", self)
        self.act_save.triggered.connect(self.save_log)
        tb.addAction(self.act_save)
        self.act_refresh = QAction(QIcon.fromTheme("view-refresh"), "", self)
        self.act_refresh.triggered.connect(self.refresh_module)
        tb.addAction(self.act_refresh)
        self.act_about = QAction(QIcon.fromTheme("help-about"), "", self)
        self.act_about.triggered.connect(self.show_about)
        tb.addAction(self.act_about)

    def _bind_shortcuts(self):
        # yerel kayıt kısayolları
        QShortcut(QKeySequence("Ctrl+Alt+1"), self).activated.connect(
            lambda: self._ctrl_recorder("start")
        )
        QShortcut(QKeySequence("Ctrl+Alt+2"), self).activated.connect(
            lambda: self._ctrl_recorder("stop")
        )

    def _init_global_hotkeys(self):
        # uygulama gizli olsa bile çalışır
        keyboard.add_hotkey("ctrl+0",     lambda: self.take_screenshot())
        keyboard.add_hotkey("ctrl+alt+1", lambda: self._ctrl_recorder("start"))
        keyboard.add_hotkey("ctrl+alt+2", lambda: self._ctrl_recorder("stop"))

    def _init_tray(self):
        self.tray_icon = QSystemTrayIcon(self.windowIcon(), self)
        menu = QMenu(self)
        act_restore = QAction("Göster / Restore", self)
        act_restore.triggered.connect(self._restore_from_tray)
        menu.addAction(act_restore)
        act_quit = QAction("Çıkış / Exit", self)
        act_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(act_quit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._restore_from_tray()

    def _restore_from_tray(self):
        if not self.isVisible() or self.isMinimized():
            self.showNormal()
        self.raise_()
        self.activateWindow()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self._minimize_to_tray)
            event.accept()
        else:
            super().changeEvent(event)

    def _minimize_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "OptimizerX",
            "Uygulama tepsiye indirildi. Çift tıkla geri getir.",
            QSystemTrayIcon.Information, 3000
        )

    def closeEvent(self, event):
        # X tuşu gerçek kapatmayı sağlar
        event.accept()

    def _on_lang_change(self, idx):
        code = self.sender().itemData(idx)
        if code in self._translations:
            self.lang = code
            self._update_texts()

    def _update_texts(self):
        t = self._translations[self.lang]
        self.setWindowTitle(t['title'])
        self.btn_clean.setText(t['detailed'])
        self.btn_boost.setText(t['booster'])
        self.btn_sysinfo.setText(t['sysinfo'])
        self.btn_gpu.setText(t['gpuinfo'])
        self.btn_net.setText(t['network'])
        self.btn_ping.setText(t['ping'])
        self.act_clear.setText(t['clear_log'])
        self.act_save.setText(t['save_log'])
        self.act_refresh.setText(t['refresh'])
        self.act_about.setText(t['about'])

    def translate_log(self, msg: str) -> str:
        if self.lang == 'en':
            for tr, en in LOG_TRANSLATIONS.items():
                msg = msg.replace(tr, en)
        return msg

    def launch(self, module, func):
        self.current_module = module
        self.current_func   = func
        for b in (
            self.btn_clean, self.btn_boost,
            self.btn_sysinfo, self.btn_gpu,
            self.btn_net,   self.btn_ping
        ):
            b.setEnabled(False)
        self.log.clear()
        thread = QThread(self)
        worker = ModuleWorker(module, func)
        worker.moveToThread(thread)
        self._threads.append(thread)
        self._workers.append(worker)
        worker.log.connect(lambda txt: self.log.append(self.translate_log(txt)))
        thread.started.connect(worker.run)
        worker.finish.connect(thread.quit)
        worker.finish.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finish.connect(self._on_finish)
        thread.start()

    def _on_finish(self):
        for b in (
            self.btn_clean, self.btn_boost,
            self.btn_sysinfo, self.btn_gpu,
            self.btn_net,   self.btn_ping
        ):
            b.setEnabled(True)

    def refresh_module(self):
        if self.current_module and self.current_func:
            self.launch(self.current_module, self.current_func)

    def save_log(self):
        t = self._translations[self.lang]
        path, _ = QFileDialog.getSaveFileName(
            self, t['save_log'], "", "Text Files (*.txt);;All Files (*)"
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.log.toPlainText())
            self.log.append(f"💾 {t['save_log']}: {path}")

    def show_about(self):
        info_tr = (
            "OptimizerX\n"
            "Sürüm: 1.0\n"
            "Alitility ile Güçlendirilmiş\n\n"
            "Kısayollar:\n"
            "  Ctrl+0     Ekran görüntüsü al\n"
            "  AltGr+1    Kayıt başlat\n"
            "  AltGr+2    Kayıt durdur\n\n"
            "https://github.com/Alitility/OptimizerX"
        )
        info_en = (
            "OptimizerX\n"
            "Version: 1.0\n"
            "Powered by Alitility\n\n"
            "Shortcuts:\n"
            "  Ctrl+0     Take screenshot\n"
            "  AltGr+1    Start recording\n"
            "  AltGr+2    Stop recording\n\n"
            "https://github.com/Alitility/OptimizerX"
        )
        text = info_tr if self.lang == 'tr' else info_en
        QMessageBox.information(
            self,
            self._translations[self.lang]['about'],
            text
        )

    def take_screenshot(self):
        screen = QGuiApplication.primaryScreen()
        t      = self._translations[self.lang]
        if not screen:
            self.log.append(self.translate_log("❌ Ekran bulunamadı."))
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = os.path.join("screenshots", f"screen_{ts}.png")
        pix = screen.grabWindow(0)
        pix.save(fn, "png")
        self.log.append(self.translate_log("📸 Ekran görüntüsü kaydedildi:") + " " + fn)

    def _ctrl_recorder(self, action: str):
        try:
            import modules.screen_recorder as sr
            cb = lambda txt: self.log.append(self.translate_log(txt))
            if action == "start":
                sr.start_record(log_callback=cb)
            else:
                sr.stop_record(log_callback=cb)
        except Exception as e:
            self.log.append(f"❌ Recorder error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OptimizerXWindow()
    w.show()
    sys.exit(app.exec_())