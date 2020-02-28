import json
import os.path
from os import path


    


def get_secret(secret_name):
    if not (path.exists('secrets.json')):
        print('No secrets found, lets create them.')
        create_secrets()
    with open('secrets.json', 'r') as fp:
        secret = json.load(fp)
        return secret[secret_name]


def create_secrets():
    secrets = {}
    C_ID = input('Enter Spotify Client ID:\n')
    C_SCT = input('Enter Spotify Client Secret:\n')
    GOOGLE_API = input('Enter Google API key:\n')
    secrets['C_ID'] = C_ID
    secrets['C_SCT'] = C_SCT
    secrets['GOOGLE_API'] = GOOGLE_API
    with open('secrets.json', 'w') as fp:
        json.dump(secrets, fp)


if __name__ == "__main__":
    print('Lets create our secrets.json file.')
    secrets = {}
    C_ID = input('Enter Spotify Client ID:\n')
    C_SCT = input('Enter Spotify Client Secret:\n')
    GOOGLE_API = input('Enter Google API key:\n')
    secrets['C_ID'] = C_ID
    secrets['C_SCT'] = C_SCT
    secrets['GOOGLE_API'] = GOOGLE_API
    with open('secrets.json', 'w') as fp:
        json.dump(secrets, fp)
    if not (path.exists('client_secret.json')):
        print('"client_secret.json" not found (from Google). Make sure it is in this directory.')