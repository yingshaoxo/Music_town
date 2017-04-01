import time
import os


commands = '''
pkill gunicorn

mkdir /opt/music
mv static/music/* /opt/music/ -f

chmod 400 ../.ssh/id_rsa
eval "$(ssh-agent -s)"
ssh-add ../.ssh/id_rsa

git add .
git commit -m "update"
git push origin master

mv /opt/music/* static/music/ -f
'''
commands = [c for c in commands.split('\n') if c != '']
#os.system('')
#os.system(' && '.join(commands))
for c in commands:
	os.system(c)
	time.sleep(3)

print('OK')
