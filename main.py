import json
import requests
import time
import urllib
import config
from dbhelper import DBHelper
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import gdown
import zipfile, os
from threading import Thread
from SureBoT_main import executePipeline

TIMEOUT = config.timeout
TOKEN = config.token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
db = DBHelper()
LABELS = ['misinformation', 'politics', 'health care']
MODEL_DOWNLOAD_URL = config.model_download_url
MODEL_ZIP = config.model_zip
MODEL_FOLDER = config.model_folder


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def build_inline_keyboard(query):
    reply_markup = {"inline_keyboard": [[{"text": "Yes", "callback_data": "YES"},{"text": "No", "callback_data": "NO"}]]}
    return json.dumps(reply_markup)


"""
def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
"""


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


def setupDB():
    db.setup()


def initBERT():
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
    model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")
    global nlpClassify
    nlpClassify = pipeline(task='zero-shot-classification', tokenizer=tokenizer, model=model)
    print("BERT has been initialized")


def downloadModels():
    url = MODEL_DOWNLOAD_URL
    output = MODEL_ZIP
    try:
        if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + MODEL_FOLDER):
            print("Required models are already available")
        else:
            gdown.download(url, output, quiet=False)
            print("Creating zip file object")
            zip_ref = zipfile.ZipFile(output)  # createzipfileobject
            print("Extracting files to directory")
            zip_ref.extractall()  # extractfiletodir
            zip_ref.close()  # closefile
            print("Removing downloaded zip")
            os.remove(output)  # deletezippedfile
    except:
        print("Models were not downloaded")


def bertClassify(sequences):
    results = nlpClassify(sequences=sequences, candidate_labels=LABELS, multi_class=False)
    resultStr = json.dumps(results)
    return resultStr
