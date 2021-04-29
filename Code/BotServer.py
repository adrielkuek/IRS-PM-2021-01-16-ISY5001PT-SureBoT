"""
Bot server implemented using Flask (Python Web Framework)
"""

from flask import Flask
from flask import request
import json
from celery.exceptions import SoftTimeLimitExceeded
import nltk

from flask_celery import make_celery
from BotHelper import downloadModels, send_message, build_inline_keyboard, answer_callback_query
from SureBoT_main import executePipeline, configure_logger

main_app = Flask(__name__, static_url_path='/static')
celery = make_celery(main_app)
celery.config_from_object('celery_config')
n = 10

@main_app.route('/', methods=["POST", "GET"])
def flaskHandler():
    try:
        print(request.data.decode('utf8'))
        update = request.data.decode('utf8')
        update = json.loads(update)
        handle_update(update)
    except ValueError:
        print('JSON Decoding has failed')
    return 'This is a Telegram Bot Server.'


def getApp():
    print("Calling function to initialize")
    initCode()
    print("Code initialization has successfully completed")
    return main_app


def initCode():
    nltk.download('punkt')
    downloadModels()


def handle_update(update):
    try:
        if "message" in update:
            chat = update["message"]["chat"]["id"]
            if "text" in update["message"]:
                text = update["message"]["text"]
                if text == "/start":
                    send_message(
                        "Hi! Thanks for using SureBoT!\nDo you need to fact-check a message? Copy and paste it in the chat to get started.",
                        chat)
                    '''
                elif text == "/debugCelery":
                    send_message("(DEBUG MODE) Fetching Celery Worker Log...", chat)
                    filehandle = open('celery_log.log', 'r')
                    while True:
                        # read a single line
                        # for i in range(n):
                        line = filehandle.readline()
                        for i in range(n):
                            if not line:
                                break
                            line += filehandle.readline()
                        if not line:
                            break
                        send_message(line, chat)
                    filehandle.close()
                elif text == "/debugIBPU":
                    send_message("(DEBUG MODE) Fetching Log from IBPU...", chat)
                    logfile = f'./SurebotLog/chat_{str(chat)}.log'
                    filehandle = open(logfile, 'r')
                    while True:
                        # read a single line
                        # for i in range(n):
                        line = filehandle.readline()
                        for i in range(n):
                            if not line:
                                break
                            line += filehandle.readline()
                        if not line:
                            break
                        send_message(line, chat)
                    filehandle.close()
                elif text == "/debugGunicorn":
                    send_message("(DEBUG MODE) Fetching Gunicorn log...", chat)
                    filehandle = open('gunicorn_log.log', 'r')
                    gunicornlog = filehandle.read()
                    filehandle.close()
                    # Return latest logs only (Max length 4096 chars)
                    send_message(gunicornlog[-4096:], chat)
                    '''
                elif text.startswith("/"):
                    return
                else:
                    output = '*Do you want to fact check below message?*\n\n' + text
                    send_message(output, chat, build_inline_keyboard(text))
            else:
                send_message("Please send only text messages.", chat)
        elif "callback_query" in update:
            callback_query_id = update["callback_query"]["id"]
            data = update["callback_query"]["data"]
            chat = update["callback_query"]["message"]["chat"]["id"]
            text = update["callback_query"]["message"]["text"]
            x = text.split("Do you want to fact check below message?\n\n", 1)[1]
            print("Split text is: " + x)
            if data == 'YES':
                print('User choice is yes, starting post process')
                job = post_process.delay(x, chat)
                print('The job id is: ' + job.id)
                answer_callback_query(callback_query_id, "Your query is being processed.....")
                if get_celery_queue_len('celery') > 0:
                    message = 'Your request has been received and is no. {} in queue. Please wait.....'.format(str(get_celery_queue_len('celery')))
                else:
                    message = 'Your request is currently being processed. Please wait.....'
                send_message(message, chat)
            else:
                answer_callback_query(callback_query_id,
                                      "Please click Yes if you want your message to be fact checked.")

    except Exception as e:
        message = 'Exception occurred while processing'
        print(message)
        print(e)
        if chat:
            send_message(message, chat)


@celery.task(name='botserver.post_process')
def post_process(query, chat):
    try:
        print('Generating Logs')
        chat_string = str(chat)
        surebot_logger = configure_logger(chat_string)
        print('Executing pipeline')
        query_result = executePipeline(query, surebot_logger)
        print("Query result obtained")
        with main_app.app_context():
            send_message(query_result, chat)
            print("After pipeline execution")
    except SoftTimeLimitExceeded:
        with main_app.app_context():
            send_message('Sorry, your query took too long to process.', chat)
            print("Pipeline execution for query exceeded 360 seconds")


def get_celery_queue_len(queue_name):
    with celery.pool.acquire(block=True) as conn:
        return conn.default_channel.client.llen(queue_name)


if __name__ == '__main__':
    print('Main is called')
    main_app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
