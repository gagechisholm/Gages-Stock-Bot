from flask import Flask, jsonify, send_from_directory, request
import logging
import os
from logging.handlers import RotatingFileHandler

app = Flask(__name__, static_folder="frontend/dist", static_url_path="")

# Logging setup
if not os.path.exists("app.log"):
    open("app.log", "w").close()

handler = RotatingFileHandler("app.log", maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app.logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app.logger.addHandler(console_handler)

app.logger.setLevel(logging.DEBUG if os.getenv("FLASK_ENV") == "development" else logging.INFO)

@app.before_request
def log_request_info():
    app.logger.debug(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    app.logger.debug(f"Response: {response.status} for {request.method} {request.url}")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.exception(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def catch_all(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.route("/logs", methods=["GET"])
def get_logs():
    if not os.path.exists("app.log"):
        return jsonify({"logs": ["Log file not found."]}), 404
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.readlines()[-100:]
        return jsonify({"logs": logs}), 200
    except Exception as e:
        app.logger.exception("Error fetching logs")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.logger.info("Starting Flask app")
    app.run()
