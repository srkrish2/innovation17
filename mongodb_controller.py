import pymongo
from constants import *
from utility_functions import slugify


######################## INSERT ONE #################################

def insert_problem(problem_dict):
    problem = {
        PROBLEM_ID: problem_dict[PROBLEM_ID],
        TITLE: problem_dict[TITLE],
        DESCRIPTION: problem_dict[DESCRIPTION],
        OWNER_USERNAME: problem_dict[OWNER_USERNAME],
        SLUG: slugify(problem_dict[TITLE]),
        STAGE: STAGE_UNPUBLISHED,
        SCHEMA_ASSIGNMENTS_NUM: problem_dict[SCHEMA_ASSIGNMENTS_NUM],
        LAZY: problem_dict[LAZY]
    }
    problems_collection.insert_one(problem)


def insert_new_schema_hit(problem_id, count_goal, hit_id):
    new_schema_hit = {
        PROBLEM_ID: problem_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id
    }
    schema_hits_collection.insert_one(new_schema_hit)


def insert_new_rank_schema_hit(schema_ids, hit_id, problem_id):
    new_rank_schema_hit = {
        SCHEMA_IDS: schema_ids,
        HIT_ID: hit_id,
        SUBMITTED_BY_WORKER: False,
        PROBLEM_ID: problem_id
    }
    rank_schema_hits_collection.insert_one(new_rank_schema_hit)


def insert_new_rank_inspiration_hit(inspiration_id, rank_inspiration_hit_id):
    new_rank_inspiration_hit = {
        INSPIRATION_ID: inspiration_id,
        HIT_ID: rank_inspiration_hit_id,
        SUBMITTED_BY_WORKER: False
    }
    rank_inspiration_hits_collection.insert_one(new_rank_inspiration_hit)


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


def insert_new_rank_idea_hit(idea_id, count_goal, hit_id):
    new_rank_idea_hit = {
        IDEA_ID: idea_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id
    }
    rank_idea_hits_collection.insert_one(new_rank_idea_hit)


def insert_new_rank_suggestion_hit(suggestion_id, count_goal, hit_id):
    new_rank_suggestion_hit = {
        SUGGESTION_ID: suggestion_id,
        COUNT: 0,
        COUNT_GOAL: count_goal,
        HIT_ID: hit_id
    }
    rank_suggestion_hits_collection.insert_one(new_rank_suggestion_hit)


def add_schema(schema):
    schemas_collection.insert_one(schema)


def add_inspiration(inspiration):
    inspirations_collection.insert_one(inspiration)


def add_idea(idea):
    # replace title with slug
    title = idea.pop(TITLE)
    idea[SLUG] = slugify(title)
    ideas_collection.insert_one(idea)


def add_feedback(feedback_id, text, idea_id):
    feedbacks_collection.insert_one({
        FEEDBACK_ID: feedback_id,
        TEXT: text,
        IDEA_ID: idea_id
    })


def insert_schema_rank(rank_dict):
    schema_ranks_collection.insert_one(rank_dict)


def insert_inspiration_rank(rank_dict):
    inspiration_ranks_collection.insert_one(rank_dict)


def insert_idea_rank(rank_dict):
    idea_ranks_collection.insert_one(rank_dict)


def insert_suggestion_rank(rank_dict):
    suggestion_ranks_collection.insert_one(rank_dict)


def new_account(username, email, password):
    new_user = {
        USER_USERNAME: username,
        USER_EMAIL: email,
        USER_PASSWORD: password
    }
    users_collection.insert_one(new_user)


def add_suggestion(suggestion):
    if suggestions_collection.find_one(suggestion) is None:
        suggestions_collection.insert_one(suggestion)


######################## UPDATE ONE #################################

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


def set_suggestion_stage(problem_id):
    query_filter = {
        PROBLEM_ID: problem_id
    }
    cur_stage = problems_collection.find_one(query_filter)[STAGE]
    if cur_stage != STAGE_IDEA:
        return
    update = {'$set': {
        STAGE: STAGE_SUGGESTION
    }}
    problems_collection.update_one(query_filter, update)


def increment_schema_hit_count(hit_id, how_much):
    query_filter = {HIT_ID: hit_id}
    update = {'$inc': {COUNT: how_much}}
    schema_hits_collection.update_one(query_filter, update)


def increment_inspiration_hit_count(hit_id, count):
    query_filter = {HIT_ID: hit_id}
    update = {'$inc': {COUNT: count}}
    inspiration_hits_collection.update_one(query_filter, update)


def increment_idea_hit_count(hit_id, count):
    query_filter = {HIT_ID: hit_id}
    update = {'$inc': {COUNT: count}}
    idea_hits_collection.update_one(query_filter, update)


def increment_suggestion_hit_count(suggestion_hit_id, how_much):
    query_filter = {HIT_ID: suggestion_hit_id}
    update = {'$inc': {COUNT: how_much}}
    suggestion_hits_collection.update_one(query_filter, update)


def increment_rank_schema_hit_count(rank_schema_hit_id, how_much):
    query_filter = {HIT_ID: rank_schema_hit_id}
    update = {'$inc': {COUNT: how_much}}
    rank_schema_hits_collection.update_one(query_filter, update)


def increment_rank_inspiration_hit_count(rank_inspiration_hit_id, how_much):
    query_filter = {HIT_ID: rank_inspiration_hit_id}
    update = {'$inc': {COUNT: how_much}}
    rank_inspiration_hits_collection.update_one(query_filter, update)


def increment_rank_idea_hit_count(rank_idea_hit_id, how_much):
    query_filter = {HIT_ID: rank_idea_hit_id}
    update = {'$inc': {COUNT: how_much}}
    rank_idea_hits_collection.update_one(query_filter, update)


def increment_rank_suggestion_hit_count(rank_suggestion_hit_id, how_much):
    query_filter = {HIT_ID: rank_suggestion_hit_id}
    update = {'$inc': {COUNT: how_much}}
    rank_suggestion_hits_collection.update_one(query_filter, update)


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


def set_idea_rejected_flag(idea_id, to_reject):
    query_filter = {IDEA_ID: idea_id}
    if to_reject:
        status = STATUS_REJECTED
    else:
        status = STATUS_ACCEPTED
    new_fields = {
        STATUS: status
    }
    update = {'$set': new_fields}
    ideas_collection.update_one(query_filter, update)


def idea_launched(idea_id):
    query_filter = {IDEA_ID: idea_id}
    new_fields = {
        STATUS: STATUS_PROCESSED
    }
    update = {'$set': new_fields}
    ideas_collection.update_one(query_filter, update)


def schema_set_well_ranked(schema_id):
    query_filter = {SCHEMA_ID: schema_id}
    new_fields = {
        WELL_RANKED: True
    }
    update = {'$set': new_fields}
    schemas_collection.update_one(query_filter, update)


def inspiration_set_well_ranked(inspiration_id):
    query_filter = {INSPIRATION_ID: inspiration_id}
    new_fields = {
        WELL_RANKED: True
    }
    update = {'$set': new_fields}
    inspirations_collection.update_one(query_filter, update)


def rank_schema_hit_set_submitted(hit_id):
    query_filter = {HIT_ID: hit_id}
    new_fields = {
        SUBMITTED_BY_WORKER: True
    }
    update = {'$set': new_fields}
    rank_schema_hits_collection.update_one(query_filter, update)


############################ FIND ONE ##########################

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


def contains_schema(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id}) is not None


def contains_idea(idea_id):
    return ideas_collection.find_one({IDEA_ID: idea_id}) is not None


def contains_inspiration(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id}) is not None


def contains_suggestion(suggestion_id):
    return suggestions_collection.find_one({SUGGESTION_ID: suggestion_id}) is not None


def contains_schema_rank(rank_id):
    return schema_ranks_collection.find_one({RANK_ID: rank_id}) is not None


def contains_inspiration_rank(rank_id):
    return inspiration_ranks_collection.find_one({RANK_ID: rank_id}) is not None


def contains_idea_rank(rank_id):
    return idea_ranks_collection.find_one({RANK_ID: rank_id}) is not None


def contains_suggestion_rank(rank_id):
    return suggestion_ranks_collection.find_one({RANK_ID: rank_id}) is not None


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


def get_problem_dict(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})


def get_idea_dict(idea_id):
    return ideas_collection.find_one({IDEA_ID: idea_id})


def get_schema_dict(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})


def get_inspiration_dict(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})


def get_feedback_dict(feedback_id):
    return feedbacks_collection.find_one({FEEDBACK_ID: feedback_id})


def get_stage(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})[STAGE]


def get_schema_text(schema_id):
    return schemas_collection.find_one({SCHEMA_ID: schema_id})[TEXT]


def get_schema_text_from_inspiration(inspiration_id):
    schema_id = inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[SCHEMA_ID]
    return get_schema_text(schema_id)


def get_inspiration_summary(inspiration_id):
    return inspirations_collection.find_one({INSPIRATION_ID: inspiration_id})[INSPIRATION_SUMMARY]


def get_problem_description(problem_id):
    return problems_collection.find_one({PROBLEM_ID: problem_id})[DESCRIPTION]


def get_idea_dict_for_slug(idea_slug):
    return ideas_collection.find_one({SLUG: idea_slug})


def get_rank_schema_hit_dict(schema_id):
    return rank_schema_hits_collection.find_one({SCHEMA_ID: schema_id})


def get_rank_inspiration_hit_dict(inspiration_id):
    return rank_inspiration_hits_collection.find_one({INSPIRATION_ID: inspiration_id})


def get_rank_idea_hit_dict(idea_id):
    return rank_idea_hits_collection.find_one({IDEA_ID: idea_id})


def get_rank_suggestion_hit_dict(suggestion_id):
    return rank_suggestion_hits_collection.find_one({SUGGESTION_ID: suggestion_id})

######################### FIND ALL ###############################


def get_schema_rank_dicts(schema_id):
    return schema_ranks_collection.find({SCHEMA_ID: schema_id})


def get_inspiration_rank_dicts(inspiration_id):
    return inspiration_ranks_collection.find({INSPIRATION_ID: inspiration_id})


def find_rank_schema_hit_dicts_with_query(query):
    return rank_schema_hits_collection.find(query)


def find_rank_inspiration_hits_dict_with_query(query):
    return rank_inspiration_hits_collection.find(query)


def get_problems_by_user(username):
    return problems_collection.find({OWNER_USERNAME: username})


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


def get_users_problem_ids(username):
    hit_ids = []
    for problem in problems_collection.find({OWNER_USERNAME: username}):
        hit_ids.append(problem[PROBLEM_ID])
    return hit_ids


def delete_problem(problem_id):
    problems_collection.remove({PROBLEM_ID: problem_id})


def edit_problem(problem_dict):
    problem_id = problem_dict[PROBLEM_ID]
    query_filter = {PROBLEM_ID: problem_id}
    new_fields = {
        DESCRIPTION: problem_dict[DESCRIPTION],
        SCHEMA_ASSIGNMENTS_NUM: problem_dict[SCHEMA_ASSIGNMENTS_NUM],
        LAZY: problem_dict[LAZY]
    }
    problem = problems_collection.find_one({PROBLEM_ID: problem_id})
    if problem_dict[TITLE] != problem[TITLE]:
        new_fields[TITLE] = problem_dict[TITLE]
        new_fields[SLUG] = slugify(problem_dict[TITLE])
    update = {'$set': new_fields}
    problems_collection.update_one(query_filter, update)


def get_ideas(problem_id):
    return ideas_collection.find({PROBLEM_ID: problem_id})


def get_suggestions(problem_id):
    return suggestions_collection.find({PROBLEM_ID: problem_id})


def get_inspirations(problem_id):
    return inspirations_collection.find({PROBLEM_ID: problem_id})


def get_feedback_dicts(idea_id):
    return feedbacks_collection.find({IDEA_ID: idea_id})


def get_accepted_schemas_count(problem_id):
    return schemas_collection.count({
        PROBLEM_ID: problem_id,
        STATUS: STATUS_ACCEPTED
    })


def get_suggestions_for_feedback(feedback_id):
    return suggestions_collection.find({FEEDBACK_ID: feedback_id})


def get_suggestions_for_problem(problem_id):
    return suggestions_collection.find({PROBLEM_ID: problem_id})


def get_suggestions_for_idea(idea_id):
    return suggestions_collection.find({IDEA_ID: idea_id})


def get_schema_dicts(problem_id):
    return schemas_collection.find({PROBLEM_ID: problem_id})


def get_new_schema_dicts(problem_id):
    return schemas_collection.find({
        PROBLEM_ID: problem_id,
        POSTED_FOR_RANK: False
    })


def get_new_inspiration_dicts(problem_id):
    return inspirations_collection.find({
        PROBLEM_ID: problem_id,
        POSTED_FOR_RANK: False
    })


def get_well_ranked_inspirations(problem_id):
    return inspirations_collection.find({
        WELL_RANKED: True,
        PROBLEM_ID: problem_id
    })


def get_well_ranked_ideas(problem_id):
    return ideas_collection.find({
        WELL_RANKED: True,
        PROBLEM_ID: problem_id
    })


def get_well_ranked_schemas(problem_id):
    return schemas_collection.find({
        WELL_RANKED: True,
        PROBLEM_ID: problem_id
    })


def get_schemas_for_inspiration_task(problem_id):
    return schemas_collection.find({
        PROBLEM_ID: problem_id,
        STATUS: STATUS_ACCEPTED,
        WELL_RANKED: True
    })


def set_schema_posted_for_rank(schema_id, val=True):
    query_filter = {
        SCHEMA_ID: schema_id
    }
    update = {'$set': {
        POSTED_FOR_RANK: val
    }}
    schemas_collection.update_one(query_filter, update)


def set_inspiration_posted_for_rank(inspiration_id, val=True):
    query_filter = {
        INSPIRATION_ID: inspiration_id
    }
    update = {'$set': {
        POSTED_FOR_RANK: val
    }}
    inspirations_collection.update_one(query_filter, update)


# client
client = pymongo.MongoClient()
# database
db = client.crowd_db
# collections
users_collection = db.users
problems_collection = db.problems
schema_hits_collection = db.schema_hits
schemas_collection = db.schemas
rank_schema_hits_collection = db.rank_schema_hits
schema_ranks_collection = db.schema_ranks
inspiration_hits_collection = db.inspiration_hits
inspirations_collection = db.inspirations
rank_inspiration_hits_collection = db.rank_inspiration_hits
inspiration_ranks_collection = db.inspiration_ranks
idea_hits_collection = db.idea_hits
ideas_collection = db.ideas
rank_idea_hits_collection = db.rank_idea_hits
idea_ranks_collection = db.idea_ranks
feedbacks_collection = db.feedbacks
suggestion_hits_collection = db.suggestion_hits
suggestions_collection = db.suggestions
rank_suggestion_hits_collection = db.rank_suggestion_hits
suggestion_ranks_collection = db.suggestion_ranks
