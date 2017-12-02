import os
import sys
import shlex, subprocess


class Base():
    def __init__(self):
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.project_path = os.path.abspath(os.path.join(__file__, "../../"))
    

class Database(Base):
    def __init__(self):
        super().__init__()
        self.userdata_folder = os.path.join(self.project_path, 'userdata')
        
        if not os.path.exists(self.userdata_folder):
            os.mkdir(self.userdata_folder)


class App(Base):
    def __init__(self):
        super().__init__()
        self.py_version = sys.version_info 

    def run_command(self, c):
        args_list = shlex.split(c)
        result = subprocess.run(args_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=15)
        return str(result.stdout)

    def run_program(self, name):
        args_list = shlex.split(name)
        p = subprocess.Popen(args_list)
        
    def set_websokets_server(self):
        server_path = os.path.join(self.current_dir, 'server.py')
        if 'app/server.py' not in self.run_command('ps x'):
            self.run_program('python{major}.{minor} {path} &'.format(major=str(self.py_version[0]), minor=str(self.py_version[1]), path=server_path))
