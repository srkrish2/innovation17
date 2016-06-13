import pymongo
import re

TITLE = "title"
DESCRIPTION = "description"
SLUG = "slug"

USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"

OWNER_USERNAME = "owner_username"
TIME_CREATED = "time_created"
PROBLEM_ID = "problem_id"
STAGE = "stage"
COUNT = "count"

EDIT_PAGE_LINK = "edit_page_link"
VIEW_PAGE_LINK = "view_page_link"
SCHEMAS_PAGE_LINK = "schemas_page_link"
INSPIRATIONS_PAGE_LINK = "inspirations_page_link"
IDEAS_PAGE_LINK = "ideas_page_link"

INSPIRATION_HIT_ID = "inspiration_hit_id"
INSPIRATION_ID = "inspiration_id"
WORKER_ID = "worker_id"
SCHEMA_TIME = "time"
SCHEMA_ID = "schema_id"

STAGE_UNPUBLISHED = "unpublished"
STAGE_SCHEMA = "schema"
STAGE_INSPIRATION = "inspiration"
STAGE_IDEA = "idea"

SCHEMA_COUNT = "schema_count"
SCHEMA_COUNT_GOAL = "schema_count_goal"
INSPIRATION_COUNT = "inspiration_count"
INSPIRATION_COUNT_GOAL = "inspiration_count_goal"
IDEA_COUNT = "idea_count"
IDEA_COUNT_GOAL = "idea_count_goal"

INSPIRATION_LINK = "source_link"
INSPIRATION_ADDITIONAL = "image_link"
INSPIRATION_SUMMARY = "summary"
INSPIRATION_REASON = "reason"

IDEA_ID = "idea_id"
IDEA_HIT_ID = "idea_hit_id"
SUGGESTION_ID = "suggestion_id"
SUGGESTION_HIT_ID = "suggestion_hit_id"
SUGGESTION_COUNT = "suggestion_count"

IS_REJECTED = "is_rejected"
TEXT = "text"
COUNT_GOAL = "count_goal"
LAUNCHED = "launched"
SUGGESTIONS_PAGE_LINK = "suggestions_page_link"
FEEDBACK_TEXT = "feedback_text"


def save_problem(temporary_id, title, description, owner_username, schema_count_goal, time_created):
    problem = {
        PROBLEM_ID: temporary_id,
        TITLE: title,
        DESCRIPTION: description,
        OWNER_USERNAME: owner_username,
        SLUG: slugify(title),
        TIME_CREATED: time_created,
        STAGE: STAGE_UNPUBLISHED,
        SCHEMA_COUNT: 0,
        SCHEMA_COUNT_GOAL: schema_count_goal,
        INSPIRATION_COUNT: 0,
        INSPIRATION_COUNT_GOAL: 0,
        IDEA_COUNT: 0,
        IDEA_COUNT_GOAL: 0
    }
    problems_collection.insert_one(problem)


def set_schema_stage(temporary_id=None, hit_id=None):
    new_fields = {
        STAGE: STAGE_SCHEMA,
    }
    query_filter = {}
    if temporary_id is not None:
        new_fields[PROBLEM_ID] = hit_id
        query_filter[PROBLEM_ID] = temporary_id
    else:
        query_filter[PROBLEM_ID] = hit_id
    update = {'$set': new_fields}
    problems_collection.update_one(query_filter, update)


def set_inspiration_stage(problem_id, count_goal):
    query_filter = {PROBLEM_ID: problem_id}
    new_fields = {
        STAGE: STAGE_INSPIRATION,
        INSPIRATION_COUNT_GOAL: count_goal
    }
    update = {'$set': new_fields}
    problems_collection.update_one(query_filter, update)


def set_idea_stage(problem_id, count_goal):
    query_filter = {PROBLEM_ID: problem_id}
    new_fields = {
        STAGE: STAGE_IDEA,
        IDEA_COUNT_GOAL: count_goal
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
            TIME_CREATED: problem[TIME_CREATED],
            EDIT_PAGE_LINK: "/{}/edit".format(problem[SLUG]),
            SCHEMAS_PAGE_LINK:"/{}/schemas".format(problem[SLUG]),
            IDEAS_PAGE_LINK:"/{}/ideas".format(problem[SLUG]),
            INSPIRATIONS_PAGE_LINK: "/{}/inspirations".format(problem[SLUG]),
            VIEW_PAGE_LINK: "/{}/view".format(problem[SLUG]),
            SCHEMA_COUNT: problem[SCHEMA_COUNT],
            SCHEMA_COUNT_GOAL: problem[SCHEMA_COUNT_GOAL],
            INSPIRATION_COUNT: problem[INSPIRATION_COUNT],
            INSPIRATION_COUNT_GOAL: problem[INSPIRATION_COUNT_GOAL],
            IDEA_COUNT: problem[IDEA_COUNT],
            IDEA_COUNT_GOAL: problem[IDEA_COUNT_GOAL]
        }
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
            TEXT: schema[TEXT],
            SCHEMA_TIME: schema[SCHEMA_TIME],
            WORKER_ID: schema[WORKER_ID],
            SCHEMA_ID: schema[SCHEMA_ID],
            IS_REJECTED: schema[IS_REJECTED]
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


def update_idea_count(problem_id, inspiration_count):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$set': {IDEA_COUNT: inspiration_count}}
    problems_collection.update_one(query_filter, update)


def add_schema(schema):
    if schemas_collection.find_one(schema) is None:
        schemas_collection.insert_one(schema)


def add_inspiration(inspiration):
    if inspirations_collection.find_one(inspiration) is None:
        inspirations_collection.insert_one(inspiration)


def add_idea(idea):
    if ideas_collection.find_one(idea) is None:
        # add slug
        title = idea.pop(TITLE)
        # set suggestion count to 0, launched
        idea[SUGGESTION_COUNT] = 0
        idea[LAUNCHED] = False
        idea[SLUG] = slugify(title)
        ideas_collection.insert_one(idea)


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
        for_result = {
            PROBLEM_ID: problem[PROBLEM_ID],
            SCHEMA_COUNT: problem[SCHEMA_COUNT],
            INSPIRATION_COUNT: problem[INSPIRATION_COUNT],
            IDEA_COUNT: problem[IDEA_COUNT]
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


def get_inspiration_ids(problem_id):
    result = []
    for inspiration in inspirations_collection.find({PROBLEM_ID: problem_id}):
        result.append(inspiration[INSPIRATION_ID])
    return result


def get_inspiration_hit_id(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})[INSPIRATION_HIT_ID]


def get_idea_hit_id(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[IDEA_HIT_ID]


def add_inspiration_hit_id_to_schema(hit_id, schema_id):
    query_filter = {SCHEMA_ID: schema_id}
    new_fields = {
        INSPIRATION_HIT_ID: hit_id
    }
    update = {'$set': new_fields}
    schemas_collection.update_one(query_filter, update)


def get_inspirations(problem_id):
    return inspirations_collection.find({PROBLEM_ID: problem_id})


def get_ideas(problem_id):
    return ideas_collection.find({PROBLEM_ID: problem_id})


def get_problem_text(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})[DESCRIPTION]


def get_schema_text(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})[TEXT]


def get_schema_text_from_inspiration(inspiration_id):
    schema_id = inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[SCHEMA_ID]
    return get_schema_text(schema_id)


def get_inspiration_summary(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[INSPIRATION_SUMMARY]


def get_schema_count_goal(temp_problem_id):
    return problems_collection.find_one({PROBLEM_ID: temp_problem_id})[SCHEMA_COUNT_GOAL]


def delete_problem(problem_id):
    problems_collection.remove({PROBLEM_ID: problem_id})


def get_problem_fields(problem_id):
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    return problem[TITLE], problem[DESCRIPTION], problem[SCHEMA_COUNT_GOAL]


def edit_problem(problem_dict):
    problem_id = problem_dict[PROBLEM_ID]
    query_filter = {PROBLEM_ID: problem_id}
    new_fields = {
        DESCRIPTION: problem_dict[DESCRIPTION],
        SCHEMA_COUNT_GOAL: problem_dict[SCHEMA_COUNT_GOAL]
    }
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    if problem_dict[TITLE] != problem[TITLE]:
        new_fields[TITLE] = problem_dict[TITLE]
        new_fields[SLUG] = slugify(problem_dict[TITLE])
    update = {'$set': new_fields}
    problems_collection.update_one(query_filter, update)


def add_idea_hit_id_to_inspiration(hit_id, inspiration_id):
    query_filter = {INSPIRATION_ID: inspiration_id}
    new_fields = {
        IDEA_HIT_ID: hit_id
    }
    update = {'$set': new_fields}
    inspirations_collection.update_one(query_filter, update)


def set_schema_rejected_flag(schema_id, to_reject):
    query_filter = {SCHEMA_ID: schema_id}
    new_fields = {
        IS_REJECTED: to_reject
    }
    update = {'$set': new_fields}
    schemas_collection.update_one(query_filter, update)


def set_inspiration_rejected_flag(inspiration_id, to_reject):
    query_filter = {INSPIRATION_ID: inspiration_id}
    new_fields = {
        IS_REJECTED: to_reject
    }
    update = {'$set': new_fields}
    inspirations_collection.update_one(query_filter, update)


def get_idea_dict(idea_id):
    return ideas_collection.find_one({IDEA_ID: idea_id})


def save_feedback(idea_id, feedback_text, count_goal, hit_id, problem_id):
    feedback = {
        IDEA_ID: idea_id,
        TEXT: feedback_text,
        COUNT_GOAL: count_goal,
        SUGGESTION_HIT_ID: hit_id,
        PROBLEM_ID: problem_id,
        SUGGESTION_COUNT: 0
    }
    feedbacks_collection.insert_one(feedback)


def get_feedbacks(problem_id):
    return feedbacks_collection.find({PROBLEM_ID: problem_id})


def add_suggestion(suggestion):
    if suggestions_collection.find_one(suggestion) is None:
        suggestions_collection.insert_one(suggestion)


def update_suggestions_count(idea_to_count):
    for idea_id in idea_to_count:
        query_filter = {IDEA_ID: idea_id}
        new_fields = {
            SUGGESTION_COUNT: idea_to_count[idea_id]
        }
        update = {'$set': new_fields}
        ideas_collection.update_one(query_filter, update)


def get_suggestion_counts(problem_id):
    feedbacks = feedbacks_collection.find({PROBLEM_ID: problem_id})
    result = []
    for feedback in feedbacks:
        for_result = {
            "feedback_id": feedback[SUGGESTION_HIT_ID],
            SUGGESTION_COUNT: feedback[SUGGESTION_COUNT]
        }
        result.append(for_result)
    return result


def idea_launched(idea_id):
    query_filter = {IDEA_ID: idea_id}
    new_fields = {
        LAUNCHED: True
    }
    update = {'$set': new_fields}
    ideas_collection.update_one(query_filter, update)


def get_accepted_schemas_count(problem_id):
    count = 0
    for schema in schemas_collection.find({PROBLEM_ID: problem_id}):
        if not schema[IS_REJECTED]:
            count += 1
    return count


def get_suggestions(idea_slug):
    idea_id = ideas_collection.find_one({SLUG: idea_slug})
    return suggestions_collection.find({IDEA_ID: idea_id})


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
ideas_collection = db.ideas
feedbacks_collection = db.feedbacks
suggestions_collection = db.suggestions
