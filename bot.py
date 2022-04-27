import argparse
import environs
import requests
import telegram
from time import sleep


env = environs.Env()
env.read_env()


devman_api_token = env('DEVMAN_TOKEN')
telegram_token = env('TELEGRAM_TOKEN')

dewman_api_url = 'https://dvmn.org/api/user_reviews/'
dewman_api_url_long = 'https://dvmn.org/api/long_polling/'


def send_message_from_bot(chat_id, response=None):
    bot = telegram.Bot(token=telegram_token)
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
        timeout=30,
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
                last_attempt_timestamp = response['last_attempt_timestamp']
                attempts = response['new_attempts']
                for attempt in attempts:
                    send_message_from_bot(chat_id, response=attempt)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat_id')
    args = parser.parse_args()

    bot_loop(
        url=dewman_api_url_long,
        token=devman_api_token,
        chat_id=args.chat_id,
    )
