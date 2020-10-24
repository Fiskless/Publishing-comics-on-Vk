import requests
import os
import urllib3
from dotenv import load_dotenv
import random
import shutil


def load_random_comic_from_internet(filename, url):

    response = requests.get(url, verify=False)
    response.raise_for_status()
    picture_url = response.json()['img']
    response = requests.get(picture_url, verify=False)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)
    comment = response.json()['alt']
    title = response.json()['title']
    return comment, title


def upload_comic_from_server(url, access_token):

    params = {
        'access_token': access_token,
        'v': 5.124,
        'group_id': 199612697
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']

    with open('comics/comic.png', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        response_json_form= response.json()
        server = response_json_form['server']
        photo = response_json_form['photo']
        hash = response_json_form['hash']

    return server, photo, hash


def save_comic_in_album(url, access_token):

    server, photo, hash = upload_comic_from_server(
        'https://api.vk.com/method/photos.getWallUploadServer',
        access_token_vk)

    params = {
            'server': server,
            'photo': photo,
            'hash': hash,
            'access_token': access_token,
            'v': 5.124,
            'group_id': 199612697
        }

    response = requests.post(url, params=params)
    response.raise_for_status()
    response_json_form = response.json()
    media_id = response_json_form['response'][0]['id']
    owner_id = response_json_form['response'][0]['owner_id']
    return media_id, owner_id


def post_comic_in_group(url, access_token):

    media_id, owner_id = save_comic_in_album(
        'https://api.vk.com/method/photos.saveWallPhoto',
        access_token_vk)
    comment, title = load_random_comic_from_internet(
        'comics/comic.png',
        f'http://xkcd.com/{comic_number}/info.0.json')

    params = {
            'access_token': access_token,
            'v': 5.124,
            'group_id': 199612697,
            'owner_id': -199612697,
            'from_group': 1,
            'attachments': f'photo{owner_id}_{media_id}',
            'message': title + '\n' + comment
        }

    response = requests.post(url, params=params)
    response.raise_for_status()


if __name__ == '__main__':

    load_dotenv()
    access_token_vk = os.getenv("ACCESS_TOKEN_VK")

    urllib3.disable_warnings()

    os.makedirs('comics', exist_ok=True)

    comic_number = random.randint(1, 2374)
    load_random_comic_from_internet(
        'comics/comic.png',
        f'http://xkcd.com/{comic_number}/info.0.json')

    post_comic_in_group('https://api.vk.com/method/wall.post', access_token_vk)

    shutil.rmtree('comics')
