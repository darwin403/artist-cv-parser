import os
import time
from pathlib import Path

from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort,
)
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

from core.process import Parser
from core.convert import web2pdf

# Static variables
STATIC_FOLDER = "static"
UPLOAD_FOLDER = (Path(__file__).parent / STATIC_FOLDER / "uploads").absolute()
FILE_PATH = "{uploads}/{filename}".format(
    uploads=str(UPLOAD_FOLDER), filename="{filename}"
)
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "png"]

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
    # get artist info
    name = request.form.get("name")
    email = request.form.get("email")
    is_artist = request.form.get("is_artist")

    # bad request
    if not name or not email or not is_artist:
        return abort(400)

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

    return redirect(
        url_for(
            "process",
            filename=filename,
            name=name if name else None,
            email=email if email else None,
            is_artist=is_artist if is_artist else None,
        )
    )


# Process file
@app.route("/process/<filename>", methods=["GET"])
def process(filename):
    # get artist info
    name = request.args.get("name")
    email = request.args.get("email")
    is_artist = request.args.get("is_artist")

    # bad request
    if not name or not email or not is_artist:
        return abort(400)

    return render_template(
        "result.jinja2", filename=filename, name=name, email=email, is_artist=is_artist
    )


# Declare socket
socketio = SocketIO(app)


# Process job
@socketio.on("job:start")
def job_start(job):
    # bad request
    if not job.get("name") or not job.get("email") or not job.get("is_artist"):
        emit(
            "job:done", {"status": "Artist's name, email or identity is not provided."}
        )
        return

    filename = job.get("filename")
    filepath = UPLOAD_FOLDER / filename

    # check if file exists
    if not os.path.isfile(filepath):
        emit("job:done", {"status": "%s does not exist." % filename})
        return

    # save user info
    meta = {
        "input": {
            "name": job.get("name"),
            "email": job.get("email"),
            "is_artist": True,
        },
        "ip": job.get("ip"),
    }

    # parse cv
    parser = Parser(meta=meta, emit=emit)
    result = parser.process_cv(filepath)

    # file processing done
    emit("job:done", {"status": "%s processed." % filename})


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=os.environ.get("PORT", 5000))
