from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# private ip of inference worker
INFERENCE_HOST = os.environ.get('INFERENCE_HOST', '10.0.2.244')
INFERENCE_PORT = os.environ.get('INFERENCE_PORT', '5000')
INFERENCE_URL = f"http://{INFERENCE_HOST}:{INFERENCE_PORT}/inference"

@app.route('/v1/chat/completions', methods=['POST'])
def handle_request():
    body = request.get_json()
    if not body:
        return jsonify({"error": "request body missing"}), 400
    
    try:
        resp = requests.post(INFERENCE_URL, json=body, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "could not reach inference worker"}), 502
    except requests.exceptions.Timeout:
        return jsonify({"error": "inference worker timed out"}), 504
    
    return jsonify({
        "id": "chatcmpl-001",
        "object": "chat.completion",
        "choices": [{
            "message": resp.json(),
            "finish_reason": "stop",
            "index": 0
        }]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
