from flask import Flask
from flask import request
import json
from main import handle_update
from main import setupDB
from main import initBERT
from main import downloadModels
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

        @main_app.after_this_response
        def post_process():
            executePipeline('A bus driver has been arrested for careless driving')
            print("after_response")

    except ValueError:
        print('JSON Decoding has failed')
    return 'Displaying empty app'


def initCode():
    print('test is successful')
    setupDB()
    # initBERT()
    downloadModels()


if __name__ == '__main__':
    main_app.run(debug=True, host='0.0.0.0', port=5000)
