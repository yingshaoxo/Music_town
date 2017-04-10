import requests

def get_pic_url(num=389281):
    r = requests.get('https://yande.re/post/show/'+str(num))
    try:
        url = r.text.split('<link rel="image_src" href="')[1].split('" />')[0]
    except Exception as e:
        print(e)
        return ''
    return url

def download_file(url, local_filename=''):
    if local_filename == '':
        local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename

def change_BG(num=None):
    if num == None:
        import random
        url = get_pic_url(random.randrange(0, 389281))
    else:
        url = get_pic_url(num)
    return download_file(url, './static/BG.jpg')

print(change_BG(389281))
