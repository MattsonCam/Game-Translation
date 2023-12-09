#!/bin/python3

import io
from flask import send_file, request, Flask, jsonify, Response
import mysql.connector
# from minio import Minio
import uuid
import redis
import base64
import json
# import jsonpickle
import hashlib
import os

app = Flask(__name__)
# bucket_name = 'mp3files'
# min_server = Minio(os.getenv('MINIO_HOST', 'localhost:9000'), access_key='rootuser', secret_key='rootpass123', secure=False)

# Establish a mysql connection
db_name = "translatedb"
connection = mysql.connector.connect(
host="10.74.112.3",
user="root",
password=""
)

# Configure Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)


def get_hash_key(line, source_lang, target_lang):
    """
    Generate a SHA256 hash key for the given source and target languages and line.
    """
    key_string = f"{source_lang}_{target_lang}_{line}"
    return hashlib.sha256(key_string.encode()).hexdigest()

def push_queue(line, source_lang, target_lang, hash_key):
    """
    Send the translation task to the Redis message queue.
    """
    task = json.dumps({
        'line': line,
        'sourceLang': source_lang,
        'targetLang': target_lang,
        'hashKey': hash_key
    })
    redis_client.rpush('translation_queue', task)
    
def query_database_for_translation(_line, _source_lang, _target_lang):
    with connection.cursor() as cursor:
        query_read = "SELECT * FROM translations WHERE input = %s AND source = %s AND target = %s"
        cursor.execute(query_read, (_line, _source_lang, _target_lang))
        result = cursor.fetchone()
    return result
    
def insert_translation(_input, _translation, _source, _target):
    translation_exists = query_database_for_translation(_input, _source, _target)
    if not translation_exists:
        with connection.cursor() as cursor:
            query_insert = "INSERT INTO translations (input, translation, source, target) VALUES (%s, %s, %s, %s)"
            cursor.execute(query_insert, (_input, _translation, _source, _target))
            connection.commit()
            print("Translation was added to database")

    else:
        print("Translation already exists")

def find_translation(line, source_lang, target_lang, hash_key):
    # Check if the translation is in Redis cache
    cached_translation = redis_client.get(hash_key)
    if cached_translation:
        redis_client.expire(hash_key, 300)
        return cached_translation.decode('utf-8')

    translation = query_database_for_translation(line, source_lang, target_lang)
    
    if translation:
        redis_client.set(hash_key, translation, ex=1800)
        return translation

    return None


@app.route('/apiv1/translate/request', methods=['POST'])
def process_translations():
    try:
        data = request.get_json()
        lines = data.get('tasks', [])
        source_lang = data.get('sourceLang', '')
        target_lang = data.get('targetLang', '')
        request_id = data.get('requestId', '')

        # mockResponse = [{'sourceText': lines[i], 'translatedText': 'Hola'} for i in range(len(lines))]

        response = {'requestId': request_id, 'status': False, 'results': {}}
        results = {}
        for line in lines:
            # Create a unique key for each line for caching and database queries
            hash_key = get_hash_key(source_lang, target_lang, line)

            # Check translation
            translated_line = find_translation(line, source_lang, target_lang, hash_key)
            if translated_line is not None:
                results[line] = translated_line
                continue

            push_queue(line, source_lang, target_lang, hash_key)

        response['results'] = results
        if len(results) == len(lines):
            response['status'] = True

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/apiv1/translate/status', methods=['POST'])
def check_translation_status():
    try:
        data = request.get_json()
        lines = data.get('tasks', [])
        source_lang = data.get('sourceLang', '')
        target_lang = data.get('targetLang', '')
        request_id = data.get('requestId', '')

        response = {'requestId': request_id, 'status': False, 'results': {}}
        results = {}
        for line in lines:
            hash_key = get_hash_key(source_lang, target_lang, line)
            translated_line = find_translation(line, source_lang, target_lang, hash_key)
            
            if translated_line is not None:
                results[line] = translated_line
                continue

        response['results'] = results
        if len(results) == len(lines):
            response['status'] = True

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


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
    return '<h1>Game Translation Server</h1><p>Use a valid endpoint</p>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
