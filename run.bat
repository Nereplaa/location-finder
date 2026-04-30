@echo off
chcp 65001 >nul
title AVM Rehber — Flask Sunucu

echo.
echo  ================================================
echo   AVM Akilli Urun Bulma Sistemi (AKIS)
echo   Flask Development Server
echo  ================================================
echo.

:: Proje dizinine gec
cd /d "%~dp0"

:: Sanal ortam kontrolu ve Python yolu belirle
set "PYTHON_EXE="
if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
    set "PIP_EXE=%~dp0venv\Scripts\pip.exe"
    echo [OK] Sanal ortam bulundu: venv
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
    set "PIP_EXE=%~dp0.venv\Scripts\pip.exe"
    echo [OK] Sanal ortam bulundu: .venv
) else (
    echo [!] Sanal ortam bulunamadi, olusturuluyor...
    python -m venv venv
    if errorlevel 1 (
        echo [HATA] Sanal ortam olusturulamadi. Python 3.x yuklu mu?
        pause
        exit /b 1
    )
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
    set "PIP_EXE=%~dp0venv\Scripts\pip.exe"
    echo [OK] Sanal ortam olusturuldu.
)

:: Gerekli paketleri kur
if exist "requirements.txt" (
    echo [*] Bagimliliklar kontrol ediliyor...
    "%PIP_EXE%" show flask >nul 2>&1
    if errorlevel 1 (
        echo [*] Gerekli paketler yukleniyor...
        "%PIP_EXE%" install -r requirements.txt
        if errorlevel 1 (
            echo [HATA] Paket yukleme basarisiz oldu.
            pause
            exit /b 1
        )
        echo [OK] Paketler yuklendi.
    )
) else (
    echo [!] requirements.txt bulunamadi, paket kontrolu atlaniyor.
)

:: Ortam degiskenleri
set FLASK_APP=backend.app:create_app
set FLASK_ENV=development
set SECRET_KEY=dev-secret-key-degistirin
set POS_API_KEY=dev-pos-api-key-degistirin

:: Flask-Migrate: ilk calistirmada migration olustur
if not exist "migrations" (
    echo [*] Veritabani migration klasoru olusturuluyor...
    "%PYTHON_EXE%" -m flask db init
    "%PYTHON_EXE%" -m flask db migrate -m "initial migration"
    "%PYTHON_EXE%" -m flask db upgrade
    echo [OK] Migration tamamlandi.
)

echo.
echo [*] Sunucu baslatiliyor: http://127.0.0.1:5000
echo [*] POS API icin X-API-Key: %POS_API_KEY%
echo [*] Durdurmak icin Ctrl+C
echo.

"%PYTHON_EXE%" -m flask run --host=0.0.0.0 --port=5000 --debug

pause
