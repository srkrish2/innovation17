import pymongo
import copy

MONGODB_ID = "_id"

PROBLEM_HIT_ID = "hit_id"
PROBLEM_DESCRIPTION = "description"
PROBLEM_OWNER_ID = "owner_id"
PROBLEM_FINISH_TIME = "finish_time"

SCHEMA_TEXT = "text"
SCHEMA_HIT_ID = "hit_id"
SCHEMA_ASSIGNMENT_ID = "assignment_id"
SCHEMA_WORKER_ID = "worker_id"
SCHEMA_TIME = "time"


def add_user():
    user = {}
    # insert user to collection and get generated id
    user_id = users_collection.insert_one(user).inserted_id
    return user_id


def add_problem(hit_id, description, owner_id, finish_time):
    problem = {
        PROBLEM_HIT_ID: hit_id,
        PROBLEM_DESCRIPTION: description,
        PROBLEM_OWNER_ID: owner_id,
        PROBLEM_FINISH_TIME: finish_time
    }
    problems_collection.insert_one(problem)


def get_problems_by_user(user_id):
    # pack each problem with keys: mongdb_id, hit_id, and description
    result = []
    for problem in problems_collection.find({PROBLEM_OWNER_ID: user_id}):
        for_result = {
            PROBLEM_HIT_ID: problem[PROBLEM_HIT_ID],
            PROBLEM_DESCRIPTION: problem[PROBLEM_DESCRIPTION]
        }
        result.append(for_result)
    return result


def add_schema(schema_dict):
    schema = copy.deepcopy(schema_dict)
    schemas_collection.insert_one(schema)

# client
client = pymongo.MongoClient()
# database
db = client.crowd_db
# collections
users_collection = db.users
problems_collection = db.problems
schemas_collection = db.schemas