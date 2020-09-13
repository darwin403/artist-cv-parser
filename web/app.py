import os
import time
from pathlib import Path

from flask import (
    Flask,
    Response,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from core.convert import web2pdf
from core.process import Parser
from flask_socketio import SocketIO, emit

from config import AWS_BUCKET_NAME, AWS_REGION_NAME

# Static variables
STATIC_FOLDER = "static"
UPLOAD_FOLDER = (Path(__file__).parent / STATIC_FOLDER / "uploads").absolute()
FILE_PATH = "{uploads}/{filename}".format(
    uploads=str(UPLOAD_FOLDER), filename="{filename}"
)

# Create upload folder if does not exist
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Declare flask
app = Flask(__name__)
app.static_folder = STATIC_FOLDER


# Homepage
@app.route("/", methods=["GET"])
def home():
    return render_template("home.jinja2")


# Save file
@app.route("/save", methods=["POST"])
def save():
    cv = request.files["cv"]
    url = request.form["url"]

    # save pdf cv
    if cv:
        filename = secure_filename(cv.filename)
        filepath = FILE_PATH.format(filename=filename)
        cv.save(filepath)

    # save web cv
    else:
        filename = secure_filename(url) + ".pdf"
        filepath = FILE_PATH.format(filename=filename)
        web2pdf(url, filepath)

    return redirect(url_for("process", filename=filename))


# Process file
@app.route("/process/<filename>", methods=["GET"])
def process(filename):
    return render_template(
        "result.jinja2",
        filename=filename,
        bucket_name=AWS_BUCKET_NAME,
        bucket_region=AWS_REGION_NAME,
    )


# Declare socket
socketio = SocketIO(app)


# Process job
@socketio.on("job:start")
def job_start(job):
    filename = job.get("filename")
    filepath = UPLOAD_FOLDER / filename

    # check if file exists
    if not os.path.isfile(filepath):
        emit("job:done", {"status": "%s does not exist." % filename})
        return

    # parse cv
    parser = Parser(emit=emit)
    print ('FILEEEEEEEEEEEEEPATH:', filepath)
    print ('EMITTTTTTTTTTTT:', emit)
    parser.process_cv(filepath)

    # file processing done
    emit("job:done", {"status": "%s processed." % filename})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=os.environ.get("PORT", 5000))
