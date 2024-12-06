from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open("app.log", "r") as log_file:
            logs = log_file.readlines()
        return jsonify({"logs": logs})
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
                const res = await fetch('/logs');
                const data = await res.json();
                document.getElementById('logs').textContent = data.logs.join('\\n');
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(port=5000)
