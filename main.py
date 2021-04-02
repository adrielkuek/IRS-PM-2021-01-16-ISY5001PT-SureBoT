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

TIMEOUT = config.timeout
TOKEN = config.token
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
db = DBHelper()
LABELS = ['misinformation', 'politics', 'health care']


def handle_update(update):
    text = update["message"]["text"]
    chat = update["message"]["chat"]["id"]
    items = db.get_items(chat)
    if text == "/done":
        keyboard = build_keyboard(items)
        send_message("Select an item to delete", chat, keyboard)
    elif text == "/start":
        send_message("Welcome to your personal To Do list. Send any text to me and I'll store it as an item. Send "
                     "/done to remove items", chat)
        send_message("To Test Zero-Shot-Learning Classification Model with labels[misinformation, politics, "
                     "health care], Send /classify with your text ", chat)
    elif text.startswith("/classify"):
        x = text.split("/classify ", 1)[1]
        send_message(bertClassify(x), chat)
    elif text.startswith("/"):
        return
    elif text in items:
        db.delete_item(text, chat)
        items = db.get_items(chat)
        keyboard = build_keyboard(items)
        send_message("Select an item to delete", chat, keyboard)
    else:
        db.add_item(text, chat)
        items = db.get_items(chat)
        message = "\n".join(items)
        send_message(message, chat)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
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
    return content


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
    get_url(url)


def setupDB():
    db.setup()


def initBERT():
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
    model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")
    global nlpClassify
    nlpClassify = pipeline(task='zero-shot-classification', tokenizer=tokenizer, model=model)
    print("BERT has been initialized")


def downloadModels():
    url = 'https://drive.google.com/uc?id=14cNpXSCiN0Wv1rcQYOjyzmty3RqOQYwC'
    output = 'pipeline_models.zip'
    gdown.download(url, output, quiet=False)

    zip_ref = zipfile.ZipFile(output)  # createzipfileobject
    zip_ref.extractall()  # extractfiletodir
    zip_ref.close()  # closefile
    os.remove(output)  # deletezippedfile


def bertClassify(sequences):
    results = nlpClassify(sequences=sequences, candidate_labels=LABELS, multi_class=False)
    resultStr = json.dumps(results)
    return resultStr