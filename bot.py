import argparse
import environs
import logging
import requests
import telegram
from time import sleep


env = environs.Env()
env.read_env()

logger = logging.getLogger('bot_logger')
logger.setLevel(logging.WARNING)

devman_api_token = env('DEVMAN_TOKEN')
telegram_token = env('TELEGRAM_TOKEN')

dewman_api_url = 'https://dvmn.org/api/user_reviews/'
dewman_api_url_long = 'https://dvmn.org/api/long_polling/'


def send_message_from_bot(chat_id, response=None):
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


def bot_loop(
        url,
        token,
        chat_id,
        timeout=60,
        last_attempt_timestamp=None
):
    while True:
        try:
            headers = {'Authorization': f'Token {token}'}
            params = {'timestamp': last_attempt_timestamp}
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            if response:
                response = response.json()
                if response['status'] == 'timeout':
                    last_attempt_timestamp = response['timestamp_to_request']
                    continue
                last_attempt_timestamp = response['last_attempt_timestamp']
                attempts = response['new_attempts']
                for attempt in attempts:
                    send_message_from_bot(chat_id, response=attempt)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            logger.warning('Ошибка соединения с сервером')
            sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat_id')
    args = parser.parse_args()

    bot = telegram.Bot(token=telegram_token)

    bot_loop(
        url=dewman_api_url_long,
        token=devman_api_token,
        chat_id=args.chat_id,
    )
