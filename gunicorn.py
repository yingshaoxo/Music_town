import time
import os

#rm nohup.out
commands = '''
pkill gunicorn
sudo nohup gunicorn -b 0.0.0.0:80 -w 4 -t 777 app:app &
'''
commands = [c for c in commands.split('\n') if c != '']
for c in commands:
    os.system(c)
    time.sleep(3)
print('OK')
