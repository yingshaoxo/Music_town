# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory
import jinja2.ext
import subprocess
import json
import os
import random
import sys


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


CURRENT_DIR = resource_path(".")
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')
TEMPLATE_DIR = os.path.join(CURRENT_DIR, 'templates')
USERDATA_FOLDER = os.path.join(CURRENT_DIR, 'userdata')
if not os.path.exists(USERDATA_FOLDER):
    os.mkdir(USERDATA_FOLDER)
USERDATA_FILE = os.path.join(USERDATA_FOLDER, 'users.json')


def get_json():
    with open(USERDATA_FILE, 'r') as f:
        text = f.read()
    return json.loads(text)


def write_json(a_dict):
    with open(USERDATA_FILE, 'w') as f:
        f.write(json.dumps(a_dict, sort_keys=True, indent=4))


if os.path.exists(USERDATA_FILE) == False:
    write_json({
        "Visitor": {
            "music": [],
            "password": "Visitor"
        },
        "yingshaoxo": {
            "music": [],
            "password": "yingshaoxo"
        }
    })


# Just use json as datebase
def in_or_out(username, a_dict=None):
    all_ = get_json()
    if a_dict == None:  # if no data need store, retuen the imformation of the user
        return all_.get(username)
    else:  # if got a dict, it'll be store under the username
        all_.update({username: a_dict})
        write_json(all_)
        return 'Alread update'


def get_users():
    all_ = get_json()
    return all_.keys()


def read_music(username):
    path = os.path.join(CURRENT_DIR, 'static/music')
    if os.path.isdir(path) == False:
        os.mkdir(path)
    files = os.listdir(path)
    files = [os.path.abspath(os.path.join(path, i)) for i in files]
    files = sorted(files, key=os.path.getctime, reverse=True)
    files = [os.path.basename(i) for i in files]
    music_files = [i for i in files if '.mp3' in i]

    if username != '':
        userinfo = in_or_out(username)
        if userinfo == None:
            print("No userinfo")
            return []
        usermusic = userinfo.get('music')
        if usermusic == None:
            print("No usermusic")
            return []
        usermusic_name = [i['name'] for i in usermusic]
        music_files = [i for i in music_files if i in usermusic_name]
        print(usermusic)

    songs = [{'name': song} for song in music_files]
    return songs


def write_music(username, music_name):
    userinfo = in_or_out(username)
    usermusic = userinfo.get('music')
    if type(music_name) is list:
        userinfo.update({'music': music_name})
    else:
        if usermusic == None:
            userinfo.update({'music': [{'name': music_name}]})
        else:
            usermusic.append({'name': music_name})
            userinfo.update({'music': usermusic})
    in_or_out(username, userinfo)
    return 'Already add song to user music list.'


# create the application object
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.before_request
def session_management():
    session.permanent = True


# @app.route('/music/<path:filename>')
# def static_files(filename):
#     return send_from_directory(LOCAL_PATH, filename)


@app.route('/')
def welcome():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    users = get_users()
    users_song = []
    for user in users:
        songs = read_music(user)
        # print(songs)
        songs = [{'name': song['name'][:-4]} for song in songs]
        if len(songs):
            users_song.append(songs)

    # read all music
    songs = read_music("")
    songs = [{'name': song['name'][:-4]} for song in songs]
    if len(songs):
        users_song.append(songs)

    return render_template('home.html', users_song=users_song)


@app.route('/user')
def user():
    username = session.get('username')
    print(username, 'loged in...')
    songs = read_music(username)
    songs = [{'name': song['name'][:-4]} for song in songs]
    return render_template('user.html', username=username, songs=songs)


@app.route('/func/<func>')
def func(func):
    username = session.get('username')
    if func == 'Logout':
        session.clear()
        print(username, 'loged out')
    return redirect(url_for('home'))


@app.route('/manage', methods=['GET', 'POST'])
def manage():
    username = session.get('username')
    if username == None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        btn_value = request.form['btn']
        if btn_value[:len('Delete')] == 'Delete':
            delete_id = int(btn_value[len('Delete'):])-1
            songs = read_music(username)
            try:
                os.remove(os.path.join(os.path.join(CURRENT_DIR, 'static/music'), songs[delete_id]['name']))
                del songs[delete_id]
            except:
                return redirect(url_for('manage'))
            write_music(username, songs)
    songs = read_music(username)
    # print(songs)
    if len(songs) == 0:
        return redirect(url_for('user'))
    return render_template('main.html', page_name='manage', username=username, songs=songs)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    username = session.get('username')
    if username == None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # check if the post request has the file part
        uploaded_files = request.files.getlist("file[]")
        for file in uploaded_files:

            #file = request.files['file']
            # if user does not select file, browser also submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and '.mp3' in file.filename:
                filename = file.filename
                temp_name = os.path.join(os.path.join(CURRENT_DIR, 'static/music'), '@w@{}'.format(filename))
                file.save(temp_name)
                try:
                    p = subprocess.Popen(['ffmpeg -i "{name}" -ac 1 -ab 64k "{real_name}"'.format(name=temp_name, real_name=temp_name.replace('@w@', ''))], shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    p.wait()
                    p.communicate()
                    p.kill()
                    if os.path.exists(temp_name.replace('@w@', '')):
                        os.remove(temp_name)
                    else:
                        os.rename(temp_name, temp_name.replace('@w@', ''))
                except Exception as e:
                    print(e)
                    os.rename(temp_name, temp_name.replace('@w@', ''))
                write_music(session.get('username'), filename)
                print('Uploaded a mp3')
                flash('Uploaded')
        return redirect(url_for('user'))
    return render_template('main.html', page_name='upload', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if request.form['btn'] == 'Login':
            userinfo = in_or_out(username)
            if userinfo == None:
                if username == 'friend':
                    error = 'unregistered'
                else:
                    error = "You havn't register yet. Ask yingshaoxo if you really want it."
            elif userinfo.get('password') != password:  # indentify password
                error = 'Password error. Please try again.'
            elif username.strip(' ') == '':
                error = 'You did not write your name on it, try again.'
            else:
                session.clear()
                session['username'] = username
                #flash('You were successfully logged in')
                return redirect(url_for('user'))
        elif request.form['btn'] == 'Visit':
            songs = read_music('Visitor')
            in_or_out('Visitor', {'password': 'Visitor'})  # set a new user with password
            write_music('Visitor', songs)
            session['username'] = 'Visitor'
            return redirect(url_for('user'))
        elif request.form['btn'] == 'Register':
            if in_or_out(username) == None:
                in_or_out(username, {'password': password})  # set a new user with password
                #flash('Welcom to our place')
                session.clear()
                session['username'] = username
                return redirect(url_for('user'))
            else:
                error = 'This accunt got used, please make your own a new one.'

    return render_template('login.html', error=error)


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('home'))


# start the server with the 'run()' method
if __name__ == '__main__':
    app.secret_key = 'some random string'
    app.run(host='0.0.0.0', port=2016, debug=True)

# for Gunicorn can use
#app.secret_key = 'some random string'
#app.run(host='0.0.0.0', port=80)
