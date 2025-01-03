from flask import Flask, jsonify, send_from_directory
import logging
import os

app = Flask(__name__, static_folder="frontend/dist", static_url_path="")

@app.route("/")
def serve():
    # Serve the index.html for the root URL
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def catch_all(path):
    # Serve files if they exist; otherwise, serve index.html for Vue.js routing
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
            logs = log_file.readlines()[-100:]  # Fetch last 100 lines
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Set up logging
if not os.path.exists("app.log"):
    open("app.log", "w").close()  # Create the file if it doesn't exist

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Application started!")