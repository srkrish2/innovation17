import pymongo
import re

# PROBLEM: {
TITLE = "title"
DESCRIPTION = "description"
STAGE = "stage"
OWNER_USERNAME = "owner_username"
SLUG = "slug"
PROBLEM_ID = "problem_id"
TIME_CREATED = "time_created"
SCHEMA_COUNT = "schema_count"
SCHEMA_COUNT_GOAL = "schema_count_goal"
INSPIRATION_COUNT = "inspiration_count"
INSPIRATION_COUNT_GOAL = "inspiration_count_goal"
IDEA_COUNT = "idea_count"
IDEA_COUNT_GOAL = "idea_count_goal"
# }

# SCHEMA_HIT: {
HIT_ID = "hit_id"
COUNT = "count"
COUNT_GOAL = "count_goal"
PROBLEM_ID = "problem_id"
# }

# SCHEMA: {
TEXT = "text"
SCHEMA_ID = "schema_id"
WORKER_ID = "worker_id"
STATUS = "status"
# TIME_CREATED
# PROBLEM_ID
# }

# INSPIRATION_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# PROBLEM_ID
# SCHEMA_ID
#  }

# INSPIRATION: {
INSPIRATION_LINK = "source_link"
INSPIRATION_ADDITIONAL = "image_link"
INSPIRATION_SUMMARY = "summary"
INSPIRATION_REASON = "reason"
INSPIRATION_ID = "inspiration_id"
# SCHEMA_ID
# TIME_CREATED
# WORKER_ID
# STATUS
# PROBLEM_ID
# }

# IDEA_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# PROBLEM_ID
# SCHEMA_ID
# INSPIRATION_ID
# }

# IDEA: {
# TEXT
IDEA_ID = "idea_id"
# TIME_CREATED
# SLUG
# WORKER_ID
# PROBLEM_ID
# SCHEMA_ID
# INSPIRATION_ID
SUGGESTION_COUNT = "suggestion_count"
SUGGESTION_COUNT_GOAL = "suggestion_count_goal"
IS_LAUNCHED = "is_launched"
# }

# FEEDBACK: {
# TEXT
FEEDBACK_ID = "feedback_id"
# IDEA_ID
# }

# SUGGESTION_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# FEEDBACK_ID
# PROBLEM_ID
# IDEA_ID
# }

# SUGGESTION: {
SUGGESTION_ID = "suggestion_id"
# TEXT
# TIME_CREATED
# WORKER_ID
# IDEA_ID
# }


# USER: {
USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"
# }

# FOR FRONT END - MOVE TO SERVER.PY?
EDIT_PAGE_LINK = "edit_page_link"
VIEW_PAGE_LINK = "view_page_link"
SCHEMAS_PAGE_LINK = "schemas_page_link"
INSPIRATIONS_PAGE_LINK = "inspirations_page_link"
IDEAS_PAGE_LINK = "ideas_page_link"


# FIELD CONSTANTS
STAGE_UNPUBLISHED = "unpublished"
STAGE_SCHEMA = "schema"
STAGE_INSPIRATION = "inspiration"
STAGE_IDEA = "idea"
STATUS_REJECTED = 0
STATUS_ACCEPTED = 1
STATUS_PROCESSED = 2


def save_problem(problem_id, title, description, owner_username, schema_count_goal, time_created):
    problem = {
        PROBLEM_ID: problem_id,
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


def set_schema_stage(problem_id):
    query_filter = {
        PROBLEM_ID: problem_id
    }
    cur_stage = problems_collection.find_one(query_filter)[STAGE]
    if cur_stage != STAGE_UNPUBLISHED:
        return
    update = {'$set': {
        STAGE: STAGE_SCHEMA
    }}
    problems_collection.update_one(query_filter, update)


def insert_new_schema_hit(problem_id, count_goal, hit_id):
    new_schema_hit = {
        PROBLEM_ID: problem_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id
    }
    schema_hits_collection.insert_one(new_schema_hit)


def insert_new_inspiration_hit(problem_id, schema_id, count_goal, hit_id):
    new_inspiration_hit = {
        PROBLEM_ID: problem_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id,
        SCHEMA_ID: schema_id
    }
    inspiration_hits_collection.insert_one(new_inspiration_hit)


def insert_new_idea_hit(problem_id, schema_id, inspiration_id, count_goal, hit_id):
    new_idea_hit = {
        PROBLEM_ID: problem_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id,
        SCHEMA_ID: schema_id,
        INSPIRATION_ID: inspiration_id
    }
    idea_hits_collection.insert_one(new_idea_hit)


def insert_new_suggestion_hit(problem_id, idea_id, feedback_id, count_goal, hit_id):
    new_suggestion_hit = {
        PROBLEM_ID: problem_id,
        IDEA_ID: idea_id,
        FEEDBACK_ID: feedback_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id
    }
    suggestion_hits_collection.insert_one(new_suggestion_hit)


def set_inspiration_stage(problem_id):
    query_filter = {
        PROBLEM_ID: problem_id
    }
    cur_stage = problems_collection.find_one(query_filter)[STAGE]
    if cur_stage != STAGE_SCHEMA:
        return
    update = {'$set': {
        STAGE: STAGE_INSPIRATION
    }}
    problems_collection.update_one(query_filter, update)


def set_idea_stage(problem_id):
    query_filter = {
        PROBLEM_ID: problem_id
    }
    cur_stage = problems_collection.find_one(query_filter)[STAGE]
    if cur_stage != STAGE_INSPIRATION:
        return
    update = {'$set': {
        STAGE: STAGE_IDEA
    }}
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


def get_accepted_schemas(problem_id):
    return schemas_collection.find({
        PROBLEM_ID: problem_id,
        STATUS: STATUS_ACCEPTED
    })


def get_accepted_inspirations(problem_id):
    return inspirations_collection.find({
        PROBLEM_ID: problem_id,
        STATUS: STATUS_ACCEPTED
    })


def get_schema_hits(problem_id):
    return schema_hits_collection.find({PROBLEM_ID: problem_id})


def get_idea_hits(problem_id):
    return idea_hits_collection.find({PROBLEM_ID: problem_id})


def get_inspiration_hits(problem_id):
    return inspiration_hits_collection.find({PROBLEM_ID: problem_id})


def get_suggestion_hits(problem_id):
    return suggestion_hits_collection.find({PROBLEM_ID: problem_id})


def increment_schema_count(problem_id, how_much):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$inc': {SCHEMA_COUNT: how_much}}
    problems_collection.update_one(query_filter, update)


def increment_inspiration_count(problem_id, how_much):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$inc': {INSPIRATION_COUNT: how_much}}
    problems_collection.update_one(query_filter, update)


def increment_idea_count(problem_id, how_much):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$inc': {IDEA_COUNT: how_much}}
    problems_collection.update_one(query_filter, update)


def increment_schema_count_goal(problem_id, how_much):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$inc': {SCHEMA_COUNT_GOAL: how_much}}
    problems_collection.update_one(query_filter, update)


def increment_inspiration_count_goal(problem_id, how_much):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$inc': {INSPIRATION_COUNT_GOAL: how_much}}
    problems_collection.update_one(query_filter, update)


def increment_idea_count_goal(problem_id, how_much):
    query_filter = {PROBLEM_ID: problem_id}
    update = {'$inc': {IDEA_COUNT_GOAL: how_much}}
    problems_collection.update_one(query_filter, update)


def increment_schema_hit_count(hit_id, count):
    query_filter = {HIT_ID: hit_id}
    update = {'$inc': {COUNT: count}}
    schema_hits_collection.update_one(query_filter, update)


def increment_inspiration_hit_count(hit_id, count):
    query_filter = {HIT_ID: hit_id}
    update = {'$inc': {COUNT: count}}
    inspiration_hits_collection.update_one(query_filter, update)


def increment_idea_hit_count(hit_id, count):
    query_filter = {HIT_ID: hit_id}
    update = {'$inc': {COUNT: count}}
    idea_hits_collection.update_one(query_filter, update)


def increment_suggestion_count_goal(idea_id, count_goal):
    query_filter = {IDEA_ID: idea_id}
    update = {'$inc': {SUGGESTION_COUNT_GOAL: count_goal}}
    ideas_collection.update_one(query_filter, update)


def increment_suggestion_hit_count_by_one(suggestion_hit_id):
    query_filter = {HIT_ID: suggestion_hit_id}
    update = {'$inc': {COUNT: 1}}
    suggestion_hits_collection.update_one(query_filter, update)


def increment_suggestion_count_by_one(idea_id):
    query_filter = {IDEA_ID: idea_id}
    update = {'$inc': {SUGGESTION_COUNT: 1}}
    ideas_collection.update_one(query_filter, update)


def add_schema(schema):
    schemas_collection.insert_one(schema)


def contains_schema(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id}) is not None


def contains_idea(idea_id):
    return ideas_collection.find_one({IDEA_ID: idea_id}) is not None


def contains_inspiration(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id}) is not None


def contains_suggestion(suggestion_id):
    return suggestions_collection.find_one({SUGGESTION_ID: suggestion_id}) is not None


def add_inspiration(inspiration):
    inspirations_collection.insert_one(inspiration)


def add_idea(idea):
    if ideas_collection.find_one(idea) is None:
        # replace title with slug
        title = idea.pop(TITLE)
        idea[SLUG] = slugify(title)
        idea[SUGGESTION_COUNT] = 0
        idea[SUGGESTION_COUNT_GOAL] = 0
        ideas_collection.insert_one(idea)



def add_feedback(feedback_id, text, idea_id):
    feedbacks_collection.insert_one({
        FEEDBACK_ID: feedback_id,
        TEXT: text,
        IDEA_ID: idea_id
    })


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


def get_inspirations(problem_id):
    return inspirations_collection.find({PROBLEM_ID: problem_id})


def get_ideas(problem_id):
    return ideas_collection.find({PROBLEM_ID: problem_id})


def get_schema_text(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})[TEXT]


def get_schema_text_from_inspiration(inspiration_id):
    schema_id = inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[SCHEMA_ID]
    return get_schema_text(schema_id)


def get_inspiration_summary(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[INSPIRATION_SUMMARY]


def delete_problem(problem_id):
    problems_collection.remove({PROBLEM_ID: problem_id})


def get_problem_fields(problem_id):
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    return problem[TITLE], problem[DESCRIPTION], problem[SCHEMA_COUNT_GOAL]


def get_problem_description(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})[DESCRIPTION]


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


def set_schema_rejected_flag(schema_id, to_reject):
    query_filter = {SCHEMA_ID: schema_id}
    if to_reject:
        status = STATUS_REJECTED
    else:
        status = STATUS_ACCEPTED
    new_fields = {
        STATUS: status
    }
    update = {'$set': new_fields}
    schemas_collection.update_one(query_filter, update)


def set_inspiration_rejected_flag(inspiration_id, to_reject):
    query_filter = {INSPIRATION_ID: inspiration_id}
    if to_reject:
        status = STATUS_REJECTED
    else:
        status = STATUS_ACCEPTED
    new_fields = {
        STATUS: status
    }
    update = {'$set': new_fields}
    inspirations_collection.update_one(query_filter, update)


def get_idea_dict(idea_id):
    return ideas_collection.find_one({IDEA_ID: idea_id})


def get_schema_dict(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})


def get_inspiration_dict(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})


def get_feedback_dict(feedback_id):
    return feedbacks_collection.find({FEEDBACK_ID: feedback_id})


def get_feedback_dicts(idea_id):
    return feedbacks_collection.find({IDEA_ID: idea_id})


def add_suggestion(suggestion):
    if suggestions_collection.find_one(suggestion) is None:
        suggestions_collection.insert_one(suggestion)


def get_suggestion_counts(problem_id):
    ideas = ideas_collection.find({PROBLEM_ID: problem_id})
    result = []
    for idea in ideas:
        for_result = {
            IDEA_ID: idea[IDEA_ID],
            SUGGESTION_COUNT: idea[SUGGESTION_COUNT]
        }
        result.append(for_result)
    return result


def idea_launched(idea_id):
    query_filter = {IDEA_ID: idea_id}
    new_fields = {
        IS_LAUNCHED: True
    }
    update = {'$set': new_fields}
    ideas_collection.update_one(query_filter, update)


def get_accepted_schemas_count(problem_id):
    return schemas_collection.count({
        PROBLEM_ID: problem_id,
        STATUS: STATUS_ACCEPTED
    })


def get_suggestion_dicts(feedback_id):
    return suggestions_collection.find({FEEDBACK_ID: feedback_id})


def get_idea_dict_for_slug(idea_slug):
    return ideas_collection.find_one({SLUG: idea_slug})


def did_reach_schema_count_goal(problem_id):
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    return problem[SCHEMA_COUNT] == problem[SCHEMA_COUNT_GOAL]


def did_reach_idea_count_goal(problem_id):
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    return problem[IDEA_COUNT] == problem[IDEA_COUNT_GOAL]


def did_reach_inspiration_count_goal(problem_id):
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    return problem[INSPIRATION_COUNT] == problem[INSPIRATION_COUNT_GOAL]


def get_schemas_for_problem(problem_id):
    result = []
    for schema in schemas_collection.find({PROBLEM_ID: problem_id}):
        for_result = {
            TEXT: schema[TEXT],
            TIME_CREATED: schema[TIME_CREATED],
            WORKER_ID: schema[WORKER_ID],
            SCHEMA_ID: schema[SCHEMA_ID],
            STATUS: schema[STATUS]
        }
        result.append(for_result)
    return result


def set_schema_processed_status(schema_id):
    query_filter = {
        SCHEMA_ID: schema_id
    }
    update = {'$set': {
        STATUS: STATUS_PROCESSED
    }}
    schemas_collection.update_one(query_filter, update)


def set_inspiration_processed_status(inspiration_id):
    query_filter = {
        INSPIRATION_ID: inspiration_id
    }
    update = {'$set': {
        STATUS: STATUS_PROCESSED
    }}
    inspirations_collection.update_one(query_filter, update)


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
schema_hits_collection = db.schema_hits
schemas_collection = db.schemas
inspiration_hits_collection = db.inspiration_hits
inspirations_collection = db.inspirations
idea_hits_collection = db.idea_hits
ideas_collection = db.ideas
feedbacks_collection = db.feedbacks
suggestion_hits_collection = db.suggestion_hits
suggestions_collection = db.suggestions
