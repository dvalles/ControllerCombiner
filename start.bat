@echo off

REM run hid hide
start /d "%HID_HIDE%" HidHideClient.exe

REM run controller combiner
python ./lib/main.py