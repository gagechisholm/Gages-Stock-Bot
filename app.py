from flask import Flask, jsonify
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/logs")
def get_logs():
    if not os.path.exists("app.log"):
        return jsonify({"logs": []}), 200
    with open("app.log") as f:
        logs = f.readlines()[-200:]
    return jsonify({"logs": logs})


if __name__ == "__main__":
    app.run()
