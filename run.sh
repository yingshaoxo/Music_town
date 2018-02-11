pkill python3.6

sudo apt-get install -y python3.6
sudo apt-get install -y python3-pip
sudo pip3 install --no-cache-dir -r requirements.txt

nohup python3.6 app/app.py &
