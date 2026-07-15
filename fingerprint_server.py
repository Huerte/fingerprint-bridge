from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app, origins=[
    "https://cap.poolreno.com"
])


@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "device": "unknown"
    })


@app.route("/api/fingerprint/capture", methods=["POST"])
def capture():

    # Chipsailing SDK integration will go here

    return jsonify({
        "success": True,
        "message": "Capture endpoint ready",
        "template": None
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000
    )