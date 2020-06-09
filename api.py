# -*- coding: utf-8 -*-

import requests
import time
import json
import boto3
import os


service_key = 'AQVNwTN2AJRehyKlSMarPl2_1JjXLkM8Qnn5s8ni'


def get_audio_from_user(bot, chat_id, voice_id):
    file_info = bot.get_file(voice_id)
    content_file = bot.download_file(file_info.file_path)
    with open(f'{chat_id}.ogg', 'wb') as file_for_bucket:
        file_for_bucket.write(content_file)
    return f'{chat_id}.ogg'


def convert_to_ogg(path_to_file, chat_id):
    cmd = f'ffmpeg -i {path_to_file} -c:a libopus {chat_id}_to_ogg.ogg'
    exit_code = os.system(cmd)
    if not exit_code:
        return f'{chat_id}_to_ogg.ogg'
    else:
        return False


def upload_to_bucket(file_name):
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )
    s3.upload_file(file_name, 'bot-bucket', file_name)
    return s3


def request_to_yandex_ai(file_name):
    file_link = 'https://storage.yandexcloud.net/bot-bucket/{}'.format(file_name)
    template_post_request = "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"
    body ={
        "config": {
            "specification": {
                "languageCode": "ru-RU"
            }
        },
        "audio": {
            "uri": file_link
        }
    }
    header = {'Authorization': 'Api-Key {}'.format(service_key)}
    response = requests.post(template_post_request, headers=header, json=body).json()
    return response


def waiting_for_recognized_text(response_from_yandex_ai):
    request_id = response_from_yandex_ai['id']
    while True:
        time.sleep(2)
        template_get_request = "https://operation.api.cloud.yandex.net/operations/{}".format(request_id)
        header = {'Authorization': 'Api-Key {}'.format(service_key)}
        response = requests.get(template_get_request, headers=header).json()
        if response['done']:
            return response


def get_recognized_text(recognized_text):
    words = []
    for chunk in recognized_text['response']['chunks']:
        words.append(chunk['alternatives'][0]['text'])
    return ' '.join(words)


def delete_from_bucket(file_name, bucket):
    for_deletion = [{'Key':'object_name'}, {'Key': file_name}]
    bucket.delete_objects(Bucket='bot-bucket', Delete={'Objects': for_deletion})
    os.remove(file_name)


def get_time_processing(duration):
    return f'Мне понадобится где-то {duration} секунд на распознавание.\nКогда всё будет готово, я пришлю текст'