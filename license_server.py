from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

LICENSE_FILE = "licenses.json"
MAX_ACTIVATIONS = 3

# 加载激活码数据
def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}
    with open(LICENSE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 保存激活码数据
def save_licenses(data):
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route("/activate/<code>", methods=["GET"])
def activate(code):
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"status": "error", "message": "缺少 device_id 参数"}), 400

    licenses = load_licenses()

    # 激活码不存在
    if code not in licenses:
        return jsonify({"status": "error", "message": "无效激活码"}), 404

    license_info = licenses[code]
    devices = license_info.get("devices", [])

    # 设备已激活
    if device_id in devices:
        return jsonify({"status": "success", "message": "设备已激活", "code": code})

    # 超过激活次数
    if len(devices) >= MAX_ACTIVATIONS:
        return jsonify({"status": "error", "message": f"该激活码已达到最大激活数（{MAX_ACTIVATIONS}台）"}), 403

    # 新增设备
    devices.append(device_id)
    license_info["devices"] = devices
    license_info["last_activated"] = datetime.utcnow().isoformat()

    licenses[code] = license_info
    save_licenses(licenses)

    return jsonify({"status": "success", "message": "激活成功", "code": code, "device_id": device_id})

# Flask 启动
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
