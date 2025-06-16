echo off
echo Build Init...

call .venv\Scripts\activate.bat

nuitka AtriaApplication.py ^
    --windows-console-mode=force^
    --windows-icon-from-ico=Art\AtriaLogo2.ico^
    --verbose ^
    --show-progress ^
    --enable-plugin=tk-inter
