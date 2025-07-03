@echo off
rem ---- build_exe.bat ----
rem Ortamı kontrol etmek için (opsiyonel):
where python >nul 2>&1 || (
  echo Python bulunamadi. Lutfen PATH'e ekleyin.
  pause
  exit /b
)
rem Sanal ortam varsa burayı aktif edin
rem call .\venv\Scripts\activate.bat

echo PyInstaller ile EXE olusturuluyor...
pyinstaller --name OptimizerX --onefile --windowed --icon=resources/app.ico ^
            --add-data "screenshots;screenshots" ^
            --add-data "recordings;recordings" ^
            ui\gui\main_window.py

if errorlevel 1 (
  echo PyInstaller basarisiz.
  pause
  exit /b
)

echo EXE olusturuldu: dist\OptimizerX.exe
pause