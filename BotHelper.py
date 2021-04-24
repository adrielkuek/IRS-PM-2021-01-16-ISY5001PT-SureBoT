"""
Helper class for the Bot server to handle Telegram requests
"""

import json
import requests
import urllib
import bot_config
import gdown
import zipfile, os

TIMEOUT = bot_config.timeout
TOKEN = bot_config.token
URL = bot_config.telegram_base_url.format(TOKEN)
MODEL_DOWNLOAD_URL = bot_config.model_download_url
MODEL_ZIP = bot_config.model_zip
MODEL_FOLDER = bot_config.model_folder


def build_inline_keyboard(query):
    reply_markup = {"inline_keyboard": [[{"text": "Yes", "callback_data": "YES"},{"text": "No", "callback_data": "NO"}]]}
    return json.dumps(reply_markup)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    code = response.status_code
    return code


def send_message(text, chat_id, reply_markup=None):
    print(text)
    try:
        text = urllib.parse.quote_plus(text)
        url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
    except:
        url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format("Exception occurred", chat_id)
        print("Exception occurred")

    status = get_url(url)
    if status == 400:
        url = url.replace('Markdown', 'html')
        get_url(url)


def answer_callback_query(query_id, text):
    print('callback_query_called')
    try:
        text = urllib.parse.quote_plus(text)
        url = URL + "answerCallbackQuery?callback_query_id={}&text={}&show_alert=false".format(query_id, text)
        get_url(url)
    except:
        print("Exception occurred while processing callback query")


def downloadModels():
    url = MODEL_DOWNLOAD_URL
    output = MODEL_ZIP
    try:
        if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + MODEL_FOLDER):
            print("Required models are already available")
        else:
            gdown.download(url, output, quiet=False)
            print("Creating zip file object")
            zip_ref = zipfile.ZipFile(output)  # create zipfile object
            print("Extracting files to directory")
            zip_ref.extractall()  # extract file to dir
            zip_ref.close()  # close file
            print("Removing downloaded zip")
            os.remove(output)  # delete zipped file
    except:
        print("Models were not downloaded")
