from flask import Flask, render_template
import json

class Web(object):
    def __init__(self):
        pass

    def start(self):
        app = Flask(__name__)
        
        @app.route('/api/getsessions')
        def state():
            with open("./data/sessions.txt") as f:
                data = json.load(f)
                f.close()
                return data
        
        @app.route('/')
        def panel():
            return render_template("index.html")

        app.run(host="0.0.0.0", port=8080)