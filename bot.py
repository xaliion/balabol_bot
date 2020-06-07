import telebot as tb
import requests
import api


bot = tb.TeleBot('937410305:AAEf-I48FEuMcjnK62YIwriUYFka4f8hLMU', threaded=False)


@bot.message_handler(content_types=['text'])
def test(message):
    bot.send_message(message.chat.id, 'очень большие сиськи и очень большие жопы')


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_name = api.get_audio_from_user(bot, message.chat.id, message.voice.file_id)
    bucket_client = api.upload_to_bucket(file_name)
    bot.send_message(message.chat.id, api.get_time_processing(message.voice.duration))
    response_from_yandex = api.request_to_yandex_ai(file_name)
    source_recognized_text = api.waiting_for_recognized_text(response_from_yandex)
    recognized_text = api.get_recognized_text(source_recognized_text)
    bot.send_message(message.chat.id, recognized_text)
    api.delete_from_bucket(file_name, bucket_client)


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    file_name = api.get_audio_from_user(bot, message.chat.id, message.audio.file_id)
    file_name = api.convert_to_ogg(file_name, message.chat.id)
    bucket_client = api.upload_to_bucket(file_name)
    bot.send_message(message.chat.id, api.get_time_processing(message.audio.duration))
    response_from_yandex = api.request_to_yandex_ai(file_name)
    source_recognized_text = api.waiting_for_recognized_text(response_from_yandex)
    recognized_text = api.get_recognized_text(source_recognized_text)
    bot.send_message(message.chat.id, recognized_text)
    api.delete_from_bucket(file_name, bucket_client)


bot.polling()
