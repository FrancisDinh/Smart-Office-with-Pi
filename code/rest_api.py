from flask import Flask
from flask_cors import CORS, cross_origin
from bson.json_util import dumps
from lib import mongodb, rabbitmq


app = Flask(__name__)
CORS(app)
mdb = mongodb.MongoDB()
rmq = rabbitmq.RabbitMQ()


@cross_origin()
@app.route("/api/sensors/<name>", methods=['GET'])
def sensors_one(name):
    return dumps(mdb.retrieve_most_recent(name)[0])


@cross_origin()
@app.route("/api/sensors/<name>/<limit>", methods=['GET'])
def sensors_limit(name, limit):
    return dumps(mdb.retrieve_most_recent(name, int(limit)))


@cross_origin()
@app.route("/api/sensors/available", methods=['GET'])
def sensors_available():
    return dumps(mdb.retrieve_available())


@cross_origin()
@app.route("/api/modes/<mode>", methods=['GET'])
def mode_day(mode):
    rmq.send('sensors.mode', str(mode))
    return '{ "mode": "' + mode + '" }'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
