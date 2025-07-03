# modules/screen_recorder.py

import os
import threading
import time
from datetime import datetime

import cv2
import numpy as np
from mss import mss

# Global değişkenler
_rec_thread = None
_recording  = False

def _record_loop(path, fps=60, resize_factor=1):
    """
    mss ile tüm ekranı yakalayıp cv2.VideoWriter ile kaydeder.
    fps: hedef kare hızı (örn. 60)
    resize_factor: 1 = tam çözünürlük, 2 = yarıya indir, vs.
    """
    global _recording

    with mss() as sct:
        mon    = sct.monitors[1]
        w      = mon["width"]
        h      = mon["height"]
        width  = w // resize_factor
        height = h // resize_factor

        # VideoWriter (avc1 = H.264 in mp4 container)
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        writer = cv2.VideoWriter(path, fourcc, fps, (width, height), True)

        frame_interval = 1.0 / fps
        next_time      = time.time()

        while _recording:
            img   = sct.grab(mon)
            frame = np.array(img)[:, :, :3]  # BGRA→BGR

            if resize_factor != 1:
                frame = cv2.resize(frame, (width, height),
                                   interpolation=cv2.INTER_LINEAR)

            writer.write(frame)

            # Zamanlayıcıyla uyku
            next_time += frame_interval
            sleep = next_time - time.time()
            if sleep > 0:
                time.sleep(sleep)

        writer.release()

def start_record(log_callback=print, fps=60, resize_factor=1):
    """
    AltGr+1 ile çağırın:
      start_record(log_callback, fps=60, resize_factor=1)
    """
    global _rec_thread, _recording

    if _recording:
        log_callback("⚠ Recording already in progress")
        return

    os.makedirs("recordings", exist_ok=True)
    fn   = datetime.now().strftime("record_%Y%m%d_%H%M%S.mp4")
    path = os.path.join("recordings", fn)

    _recording = True
    _rec_thread = threading.Thread(
        target=_record_loop,
        args=(path, fps, resize_factor),
        daemon=True
    )
    _rec_thread.start()
    log_callback(f"▶ Recording started: {path} @ {fps} FPS")

def stop_record(log_callback=print):
    """
    AltGr+2 ile çağırın:
      stop_record(log_callback)
    """
    global _rec_thread, _recording

    if not _recording:
        log_callback("⚠ No recording in progress")
        return

    _recording = False
    _rec_thread.join(timeout=5)
    log_callback("■ Recording stopped")
    _rec_thread = None