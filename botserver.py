from flask import Flask
from flask import request
import json
import ModelsReference
from EvidenceRetrieval import loadPretrainedModels

from flask_celery import make_celery
from main import setupDB, downloadModels, send_message, build_inline_keyboard, answer_callback_query
from AfterResponseMiddleware import AfterThisResponse
from SureBoT_main import executePipeline

main_app = Flask(__name__, static_url_path='/static')
AfterThisResponse(main_app)
celery = make_celery(main_app)


@main_app.route('/', methods=["POST", "GET"])
def flaskHandler():
    try:
        print(request.data.decode('utf8'))
        update = request.data.decode('utf8')
        update = json.loads(update)
        handle_update(update)
    except ValueError:
        print('JSON Decoding has failed')
    return 'Displaying empty app'


def initCode():
    print('test is successful')
    setupDB()
    # initBERT()
    downloadModels()
    loadModels()


def loadModels():
    loadPretrainedModels()


def handle_update(update):
    try:
        if "message" in update:
            chat = update["message"]["chat"]["id"]
            if "text" in update["message"]:
                text = update["message"]["text"]
                if text == "/start":
                    send_message(
                        "Do you need to fact check any message? Copy and paste it in the chat and we will do the work for you!!",
                        chat)
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
                '''
                @main_app.after_this_response
                def post_process():
                    send_message(executePipeline(x), chat)
                    print("After pipeline execution")
                '''
                print('user choice is yes, starting post process')
                job = post_process.delay(x, chat, ModelsReference.PEGASUS_MODEL)
                print('The job id is: ' + job.id)
                answer_callback_query(callback_query_id, "Your query is being processed.....")
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
def post_process(query, chat, pegasusModel):
    print('Going to execute pipeline')
    query_result = executePipeline(query, pegasusModel)
    print("Query result obtained")
    with main_app.app_context():
        send_message(query_result, chat)
        print("After pipeline execution")


if __name__ == '__main__':
    print('Main is called')
    main_app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
