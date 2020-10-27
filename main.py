import requests
import os
import urllib3
from dotenv import load_dotenv
import random
import shutil


def download_random_comic_from_internet(filename, url):

    response = requests.get(url, verify=False)
    response.raise_for_status()
    random_comics = response.json()
    picture_url = random_comics['img']
    comment = random_comics['alt']
    title = random_comics['title']
    response = requests.get(picture_url, verify=False)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)

    return comment, title


def get_comic_data_from_server(url, access_token, vk_group_id):

    params = {
        'access_token': access_token,
        'v': 5.124,
        'group_id': vk_group_id
    }

    response = requests.get(url, params=params)
    information_to_get_picture_url = response.json()
    if not information_to_get_picture_url.get('error'):
        upload_url = information_to_get_picture_url['response']['upload_url']

        with open('comics/comic.png', 'rb') as file:
            files = {
                'photo': file
            }
            response = requests.post(upload_url, files=files)
            response.raise_for_status()
            information_to_load_picture = response.json()
            server = information_to_load_picture['server']
            photo = information_to_load_picture['photo']
            hash = information_to_load_picture['hash']

        return server, photo, hash


def save_comic_in_album(url, access_token, vk_group_id):

    server, photo, hash = get_comic_data_from_server(
        'https://api.vk.com/method/photos.getWallUploadServer',
        access_token_vk,
        vk_group_id
    )

    params = {
            'server': server,
            'photo': photo,
            'hash': hash,
            'access_token': access_token,
            'v': 5.124,
            'group_id': vk_group_id
        }

    response = requests.post(url, params=params)
    if not response.json().get('error'):
        information_to_post_comic = response.json()['response'][0]
        media_id = information_to_post_comic['id']
        owner_id = information_to_post_comic['owner_id']
        return media_id, owner_id


def post_comic_in_group(url, access_token, vk_group_id):

    media_id, owner_id = save_comic_in_album(
        'https://api.vk.com/method/photos.saveWallPhoto',
        access_token_vk, vk_group_id)
    comment, title = download_random_comic_from_internet(
        'comics/comic.png',
        f'http://xkcd.com/{comic_number}/info.0.json')

    params = {
        'access_token': access_token,
        'v': 5.124,
        'group_id': vk_group_id,
        'owner_id': -vk_group_id,
        'from_group': 1,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': f'{title} \n {comment}'
        }

    response = requests.post(url, params=params)


if __name__ == '__main__':

    try:

        load_dotenv()
        access_token_vk = os.getenv("ACCESS_TOKEN_VK")
        vk_group_id = int(os.getenv("VK_GROUP_ID"))

        urllib3.disable_warnings()

        os.makedirs('comics', exist_ok=True)

        number_of_first_comic = 1
        number_of_last_comic = 2376
        comic_number = random.randint(number_of_first_comic,
                                      number_of_last_comic)

        download_random_comic_from_internet(
            'comics/comic.png',
            f'http://xkcd.com/{comic_number}/info.0.json')

        post_comic_in_group('https://api.vk.com/method/wall.post',
                            access_token_vk,
                            vk_group_id)

    finally:

        shutil.rmtree('comics')
