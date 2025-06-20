echo off
echo Entering venv

call .venv\Scripts\activate.bat

echo Build Init...

call nuitka AtriaApplication.py ^
    --windows-console-mode=force^
    --windows-icon-from-ico=Art\AtriaLogo2.ico^
    --verbose ^
    --show-progress ^
    --show-modules^
    --show-scons^
    --include-module=modelEditWindow

echo Sending Notification...

call python notification.py

echo Build Complete
