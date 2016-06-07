import pymongo
import re

TITLE = "title"
DESCRIPTION = "description"
SLUG = "slug"

USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"

OWNER_USERNAME = "owner_username"
SCHEMA_COUNT = "schema_count"
SCHEMA_COUNT_GOAL = "schema_count_goal"
SCHEMAS_PAGE_LINK = "schemas_page_link"
TIME_CREATED = "time_created"
PROBLEM_ID = "problem_id"
STAGE = "stage"
STAGE_SCHEMA = "schema"
COUNT = "count"
STAGE_INSPIRATION = "inspiration"
STAGE_UNPUBLISHED = "unpublished"
INSPIRATIONS_PAGE_LINK = "inspirations_page_link"
INSPIRATION_COUNT = "inspiration_count"
INSPIRATION_COUNT_GOAL = "inspiration_count_goal"
EDIT_PAGE_LINK = "edit_page_link"
VIEW_PAGE_LINK = "view_page_link"

SCHEMA_TEXT = "text"
INSPIRATION_HIT_ID = "inspiration_hit_id"
INSPIRATION_ID = "inspiration_id"
WORKER_ID = "worker_id"
SCHEMA_TIME = "time"
SCHEMA_ID = "schema_id"

IDEA_ID = "idea_id"


def save_problem(temporary_id, title, description, owner_username, schema_count_goal, time_created):
    problem = {
        PROBLEM_ID: temporary_id,
        TITLE: title,
        DESCRIPTION: description,
        OWNER_USERNAME: owner_username,
        SCHEMA_COUNT_GOAL: schema_count_goal,
        SLUG: slugify(title),
        TIME_CREATED: time_created,
        STAGE: STAGE_UNPUBLISHED
    }
    problems_collection.insert_one(problem)


def set_schema_stage(temporary_id=None, hit_id=None):
    query_filter = {PROBLEM_ID: temporary_id}
    new_fields = {
        STAGE: STAGE_SCHEMA,
        SCHEMA_COUNT: 0
    }
    if temporary_id is not None:
        new_fields[PROBLEM_ID: hit_id]
    update = {'$set': new_fields}
    problems_collection.update_one(query_filter, update)


def set_inspiration_stage(problem_id, count_goal):
    query_filter = {PROBLEM_ID: problem_id}
    new_fields = {
        STAGE: STAGE_INSPIRATION,
        INSPIRATION_COUNT: 0,
        INSPIRATION_COUNT_GOAL: count_goal
    }
    update = {'$set': new_fields}
    problems_collection.update_one(query_filter, update)


def get_problems_by_user(username):
    result = []
    for problem in problems_collection.find({OWNER_USERNAME: username}):
        for_result = {
            PROBLEM_ID: problem[PROBLEM_ID],
            TITLE: problem[TITLE],
            DESCRIPTION: problem[DESCRIPTION],
            STAGE: problem[STAGE],
            SCHEMA_COUNT_GOAL: problem[SCHEMA_COUNT_GOAL],
            TIME_CREATED: problem[TIME_CREATED]
        }
        if problem[STAGE] == STAGE_UNPUBLISHED:
            for_result[EDIT_PAGE_LINK] = "/{}/edit".format(problem[SLUG])
            for_result[VIEW_PAGE_LINK] = "/{}/view".format(problem[SLUG])
        elif problem[STAGE] == STAGE_SCHEMA:
            for_result[SCHEMA_COUNT] = problem[SCHEMA_COUNT]
            for_result[SCHEMAS_PAGE_LINK] = "/{}/schemas".format(problem[SLUG])
        elif problem[STAGE] == STAGE_INSPIRATION:
            for_result[INSPIRATION_COUNT] = problem[INSPIRATION_COUNT],
            for_result[INSPIRATION_COUNT_GOAL] = problem[INSPIRATION_COUNT_GOAL]
            for_result[INSPIRATIONS_PAGE_LINK] = "/{}/inspirations".format(problem[SLUG])

        result.append(for_result)
        
    return result


def does_user_have_problem(username, problem_slug):
    query = {
        OWNER_USERNAME: username,
        SLUG: problem_slug
    }
    return problems_collection.find_one(query) is not None


def does_user_have_problem_with_id(username, problem_id):
    query = {
        OWNER_USERNAME: username,
        PROBLEM_ID: problem_id
    }
    return problems_collection.find_one(query) is not None


def get_problem_id(username, problem_title_slug):
    query = {
        OWNER_USERNAME: username,
        SLUG: problem_title_slug
    }
    problem = problems_collection.find_one(query)
    return problem[PROBLEM_ID]


def get_schemas(problem_id):
    result = []
    for schema in schemas_collection.find({PROBLEM_ID: problem_id}):
        for_result = {
            SCHEMA_TEXT: schema[SCHEMA_TEXT],
            SCHEMA_TIME: schema[SCHEMA_TIME],
            WORKER_ID: schema[WORKER_ID],
            SCHEMA_ID: schema[SCHEMA_ID]
        }
        result.append(for_result)
    return result


def update_schema_count(problem_id, schema_count):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$set': {SCHEMA_COUNT: schema_count}}
    problems_collection.update_one(query_filter, update)


def update_inspiration_count(problem_id, inspiration_count):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$set': {INSPIRATION_COUNT: inspiration_count}}
    problems_collection.update_one(query_filter, update)


def add_schema(schema):
    if schemas_collection.find_one(schema) is None:
        schemas_collection.insert_one(schema)


def add_inspiration(inspiration):
    if inspirations_collection.find_one(inspiration) is None:
        inspirations_collection.insert_one(inspiration)


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


def get_users_problem_ids(username):
    hit_ids = []
    for problem in problems_collection.find({OWNER_USERNAME: username}):
        hit_ids.append(problem[PROBLEM_ID])
    return hit_ids


def get_counts_for_user(username):
    result = []
    for problem in problems_collection.find({OWNER_USERNAME: username}):
        stage = problem[STAGE]
        if stage == STAGE_UNPUBLISHED:
            continue
        elif stage == STAGE_SCHEMA:
            count = problem[SCHEMA_COUNT]
        elif stage == STAGE_INSPIRATION:
            count = problem[INSPIRATION_COUNT]
        for_result = {
            PROBLEM_ID: problem[PROBLEM_ID],
            COUNT: count
        }
        result.append(for_result)
    return result


def get_stage(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})[STAGE]


def get_schema_ids(problem_id):
    result = []
    for schema in schemas_collection.find({PROBLEM_ID: problem_id}):
        result.append(schema[SCHEMA_ID])
    return result


def get_inspiration_hit_id(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})[INSPIRATION_ID]


def add_inspiration_hit_id_to_schema(hit_id, schema_id):
    query_filter = {SCHEMA_ID: schema_id}
    new_fields = {
        INSPIRATION_ID: hit_id
    }
    update = {'$set': new_fields}
    schemas_collection.update_one(query_filter, update)


def get_inspirations(problem_id):
    return inspirations_collection.find({PROBLEM_ID: problem_id})


def get_problem_text(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})[DESCRIPTION]


def get_schema_text(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})[SCHEMA_TEXT]


def get_schema_count_goal(temp_problem_id):
    return problems_collection.find_one({PROBLEM_ID: temp_problem_id})[SCHEMA_COUNT_GOAL]


def delete_problem(problem_id):
    problems_collection.remove({PROBLEM_ID: problem_id})


def get_problem_fields(problem_id):
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    return problem[TITLE], problem[DESCRIPTION], problem[SCHEMA_COUNT_GOAL], problem[PROBLEM_ID]


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

# client
client = pymongo.MongoClient()
# database
db = client.crowd_db
# collections
users_collection = db.users
problems_collection = db.problems
schemas_collection = db.schemas
inspirations_collection = db.inspirations
