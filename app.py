# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, send_file
import jinja2.ext
import subprocess
import json
import os
from os.path import join, isdir, abspath, basename, getctime
import random
import sys

Use_OutSide_Folder = False
arguments = sys.argv[1:]
if len(arguments) > 0:
    the_music_path = arguments[0]
    if os.path.exists(the_music_path):
        Use_OutSide_Folder = True
        the_music_path = os.path.abspath(the_music_path)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


CURRENT_DIR = resource_path(".")
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')
MUSIC_DIR = os.path.join(STATIC_DIR, 'music')
TEMPLATE_DIR = os.path.join(CURRENT_DIR, 'templates')
USERDATA_FOLDER = os.path.join(CURRENT_DIR, 'userdata')
if not os.path.exists(USERDATA_FOLDER):
    os.mkdir(USERDATA_FOLDER)
USERDATA_FILE = os.path.join(USERDATA_FOLDER, 'users.json')


if Use_OutSide_Folder == True:
    the_link_music_folder = os.path.join(MUSIC_DIR, "linked_music_folder")
    os.system("rm -fr '{path}'".format(path=the_link_music_folder))
    os.system("mkdir -p '{path}'".format(path=the_link_music_folder))
    os.system("ln -s '{source_path}' '{target_path}'".format(source_path=the_music_path, target_path=the_link_music_folder))


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


def find_music_files(path, username=None):
    music_files = []

    for root, dirs, files in os.walk(path, followlinks=True):
        for file in files:
            if file.endswith('.mp3') or file.endswith(".m4a"):
                full_path = abspath(join(root, file))
                music_files.append(full_path)

    if not music_files:
        return []

    # Sort by creation time (newest first)
    music_files.sort(key=getctime, reverse=True)
    new_music_files = []
    for one in music_files:
        if "linked_music_folder" in one:
            new_music_files.append(one[len(MUSIC_DIR)-1:])
        else:
            new_music_files.append(basename(one))
    music_files = new_music_files

    if username:
        userinfo = in_or_out(username)
        if not userinfo:
            print("No userinfo")
            return []

        usermusic = userinfo.get('music')
        if not usermusic:
            print("No usermusic")
            return []

        usermusic_names = [i['name'] for i in usermusic]
        music_files = [f for f in music_files if f in usermusic_names]

    return [{'name': song} for song in music_files]


def read_music(username):
    path = join(CURRENT_DIR, 'static/music')
    if not isdir(path):
        os.mkdir(path)
        return []
    songs = find_music_files(path, username)
    #print(songs)
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


all_songs = []
@app.route('/home')
def home():
    global all_songs

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
        all_songs = songs

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
                a_music_path = os.path.join(os.path.join(CURRENT_DIR, 'static/music'), songs[delete_id]['name'])
                if "linked_music_folder" in songs[delete_id]['name']:
                    raise Exception("We will not delete linked music folder:", a_music_path)
                else:
                    os.remove(a_music_path)
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
    global all_songs, Use_OutSide_Folder

    if Use_OutSide_Folder == False:
        return redirect(url_for('home'))

    try:
        if len(all_songs) == 0:
            songs = read_music("")
            all_songs = [{'name': song['name'][:-4]} for song in songs]
        if len(all_songs) == 0:
            raise Exception("no songs in ./static/music folder")
        song = random.choice(all_songs)
        file_path = MUSIC_DIR + "/" + song['name'] + '.mp3'
        print(file_path)

        if not os.path.exists(file_path):
            return "File not found", 404

        return send_file(
            file_path,
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        return str(e), 500


# start the server with the 'run()' method
if __name__ == '__main__':
    app.secret_key = 'some random string'
    app.run(host='0.0.0.0', port=2016, debug=True)

# for Gunicorn can use
#app.secret_key = 'some random string'
#app.run(host='0.0.0.0', port=80)
