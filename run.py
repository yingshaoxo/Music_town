from flask import Flask, send_from_directory, redirect, url_for
import os


your_host_ip = '192.168.1.103'
#your_host_ip = '45.63.90.169' 
your_port = '80'


def show(name):
    dir_ = [i for i in os.listdir(name) if os.path.isdir(os.path.join(name, i))==True]
    file_ = [i for i in os.listdir(name) if os.path.isfile(os.path.join(name, i))==True]
    all_ = ['<a href="http://{ip}:{port}/{path}">{name}</a>'.format(ip=your_host_ip, port=your_port, path=os.path.join(name, i), name=i) for i in dir_ + file_]
    css_ = '''
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!--[if lt IE 9]><script src="http://css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script> <![endif]-->
'''
    html = css_ + '<body>' + '<br>'.join(all_) + '</body>'
    return html


app = Flask(__name__)

@app.route('/')
def home():
    return show('.')

@app.route('/<path:path>')
def any_path(path):
    if os.path.exists(path) == True:
        if os.path.isdir(path) == True:
            return show(path)
        else:
            return send_from_directory('.', path)
    return send_from_directory('.', path)

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('home'))

if __name__ == '__main__':
    print('http://{}:{}'.format(your_host_ip, your_port))
    app.run(host='0.0.0.0', port=your_port)
