import environs
import requests


env = environs.Env()
env.read_env()


devman_api_token = env('DEVMAN_TOKEN')
