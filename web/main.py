import typing

from flask import Flask, request, jsonify, g
import json
import hashlib

from db import MongoManager, DBManager

app = Flask(__name__)


@app.route("/sensor/add", methods=['POST'])
def add_sensor_record():
    record = json.loads(request.get_data())
    m = hashlib.md5()
    m.update(record["sensor_data"].encode('utf-8'))
    record['hash'] = m.hexdigest()[:30]

    status: bool = g.dbmanager.insert(record)
    if status:
        return jsonify({"status": status}), 201
    else:
        return jsonify({"error": "operation failed."}), 400


@app.route("/sensor/query/<int:page>")
def query_sensor_record(page):
    result: typing.Union[typing.List[dict], None] = g.dbmanager.query(page)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "operation failed."}), 400


if __name__ == "__main__":
    g.dbmanager = MongoManager()
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=False, port=80)
