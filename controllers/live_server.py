from flask import Flask, render_template
import threading
import os

def start_flask_debug_server(model, port=5000):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

    import logging
    log = logging.getLogger('werkzeug')
    log.disabled = True

    app = Flask(
        __name__,
        root_path=BASE_DIR,
        template_folder=TEMPLATE_DIR
    )

    @app.route("/")
    def index():
        return render_template("index.html", model=model)

    @app.route("/state")
    def state():
        return render_template("state.html", model=model)

    def run():
        app.run(port=port, debug=False, use_reloader=False, threaded=True)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    return thread



