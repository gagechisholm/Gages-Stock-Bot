import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="frontend/dist", static_url_path="/")

@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")

# Catch-all route for Vue.js routing
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Heroku's assigned port or 5000 for local
    app.run(host="0.0.0.0", port=port)
