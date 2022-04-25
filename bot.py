import environs
import requests


env = environs.Env()
env.read_env()


devman_api_token = env('DEVMAN_TOKEN')
dewman_api_url = 'https://dvmn.org/api/user_reviews/'


def get_user_assessments(url, token):
    headers = {'Authorization': f'Token {devman_api_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


print(get_user_assessments(dewman_api_url, devman_api_token))
