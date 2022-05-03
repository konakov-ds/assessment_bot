import argparse
import environs
import logging
import requests
import telegram
import os
from time import sleep


env = environs.Env()
env.read_env()

logger = logging.getLogger('bot_logger')

devman_api_token = env('DEVMAN_TOKEN')
telegram_token = env('TELEGRAM_TOKEN')

dewman_api_url = 'https://dvmn.org/api/user_reviews/'
dewman_api_url_long = 'https://dvmn.org/api/long_polling/'


class BotLogsHandler(logging.Handler):

    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        record_formated = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=record_formated)


def send_message_from_bot(bot, chat_id, response=None):
    if response:
        message_title = f'У вас проверили работу: "{response["lesson_title"]}"\n'
        if response['is_negative']:
            bot.send_message(
                chat_id=chat_id,
                text=f'{message_title}К сожалению в работе нашлись ошибки.'
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=f'{message_title}Преподавателю все понравилось, можно приступать'
                     f'к следующему уроку.'
            )


def run_bot(
        bot,
        url,
        token,
        chat_id,
        timeout=60,
        last_attempt_timestamp=None
):
    logger.warning('Бот запущен')
    headers = {'Authorization': f'Token {token}'}
    while True:
        params = {'timestamp': last_attempt_timestamp}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            response_content = response.json()
            if response_content['status'] == 'timeout':
                last_attempt_timestamp = response_content['timestamp_to_request']
                continue
            last_attempt_timestamp = response_content['last_attempt_timestamp']
            attempts = response_content['new_attempts']
            for attempt in attempts:
                send_message_from_bot(bot, chat_id, response=attempt)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logger.warning('Ошибка соединения с сервером')
            sleep(60)
        except telegram.error.TelegramError:
            logger.error('Сбой в telegram')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat_id', default=os.environ.get('chat_id'))
    args = parser.parse_args()

    tg_bot = telegram.Bot(token=telegram_token)

    logger.setLevel(logging.WARNING)
    logger.addHandler(BotLogsHandler(tg_bot, args.chat_id))

    run_bot(
        bot=tg_bot,
        url=dewman_api_url_long,
        token=devman_api_token,
        chat_id=args.chat_id,
    )
