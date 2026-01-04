
@echo on
cd /d "%~dp0"

REM Настройки (можно менять)
set PYTHON_PATH="python.exe run.py"
set BROWSER_PATH=C:\Users\Workstation\AppData\Local\Yandex\YandexBrowser\Application\browser.exe
set SITE_URL=http://127.0.0.1:5555/
set DELAY=1

echo [%time%] Запуск командной строки...
rem start cmd.exe
rem timeout /t %DELAY% /nobreak >nul

echo [%time%] Запуск Python...
start C:\Users\Workstation\Desktop\LaLa\LaLa-main\run.py
timeout /t %DELAY% /nobreak >nul

echo [%time%] Запуск браузера...
start %BROWSER_PATH%
timeout /t %DELAY% /nobreak >nul

echo [%time%] Открытие сайта: %SITE_URL%
start %SITE_URL%


echo Готово!