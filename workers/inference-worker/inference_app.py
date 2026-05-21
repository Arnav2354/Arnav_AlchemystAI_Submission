from flask import Flask, request, jsonify

app = Flask(__name__)

# inference worker - runs on private subnet (10.0.2.244:5000)
# only accessible from caller worker, not from internet

@app.route('/inference', methods=['POST'])
def run_inference():
    body = request.get_json()
    if not body:
        return jsonify({"error": "no body"}), 400
    
    msgs = body.get('messages', [])
    last_msg = ""
    for m in msgs:
        if m.get('role') == 'user':
            last_msg = m.get('content', '')
    
    # TODO: replace with actual gemma model once KVM is available
    # iii-sdk requires KVM which t3.micro doesnt support
    result = {
        "role": "assistant",
        "content": f"got your message: {last_msg}"
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
