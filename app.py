from flask import Flask, send_from_directory
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
