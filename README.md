# ZBX_MaintenanceModeCreator
basic app for putting a server into maintenance mode during an update or security patch inslattion.


cd ./ZBX_MaintenanceModeCreator

pyuic5 ./shell_ui.ui -o ./shell_ui.py

pyinstaller --onefile ./zbx_mm.py --noconsole --icon=Custom.ico