from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'licenses.json'

def load_licenses():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_licenses(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/activate', methods=['POST'])
def activate():
    req_data = request.get_json()
    code = req_data.get('code')
    device = req_data.get('device')

    if not code or not device:
        return jsonify({'status': 'error', 'message': 'Missing code or device'}), 400

    data = load_licenses()

    if code not in data:
        return jsonify({'status': 'error', 'message': 'Invalid activation code'}), 403

    if device in data[code]['devices']:
        return jsonify({'status': 'success', 'message': 'Device already activated'})

    if len(data[code]['devices']) >= 3:
        return jsonify({'status': 'error', 'message': 'Activation limit reached'}), 403

    data[code]['devices'].append(device)
    save_licenses(data)

    return jsonify({'status': 'success', 'message': 'Activation successful'})

@app.route('/check/<code>', methods=['GET'])
def check(code):
    data = load_licenses()
    if code not in data:
        return jsonify({'exists': False})
    return jsonify({'exists': True, 'devices': data[code]['devices']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
