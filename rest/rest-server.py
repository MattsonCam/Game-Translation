import io
from flask import send_file, request, Flask, jsonify, Response
from minio import Minio
import uuid
import redis
import base64
import json
import jsonpickle
from minio import Minio
import os

app = Flask(__name__)
bucket_name = 'mp3files'
#redis_server = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)
#min_server = Minio(os.getenv('MINIO_HOST', 'localhost:9000'), access_key='rootuser', secret_key='rootpass123', secure=False)

@app.route('/apiv1/translate/<string:translations>', methods=['GET', 'POST'])
def process_translations(translations):
    response = {'translation' : translations}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")
    """
    songhash = str(uuid.uuid4())
    modhash = f"{songhash}.mp3"
    json_req = request.json
    task_info = {'songhash': songhash, 'callback': json_req.get('callback')}
    
    if not min_server.bucket_exists(bucket_name):
        min_server.make_bucket(bucket_name)

    mp3_enc = base64.b64decode(json_req.get('mp3'))
    min_server.put_object(bucket_name, modhash, io.BytesIO(mp3_enc), len(mp3_enc))
    redis_server.lpush('toWorker', json.dumps(task_info))

    return jsonify(hash=songhash, reason="Song enqueued for separation")
    """
"""
@app.route('/apiv1/queue/', methods=['GET'])
def get_queue():
    queue = redis_server.lrange('toWorker', 0, -1)
    return jsonify(queue=[json.loads(i) for i in queue])

@app.route('/apiv1/track/<songhash>/<track>', methods=['GET'])
def get_track(songhash, track):
        mp3_name = f"{songhash}-{track}.mp3"
        down_name = f"{track}.mp3"

        track_info = min_server.get_object(bucket_name, mp3_name)
        return send_file(io.BytesIO(track_info.read()), download_name=down_name, mimetype='audio/mpeg', as_attachment=True)

@app.route('/apiv1/remove/<songhash>/<track>', methods=['GET', 'DELETE'])
def remove_track(songhash, track):
        mp3_name = f"{songhash}-{track}.mp3"

        min_server.remove_object(bucket_name, mp3_name)
        return jsonify(success=True, message="Track removed from database")
"""
@app.route('/', methods=['GET'])
def hello():
    return '<h1>Music Separation Server</h1><p>Use a valid endpoint</p>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
