from flask import Flask, jsonify
import json
import uuid

app = Flask(__name__)
LICENSE_FILE = "licenses.json"

def load_licenses():
    try:
        with open(LICENSE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_licenses(licenses):
    with open(LICENSE_FILE, "w") as f:
        json.dump(licenses, f, indent=4)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the license API"})

@app.route("/check/<license_key>")
def check_license(license_key):
    licenses = load_licenses()
    license_data = licenses.get(license_key)

    if not license_data:
        return jsonify({"exists": False}), 200

    return jsonify({
        "exists": True,
        "bind_count": len(license_data["devices"]),
        "max_binds": license_data["max_devices"]
    })

@app.route("/activate/<license_key>")
def activate_license(license_key):
    from flask import request

    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"success": False, "error": "Missing device_id"}), 400

    licenses = load_licenses()
    license_data = licenses.get(license_key)

    if not license_data:
        return jsonify({"success": False, "error": "License not found"}), 404

    if device_id in license_data["devices"]:
        return jsonify({"success": True, "message": "Already activated"}), 200

    if len(license_data["devices"]) >= license_data["max_devices"]:
        return jsonify({"success": False, "error": "Activation limit reached"}), 403

    license_data["devices"].append(device_id)
    save_licenses(licenses)

    return jsonify({"success": True, "message": "Activation successful"}), 200

if __name__ == "__main__":
    app.run(debug=True)
