# Automated webhook setup

import requests
from pyngrok import ngrok
import bot_config

# Create HTTP Tunnel
TOKEN = bot_config.token
print(f'BOT TOKEN: {TOKEN}')
webhook = ngrok.connect(80, bind_tls=True).public_url
print(f'WEBHOOK: {webhook}')

URL = "https://api.telegram.org/bot{}/setWebhook?url={}".format(TOKEN, webhook)
print(URL)
result = requests.post(URL)

print(result)

print(f'Bot will initiate shortly, ctrl-c to terminate process')

while True:
    pass