import json

from flask import Flask, Response

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    thread = app.config["thread"]
    if thread and thread.is_alive():
        return Response(
            json.dumps({"Status": "OK"}),
            status=200,
            mimetype="application/json",
        )
    else:
        return Response(
            json.dumps({"Status": "Error"}),
            status=426,
            mimetype="application/json",
        )


def run_health():
    app.run(port=80, host="0.0.0.0")


def set_thread(thread):
    app.config["thread"] = thread
