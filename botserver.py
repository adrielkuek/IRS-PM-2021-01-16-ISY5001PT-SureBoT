from flask import Flask
from flask import request
import json
from main import setupDB, downloadModels, send_message, build_inline_keyboard, answer_callback_query
from AfterResponseMiddleware import AfterThisResponse
from SureBoT_main import executePipeline

main_app = Flask(__name__, static_url_path='/static')
AfterThisResponse(main_app)


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


def handle_update(update):
    try:
        if "message" in update:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            if text == "/start":
                send_message("To Test Zero-Shot-Learning Classification Model with labels[misinformation, politics, "
                         "health care], Send /classify with your text ", chat)
            elif text.startswith("/pipeline"):
                x = text.split("/pipeline ", 1)[1]
                send_message('Your query is being processed.....', chat)
            elif text.startswith("/test"):
                x = text.split("/pipeline ", 1)[1]
                send_message('Click on yes or no: ', chat, build_inline_keyboard(x))
            elif text.startswith("/"):
                return
            else:
                message = "The message entered is " + text
                send_message(message, chat)
        elif "callback_query" in update:
            callback_query_id = update["callback_query"]["id"]
            data = update["callback_query"]["data"]
            chat = update["callback_query"]["message"]["chat"]["id"]
            @main_app.after_this_response
            def post_process():
                send_message(executePipeline(data), chat)
                print("after_response")
            answer_callback_query(callback_query_id, "Your query is being processed.....")
    except:
        message = 'Exception occurred while processing'
        print(message)
        send_message(message, chat)


if __name__ == '__main__':
    main_app.run(debug=True, host='0.0.0.0', port=5000)
