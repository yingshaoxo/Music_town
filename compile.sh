#sudo apt install nuitka
#python3 -m nuitka --standalone --follow-imports --show-progress --show-scons app.py

pyinstaller app.py -w --add-data "./static:static" --add-data "./templates:templates" --noconfirm
