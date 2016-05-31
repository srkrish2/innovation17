import pymongo
import copy
import re

MONGODB_ID = "_id"

TITLE = "title"
DESCRIPTION = "description"
SLUG = "slug"

USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"

OWNER_USERNAME = "owner_username"
SCHEMA_COUNT = "schema_count"
GENERATE_SCHEMA_HIT_ID = "generate_schema_hit_id"
SCHEMA_COUNT_GOAL = "schema_count_goal"
SCHEMAS_PAGE_LINK = "schemas_page_link"
# PROBLEM_OWNER_ID = "owner_id"

SCHEMA_TEXT = "text"
SCHEMA_HIT_ID = "hit_id"
SCHEMA_WORKER_ID = "worker_id"
SCHEMA_TIME = "time"
SCHEMA_ASSIGNMENT_ID = "assignment_id"

PROJECT_OWNER_ID = "owner_id"
PROJECT_CATEGORY = "category"


def add_user():
    user = {}
    # insert user to collection and get generated id
    user_id = users_collection.insert_one(user).inserted_id
    return user_id


def add_problem(generate_schema_hit_id, title, description, owner_username, schema_count_goal):
    problem = {
        GENERATE_SCHEMA_HIT_ID: generate_schema_hit_id,
        TITLE: title,
        DESCRIPTION: description,
        OWNER_USERNAME: owner_username,
        SCHEMA_COUNT: 0,
        SCHEMA_COUNT_GOAL: schema_count_goal,
        SLUG: slugify(title)
    }
    problems_collection.insert_one(problem)


def slugify(s):
    s = s.lower()
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')
    s = re.sub('\W', '', s)
    s = s.replace('_', ' ')
    s = re.sub('\s+', ' ', s)
    s = s.strip()
    s = s.replace(' ', '-')
    return s


def get_problems_by_user(username):
    result = []
    for problem in problems_collection.find({OWNER_USERNAME: username}):
        for_result = {
            TITLE: problem[TITLE],
            DESCRIPTION: problem[DESCRIPTION],
            SCHEMA_COUNT: problem[SCHEMA_COUNT],
            SCHEMA_COUNT_GOAL: problem[SCHEMA_COUNT_GOAL],
            GENERATE_SCHEMA_HIT_ID: problem[GENERATE_SCHEMA_HIT_ID],
            SCHEMAS_PAGE_LINK: "/{}/schemas".format(problem[SLUG])
        }
        result.append(for_result)
    return result


def does_user_have_problem(username, problem_slug):
    query = {
        OWNER_USERNAME: username,
        SLUG: problem_slug
    }
    return problems_collection.find_one(query) is not None


def get_generate_schema_hit_id(username, problem_title_slug):
    query = {
        OWNER_USERNAME: username,
        SLUG: problem_title_slug
    }
    problem = problems_collection.find_one(query)
    return problem[GENERATE_SCHEMA_HIT_ID]


def get_schemas(username, problem_title_slug):
    result = []
    query = {
        OWNER_USERNAME: username,
        SLUG: problem_title_slug
    }
    for schema in schemas_collection.find(query):
        for_result = {
            SCHEMA_TEXT: schema[SCHEMA_TEXT],
            SCHEMA_TIME: schema[SCHEMA_TIME],
            SCHEMA_WORKER_ID: schema[SCHEMA_WORKER_ID],
            SCHEMA_ASSIGNMENT_ID: schema[SCHEMA_ASSIGNMENT_ID]
        }
        result.append(for_result)
    return result


def update_schema_count(generate_schema_hit_id, schema_count):
    query_filter = {GENERATE_SCHEMA_HIT_ID: generate_schema_hit_id}
    update = {'$set': {SCHEMA_COUNT: schema_count}}
    problems_collection.update_one(query_filter, update)


def add_schema(schema):
    schemas_collection.insert_one(schema)


def are_all_schemas_generated(username, problem_title_slug):
    query = {
        OWNER_USERNAME: username,
        SLUG: problem_title_slug
    }
    problem = problems_collection.find_one(query)
    return problem[SCHEMA_COUNT] == problem[SCHEMA_COUNT_GOAL]


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


def get_username_from_email(email):
    return users_collection.find_one({USER_EMAIL: email})[USER_USERNAME]

# client
client = pymongo.MongoClient()
# database
db = client.crowd_db
# collections
users_collection = db.users
problems_collection = db.problems
schemas_collection = db.schemas
projects_collection = db.projects
