import json

username = input("The username is: ").strip()
password = input("The password is: ").strip()
file_name = 'users.json'


def get_json():
    with open(file_name, 'r') as f:
        text = f.read()
    return json.loads(text)


def write_json(a_dict):
    with open(file_name, 'w') as f:
        f.write(json.dumps(a_dict, sort_keys=True, indent=4))


all_ = get_json()
new = {
    username: {'music': [], 'password': password}
}
all_.update(new)
write_json(all_)
print(all_)
