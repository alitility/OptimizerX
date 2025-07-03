import keyboard

# … sınıf içinde …
def __init__(self):
    # … önceki init …
    if True:  # keyboard modülü yüklüyse
        keyboard.add_hotkey("ctrl+alt+1", lambda: self._ctrl_recorder("start"))
        keyboard.add_hotkey("ctrl+alt+2", lambda: self._ctrl_recorder("stop"))
        keyboard.add_hotkey("ctrl+0",      lambda: self.take_screenshot())