import datetime
import random
import string
import mongodb_controller

def create_schema_making_hit(problem):
    hit_id = ''.join(random.sample(string.hexdigits, 8))
    return hit_id, datetime.datetime.now()

def get_schema_making_status(hit_id):
    return "schema count dummy"

def get_schema_making_results(hit_id):
    schemas = []
    schema1 = {
        mongodb_controller.SCHEMA_ASSIGNMENT_ID: ''.join(random.sample(string.hexdigits, 8)),
        mongodb_controller.SCHEMA_HIT_ID: hit_id,
        mongodb_controller.SCHEMA_TEXT: "answer text1",
        mongodb_controller.SCHEMA_TIME: "1463622677000",
        mongodb_controller.SCHEMA_WORKER_ID: ''.join(random.sample(string.hexdigits, 8))
    }
    schemas.append(schema1)

    schema2 = {
        mongodb_controller.SCHEMA_ASSIGNMENT_ID: ''.join(random.sample(string.hexdigits, 8)),
        mongodb_controller.SCHEMA_HIT_ID: hit_id,
        mongodb_controller.SCHEMA_TEXT: "answer text2",
        mongodb_controller.SCHEMA_TIME: "1463622960000",
        mongodb_controller.SCHEMA_WORKER_ID: ''.join(random.sample(string.hexdigits, 8))
    }
    schemas.append(schema2)

    return schemas