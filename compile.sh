#sudo apt install nuitka
#python3 -m nuitka --standalone --follow-imports --show-progress --show-scons app.py

python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install flask==0.12.2 pyinstaller

pyinstaller app.py -w --add-data "./static:static" --add-data "./templates:templates" --noconfirm
