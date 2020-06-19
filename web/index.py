import os
import time
from pathlib import Path

from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from core.process import Parser

UPLOAD_FOLDER = Path(__file__).parent / "static/uploads"

# create upload folder if does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        # save file
        cv = request.files["cv"]
        filename = secure_filename(cv.filename)
        filepath = UPLOAD_FOLDER / filename
        cv.save(filepath)

        # process cv
        return render_template("result.html", filename=filename)
    else:
        return render_template("index.html")


@socketio.on("job:start")
def job_start(filename):
    filepath = (UPLOAD_FOLDER / filename).absolute()

    # check if file exists
    if not os.path.isfile(filepath):
        emit("job:message", "%s does not exist." % filename)
        return

    parser = Parser(emit=emit)
    parser.process_cv(filepath)

    # remove file after processing
    os.remove(filepath)
    emit("job:message", "%s job completed." % filename)


if __name__ == "__main__":
    # app.run(debug=True, threaded=False)
    socketio.run(app, debug=True, port=1234)
