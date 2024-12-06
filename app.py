from flask import Flask, jsonify
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

app = Flask(__name__)

@app.after_request
def disable_caching(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/logs', methods=['GET'])
def get_logs():
    if not os.path.exists("app.log"):
        return jsonify({"logs": ["Log file not found."]})
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.readlines()[-100:]  # Fetch the last 100 lines
        return jsonify({"logs": logs}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Logs</title></head>
    <body>
        <h1>Logs Viewer</h1>
        <button onclick="fetchLogs()">Refresh Logs</button>
        <pre id="logs"></pre>
        <script>
            async function fetchLogs() {
                try {
                    const res = await fetch('/logs');
                    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                    const data = await res.json();
                    if (data.logs) {
                        document.getElementById('logs').textContent = data.logs.join('\\n');
                    } else if (data.error) {
                        document.getElementById('logs').textContent = `Error: ${data.error}`;
                    }
                } catch (error) {
                    document.getElementById('logs').textContent = `Fetch error: ${error.message}`;
                }
            }
            window.onload = fetchLogs;
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    try:
        app.run(host="0.0.0.0", port=port)
    except OSError as e:
        logging.error(f"Port {port} is already in use. Please choose a different port.")
        sys.exit(1)
