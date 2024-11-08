@echo off
cls

set name=Ping

echo Press any key to start building
pause>nul
pyinstaller --windowed --clean %name%.py
cls

set src=_internal
set dst=dist\%name%\_internal

if not exist %dst% (
    mkdir %dst%
)

xcopy %src%\* %dst% /E /I /Y
rmdir /S /Q %dst%\classes
cls

echo All done, press any key to exit
pause>nul