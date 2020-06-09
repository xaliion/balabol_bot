import telebot as tb
import requests
import logging
import api


bot = tb.TeleBot('937410305:AAEf-I48FEuMcjnK62YIwriUYFka4f8hLMU', threaded=False)
bot_logger = logging.getLogger('bot')
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n',
                    datefmt='%d.%m.%Y %H:%M')



@bot.message_handler(commands=['start'])
def say_hello(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}.\nЯ умею переводить голосовые сообщения и аудио в текст.\nДля этого отправь мне что-то из этого')


@bot.message_handler(content_types=['text', 'document', 'photo', 'sticker', 'video',
                                    'video_note', 'location', 'contact'])
def handle_other_types(message):
    bot_logger.info('message of the wrong type, standard response')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIBYF7fYmW6cnBBkjRBxtpKtxmuoUmmAAK4AANXTxUIhTZakrqH0UYaBA')


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_name = api.get_audio_from_user(bot, message.chat.id, message.voice.file_id)
    bucket_client = api.upload_to_bucket(file_name)
    bot.send_message(message.chat.id, api.get_time_processing(message.voice.duration))
    bot_logger.info(f'voice message processing, approximate processing time - {message.voice.duration} seconds')
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
    bot.send_message(message.chat.id, api.get_time_processing(message.voice.duration))
    bot_logger.info(f'voice message processing, approximate processing time - {message.voice.duration} seconds')
    response_from_yandex = api.request_to_yandex_ai(file_name)
    source_recognized_text = api.waiting_for_recognized_text(response_from_yandex)
    recognized_text = api.get_recognized_text(source_recognized_text)
    bot.send_message(message.chat.id, recognized_text)
    api.delete_from_bucket(file_name, bucket_client)


try:
    bot.polling()
except:
    bot_logger.exception('Error starting bot, restart docker container')

