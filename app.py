from flask import Flask, jsonify, send_from_directory
import os
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__, static_folder="frontend/dist", static_url_path="")

@app.route("/logs", methods=["GET"])
def get_logs():
    if not os.path.exists("app.log"):
        return jsonify({"logs": ["Log file not found."]})
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.readlines()[-100:]  # Fetch the last 100 lines
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(host="0.0.0.0", port=port)
    except OSError as e:
        logging.error(f"Port {port} is already in use. Please choose a different port.")
        sys.exit(1)
