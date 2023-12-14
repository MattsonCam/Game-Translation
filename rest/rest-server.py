#!/bin/python3

import io
import logging
from flask import send_file, request, Flask, jsonify, Response
from flask_cors import CORS
import mysql.connector
import uuid
import redis
import base64
import json
# import jsonpickle
import hashlib
import os

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)
logger = logging.getLogger('flask.app')

# Establish a mysql connection
db_name = "translatedb"
connection = mysql.connector.connect(
host="10.74.112.3",
user="root",
password="",
database=db_name
)

# Configure Redis
redis_host = '10.38.224.3'
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port)

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
    
def connect_cursor(func):
    def wrapper(*args):
        with connection.cursor() as cursor:
            result = func(*args, cursor)
        return result
    return wrapper

@connect_cursor
def query_database_for_translation(_line, _source_lang, _target_lang, cursor):
    query_read = "SELECT translation FROM translations WHERE input = %s AND source = %s AND target = %s"
    cursor.execute(query_read, (_line, _source_lang, _target_lang))
    fetch_result = cursor.fetchone()

    if fetch_result is not None:
        result = fetch_result[0]
        return result
    else:
        return None
    
@connect_cursor
def insert_translation(_input, _translation, _source, _target, cursor):
    translation_exists = query_database_for_translation(_input, _source, _target)
    if not translation_exists:
        query_insert = "INSERT INTO translations (input, translation, source, target) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_insert, (_input, _translation, _source, _target))
        connection.commit()
        print("Translation was added to database")

    else:
        print("Translation already exists")

def find_translation(line, source_lang, target_lang, hash_key):
    try:
        cached_translation = redis_client.get(hash_key)

        if cached_translation is not None:
            redis_client.expire(hash_key, 300)
            try:
                cached_translation_json = json.loads(cached_translation)
                if "translation" in cached_translation_json:
                    return cached_translation_json["translation"]
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON decoding error: {json_err}")
                # Handle the case where JSON is not in expected format

        logger.error(f"Retrieving translation for line: '{line}', Querying database for translation")
        translation = query_database_for_translation(line, source_lang, target_lang)

        if translation is not None:
            redis_client.set(hash_key, json.dumps({'translation': translation}), ex=1800)
            return translation

        return None
    except Exception as e:
        logger.error(f"Error finding translation: {e}")
        raise


@app.route('/apiv1/translate/request', methods=['POST'])
def process_translations():
    try:
        data = request.get_json()
        lines = data.get('lines', [])
        source_lang = data.get('sourceLang', '')
        target_lang = data.get('targetLang', '')
        request_id = data.get('requestId', '')

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

        # results = {lines[i]: f"{lines[i]} - Translated" for i in range(len(lines) - 10)}

        response['results'] = results
        if len(results) == len(set(lines)):
            response['status'] = True

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/apiv1/translate/status', methods=['POST'])
def check_translation_status():
    try:
        data = request.get_json()
        lines = data.get('lines', [])
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

        # results = {line: f"{line} - Translated" for line in lines}

        response['results'] = results
        if len(results) == len(set(lines)):
            response['status'] = True

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/', methods=['GET'])
def hello():
    return '<h1>Game Translation Server</h1><p>Use a valid endpoint</p>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
