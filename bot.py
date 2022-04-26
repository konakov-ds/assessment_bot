import environs
import requests
import telegram
from time import sleep


env = environs.Env()
env.read_env()


devman_api_token = env('DEVMAN_TOKEN')
telegram_token = env('TELEGRAM_TOKEN')
chat_id = '166898548'
dewman_api_url = 'https://dvmn.org/api/user_reviews/'
dewman_api_url_long = 'https://dvmn.org/api/long_polling/'


def get_user_assessments(url, token, timestamp, timeout=60, params=None):
    headers = {'Authorization': f'Token {token}'}
    if timestamp:
        params = {'timestamp': timestamp}
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def send_message_from_bot(chat_id, response=None):
    bot = telegram.Bot(token=telegram_token)
    if response:
        bot.send_message(chat_id=chat_id, text='Преподаватель проверил работу!')


def loop(last_attempt_timestamp=None):
    while True:
        try:
            response = get_user_assessments(
                dewman_api_url_long,
                devman_api_token,
                timestamp=last_attempt_timestamp,
                timeout=20
            )
            if response:
                last_attempt_timestamp = response['last_attempt_timestamp']
                send_message_from_bot(chat_id, response=response)
                loop(last_attempt_timestamp)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            sleep(10)
            loop(last_attempt_timestamp)

loop()
