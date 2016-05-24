import pymongo
import copy

MONGODB_ID = "_id"

USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"

PROBLEM_HIT_ID = "hit_id"
PROBLEM_DESCRIPTION = "description"
PROBLEM_OWNER_ID = "owner_id"

SCHEMA_TEXT = "text"
SCHEMA_HIT_ID = "hit_id"
SCHEMA_WORKER_ID = "worker_id"
SCHEMA_TIME = "time"


def add_user():
    user = {}
    # insert user to collection and get generated id
    user_id = users_collection.insert_one(user).inserted_id
    return user_id


def add_problem(hit_id, description, owner_id):
    problem = {
        PROBLEM_HIT_ID: hit_id,
        PROBLEM_DESCRIPTION: description,
        PROBLEM_OWNER_ID: owner_id
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


def new_account(username, email, password):
    new_user = {
        USER_USERNAME: username,
        USER_EMAIL: email,
        USER_PASSWORD: password
    }
    users_collection.insert_one(new_user)


def is_email_in_use(email):
    return users_collection.find_one({USER_EMAIL: email}) is not None


def is_username_taken(username):
    return users_collection.find_one({USER_USERNAME: username}) is not None


def get_password_for_email(email):
    user_entry = users_collection.find_one({USER_EMAIL: email})
    if user_entry is None:
        print "MONGODB: no user with email %s" % email
        return ""
    return user_entry[USER_PASSWORD]


def get_password_for_username(username):
    user_entry = users_collection.find_one({USER_USERNAME: username})
    if user_entry is None:
        print "MONGODB: no user with name %s" % username
        return ""
    return user_entry[USER_PASSWORD]


# client
client = pymongo.MongoClient()
# database
db = client.crowd_db
# collections
users_collection = db.users
problems_collection = db.problems
schemas_collection = db.schemas
