from flask import Flask, render_template, make_response, Response
from flask import request
import json
from main import handle_update
from main import setupDB
from main import initBERT
from main import downloadModels
import multiprocessing
import gunicorn.app.base
from six import iteritems

main_app = Flask(__name__, static_url_path='/static')


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
    initBERT()
    downloadModels()


#if __name__ == '__main__':
#    main_app.run(debug=True, host='0.0.0.0', port=5000)


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('0.0.0.0', '5000'),
        'workers': number_of_workers(),
        'daemon': True
    }

    print("Calling init code")
    initCode()
    print("Code initialization has successfully completed")

    # Modification 3: pass Flask app instead of handler_app
    StandaloneApplication(main_app, options).run(debug=True, host='0.0.0.0', port=5000)
