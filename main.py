import requests
import json
from tqdm import tqdm


"""Token для VK и Яндекса должны лежать в файле token_vk_ya,который содержит две строки
   Первая строка token_vk
   Вторая строка token_ya"""


class YandexDisk:
    def __init__(self, token):
        self.token = token
        self.url = 'https://cloud-api.yandex.net/v1/'

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
             }

    def get_info_yandex_user(self):
        url = self.url + 'disk'
        headers = self.get_headers()
        response = requests.get(url=url, headers=headers)
        return response.json()

    def download_photo_by_the_link(self, url_photo, name_file):
        url = self.url + 'disk/resources/upload'
        headers = self.get_headers()
        params = {
            'url': url_photo,
            "path": name_file+'.jpg',

            }
        response = requests.post(url=url, headers=headers, params=params)
        code = response.status_code
        response = response.json()

        if 'error' in list(response):
            response = response['message']+response['error']

        result = {code: response}
        return result

    def create_dir(self, name_dir):
        url = self.url + 'disk/resources'
        headers = self.get_headers()
        params = {'path': name_dir,
                  'fields': ''
                  }
        response = requests.put(url=url, headers=headers, params=params)
        code = response.status_code
        response = response.json()

        if 'error' in list(response):
            response = response['message']+response['error']

        result = {code: response}
        return result


def get_photos_profile(id_vk, count_photos='5'):

    """На вход функция принимает id пользователя в VK(id =str() )
       и количество фотографий (count_photos = str() ). После этого при помощи  _response_get формируется get запрос.
     _response_get проверяет на код запроса. если код =200
      В результате функция возвращает dict (смотри документацию)VK """

    url = 'https://api.vk.com/method/photos.get'
    params = {
                'user_id': id_vk,
                'album_id': 'profile',
                'extended': '1',
                'rev': '0',
                'count': count_photos,
                'access_token': token_vk,
                'v': ver_api


              }
    dict_response = _response_get(url, params)
    return dict_response


def _response_get(any_url, any_params):
    """Обрабатывает GET запросы  возвращает обьект Response из библиотеки requests если запрос прошел.
        Если запрос не прошел выводит код ошибки """
    response = requests.get(url=any_url, params=any_params)
    if response.status_code == 200:
        # print("Запрос 200")
        res = response.json()

        if res.get('response') is None:
            res = response.json()['error']
        else:
            res = response.json()['response']
    else:
        res = f'Что-то пошло не так смотри код ошибки  {response.status_code}'

    return res


def _processing_dict_api_get_photos(dict_photos_user, count_photos='5'):
    """Функция принимает на вход словать полученнйы по ключу ['response'] при  истользования метода API VK photos.get
       и количестово фотограций. После чего обрабатывает данные  .Функция возвращает словать
       dict_result= {countLIKES : url_photos  } """
    result = {}
    # _count = 0
    all_count_photos = dict_photos_user['count']

    need_count_photos_user = int(count_photos)

    if all_count_photos <= need_count_photos_user:
        need_count_photos_user = all_count_photos
        print(f" всего {all_count_photos} фото")

    list_photos_user = dict_photos_user['items']
    for i in range(need_count_photos_user):
        if i <= all_count_photos:

            # _count += 1
            photo_ = list_photos_user[i]
            count_likes_photo = photo_['likes']['count']
            create_photo = photo_['date']
            count_size_photos = (len(photo_['sizes']))
            dict_format_photos = {}
            [dict_format_photos.update({photo_['sizes'][q]['type']: photo_['sizes'][q]['url']}) for q in
             range(count_size_photos)]

            # print(f"ФОТО {_count}")

            if 'w' in list(dict_format_photos):

                url_max_size = dict_format_photos.get('w')
                size = "w"

            elif list(dict_format_photos)[-1] == 'x' and list(dict_format_photos)[-2] == 's':
                url_max_size = dict_format_photos.get(list(dict_format_photos)[-3])
                size = list(dict_format_photos)[-3]
            else:
                url_max_size = dict_format_photos.get(list(dict_format_photos)[-1])
                size = list(dict_format_photos)[-1]

            if result.get(count_likes_photo) is None:
                result.update({count_likes_photo: (url_max_size, size)})
            else:
                key = (count_likes_photo, create_photo)
                result.update({key: (url_max_size, size)})

        else:
            break

    return result


def get_users_info(id_vk, str_info='bdate ,city'):
    """Функция get_users_info на вход принимает id пользователя в ВК(id = str() ) и переменную
        str_info. (str_info содержит параметры выводимой информации. bdate дата рождения,city город
        смотри документацию api ВК).Возвращает dict_"""
    url = "https://api.vk.com/method/users.get"
    params = {
             "user_ids": id_vk,
             'fields': str_info,

             'access_token': token_vk,
             'v': ver_api

            }
    res = _response_get(url, params)[0]

    return res


def copy_photos_vk_to_ya_disk(id_users_vk, token):
    class_yandisk = YandexDisk(token)
    dict_url_photo = _processing_dict_api_get_photos(get_photos_profile(id_users_vk))
    class_yandisk.create_dir(id_users_vk)
    list_for_json = []
    for photo_name, url_photo in tqdm(dict_url_photo.items(), desc="Photos", unit=" photo", colour='GREEN'):
        class_yandisk.download_photo_by_the_link(url_photo[0], id_users_vk+'/'+str(photo_name))
        _dict = {"file_name": str(photo_name)+'.jpg',
                 'size': url_photo[1]}
        list_for_json.append(_dict)
    with open("data_file.json", "w") as write_file:
        json.dump(list_for_json, write_file)


ver_api = '5.131'
with open("C:\\Users\\BAI\\token_vk_ya.txt") as file:
    for line in file:
        token_vk = line.strip()
        token_ya = (file.readline().strip())

id = '5'
copy_photos_vk_to_ya_disk(id, token_ya)
