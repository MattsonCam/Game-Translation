import redis
from pathlib import Path
import uuid
import os
import json
import mysql.connector
from transformers import T5Tokenizer, T5ForConditionalGeneration

redis_host = '10.38.224.3'
redis_port = 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port)

db_name = "translatedb"
connection = mysql.connector.connect(
host="10.74.112.3",
user="root",
password="",
database=db_name
)

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def connect_cursor(func):
    def wrapper(*args):
        with connection.cursor() as cursor:
            result = func(*args, cursor)
        return result
    return wrapper

@connect_cursor
def send_translation_mysql(_input, _translation, _source, _target, cursor):
        query_insert = "INSERT INTO translations (input, translation, source, target) VALUES (%s, %s, %s, %s)"
        cursor.execute(query_insert, (_input, _translation, _source, _target))
        connection.commit()
        print("Translation was added to mysql database")
        
def send_translation_redis(_translation, _key):
    redis_client.set(_key, json.dumps({'translation': _translation}), ex=1800)
    print("Translation was added to redis")

def process_translation(trans_data):
    line = trans_data["line"]
    source_lang = trans_data["sourceLang"]
    target_lang = trans_data["targetLang"]
    hash_key = trans_data["hashKey"]
    
    trans_prompt = f"translate {source_lang} to {target_lang}: {line}"
    
    input_ids = tokenizer.encode(trans_prompt, return_tensors="pt", padding=True)
    attention_mask = input_ids.ne(0)

    output_sequence = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        no_repeat_ngram_size=5,
        max_length=512,
        do_sample=False,
    )

    decoded_output = tokenizer.decode(output_sequence[0], skip_special_tokens=True)
    
    send_translation_mysql(line, decoded_output, source_lang, target_lang)
    send_translation_redis(decoded_output, hash_key)    

def queue_listen():
    while True:
        red_resp = redis_client.blpop('translation_queue')[1]
        process_translation(json.loads(red_resp))

if __name__ == '__main__':
    queue_listen()
