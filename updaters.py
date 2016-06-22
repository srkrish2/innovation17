import mongodb_controller
import mturk_controller
import datetime
from constants import READABLE_TIME_FORMAT, HOW_MANY_RANKS, MIN_RANK


def update_hit_results(username):
    # start = time.clock()
    for problem_id in mongodb_controller.get_users_problem_ids(username):
        if not mongodb_controller.did_reach_schema_count_goal(problem_id):
            update_schemas_for_problem(problem_id)
        if not mongodb_controller.did_reach_inspiration_count_goal(problem_id):
            update_inspirations_for_problem(problem_id)
        if not mongodb_controller.did_reach_idea_count_goal(problem_id):
            update_ideas_for_problem(problem_id)
        update_problems_schema_count(problem_id)
    # elapsed = time.clock()
    # elapsed = elapsed - start
    # print "Done updating! Time spent:", elapsed*1000


###############################################################################

def update_schemas_for_problem(problem_id):
    for schema_hit in mongodb_controller.get_schema_hits(problem_id):
        if schema_hit[mongodb_controller.COUNT] != schema_hit[mongodb_controller.COUNT_GOAL]:
            pull_schema_hit_results(schema_hit)
    for schema in mongodb_controller.get_schema_dicts(problem_id):
        schema_id = schema[mongodb_controller.SCHEMA_ID]
        rank_schema_hit_dict = mongodb_controller.get_rank_schema_hit_dict(schema_id)
        count = rank_schema_hit_dict[mongodb_controller.COUNT]
        count_goal = rank_schema_hit_dict[mongodb_controller.COUNT_GOAL]
        if count < count_goal:
            pull_rank_schema_hit_results(rank_schema_hit_dict)


def pull_schema_hit_results(schema_hit):
    schema_hit_id = schema_hit[mongodb_controller.HIT_ID]
    problem_id = schema_hit[mongodb_controller.PROBLEM_ID]
    schema_dicts = mturk_controller.get_schema_making_results(schema_hit_id)
    if schema_dicts == "FAIL":
        print "mturk_controller.get_schema_making_results - FAIL!"
        return
    for schema_dict in schema_dicts:
        schema_id = schema_dict[mongodb_controller.SCHEMA_ID]
        if mongodb_controller.contains_schema(schema_id):
            continue

        # pop epoch time
        epoch_time_ms = long(schema_dict.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        schema_dict[mongodb_controller.TIME_CREATED] = readable_time
        # add problem_id, status, and rank
        schema_dict[mongodb_controller.STATUS] = mongodb_controller.STATUS_ACCEPTED
        schema_dict[mongodb_controller.PROBLEM_ID] = problem_id
        schema_dict[mongodb_controller.RANK] = 0
        mongodb_controller.add_schema(schema_dict)
        rank_schema_hit_id = mturk_controller.create_rank_schema_hit(schema_dict[mongodb_controller.TEXT],
                                                                     HOW_MANY_RANKS)
        mongodb_controller.insert_new_rank_schema_hit(schema_id, HOW_MANY_RANKS, rank_schema_hit_id)
        mongodb_controller.increment_schema_hit_count_by_one(schema_hit_id)


def pull_rank_schema_hit_results(rank_schema_hit):
    rank_schema_hit_id = rank_schema_hit[mongodb_controller.HIT_ID]
    schema_id = rank_schema_hit[mongodb_controller.SCHEMA_ID]
    rank_dicts = mturk_controller.get_schema_ranking_results(rank_schema_hit_id)
    if rank_dicts == "FAIL":
        print "mturk_controller.get_schema_ranking_results - FAIL!"
        return
    new_ranks_count = 0
    for rank_dict in rank_dicts:
        rank_id = rank_dict[mongodb_controller.RANK_ID]
        if mongodb_controller.contains_schema_rank(rank_id):
            continue
        # pop epoch time
        epoch_time_ms = long(rank_dict.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        rank_dict[mongodb_controller.TIME_CREATED] = readable_time
        # add schema_id
        rank_dict[mongodb_controller.SCHEMA_ID] = schema_id

        mongodb_controller.add_schema_rank(rank_dict)
        new_ranks_count += 1
        mongodb_controller.increment_schema_rank(schema_id, rank_dict[mongodb_controller.RANK])
    mongodb_controller.increment_rank_schema_hit_count(rank_schema_hit_id, new_ranks_count)
    return new_ranks_count


def update_problems_schema_count(problem_id):
    well_ranked_count = 0
    for schema_dict in mongodb_controller.get_schema_dicts(problem_id):
        # schema_id = schema_dict[mongodb_controller.SCHEMA_ID]
        # rank_schema_hit_dict = mongodb_controller.get_rank_schema_hit_dict(schema_id)
        # count = rank_schema_hit_dict[mongodb_controller.COUNT]
        # count_goal = rank_schema_hit_dict[mongodb_controller.COUNT_GOAL]
        if schema_dict[mongodb_controller.RANK] >= MIN_RANK:
            well_ranked_count += 1
    mongodb_controller.set_schema_count(problem_id, well_ranked_count)


###############################################################################

def pull_inspiration_hit_results(inspiration_hit):
    inspiration_hit_id = inspiration_hit[mongodb_controller.HIT_ID]
    schema_id = inspiration_hit[mongodb_controller.SCHEMA_ID]
    problem_id = inspiration_hit[mongodb_controller.PROBLEM_ID]
    inspirations = mturk_controller.get_inspiration_hit_results(inspiration_hit_id)
    if inspirations == "FAIL":
        print "mturk_controller.get_inspiration_hit_results - FAIL!"
        return
    new_inspirations_count = 0
    for inspiration in inspirations:
        inspiration_id = inspiration[mongodb_controller.INSPIRATION_ID]
        if mongodb_controller.contains_inspiration(inspiration_id):
            continue
        # replace time with a readable one
        epoch_time_ms = long(inspiration.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        inspiration[mongodb_controller.TIME_CREATED] = readable_time
        # add problem id, schema id, and status
        inspiration[mongodb_controller.PROBLEM_ID] = problem_id
        inspiration[mongodb_controller.SCHEMA_ID] = schema_id
        inspiration[mongodb_controller.STATUS] = mongodb_controller.STATUS_ACCEPTED
        mongodb_controller.add_inspiration(inspiration)
        new_inspirations_count += 1
    mongodb_controller.increment_inspiration_hit_count(inspiration_hit_id, new_inspirations_count)
    return new_inspirations_count


def update_inspirations_for_problem(problem_id):
    new_inspirations_count = 0
    for inspiration_hit in mongodb_controller.get_inspiration_hits(problem_id):
        if inspiration_hit[mongodb_controller.COUNT] != inspiration_hit[mongodb_controller.COUNT_GOAL]:
            new_inspirations_count += pull_inspiration_hit_results(inspiration_hit)
    mongodb_controller.increment_inspiration_count(problem_id, new_inspirations_count)


###############################################################################

def pull_idea_hit_results(idea_hit):
    idea_hit_id = idea_hit[mongodb_controller.HIT_ID]
    schema_id = idea_hit[mongodb_controller.SCHEMA_ID]
    inspiration_id = idea_hit[mongodb_controller.INSPIRATION_ID]
    problem_id = idea_hit[mongodb_controller.PROBLEM_ID]

    ideas = mturk_controller.get_idea_hit_results(idea_hit_id)
    new_ideas_count = 0
    for idea in ideas:
        idea_id = idea[mongodb_controller.IDEA_ID]
        if mongodb_controller.contains_idea(idea_id):
            continue
        # replace time with a readable one
        epoch_time_ms = long(idea.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        idea[mongodb_controller.TIME_CREATED] = readable_time
        # add problem id, schema id, inspiration_id, and status
        idea[mongodb_controller.PROBLEM_ID] = problem_id
        idea[mongodb_controller.SCHEMA_ID] = schema_id
        idea[mongodb_controller.INSPIRATION_ID] = inspiration_id
        idea[mongodb_controller.STATUS] = mongodb_controller.STATUS_NEW
        mongodb_controller.add_idea(idea)
        new_ideas_count += 1
    mongodb_controller.increment_inspiration_hit_count(idea_hit_id, new_ideas_count)
    return new_ideas_count


def update_ideas_for_problem(problem_id):
    new_ideas_count = 0
    for idea_hit in mongodb_controller.get_idea_hits(problem_id):
        if idea_hit[mongodb_controller.COUNT] != idea_hit[mongodb_controller.COUNT_GOAL]:
            new_ideas_count += pull_idea_hit_results(idea_hit)
    mongodb_controller.increment_idea_count(problem_id, new_ideas_count)


###############################################################################

def update_suggestions(problem_id):
    # start = time.clock()
    for suggestion_hit in mongodb_controller.get_suggestion_hits(problem_id):
        if suggestion_hit[mongodb_controller.COUNT_GOAL] == suggestion_hit[mongodb_controller.COUNT]:
            continue
        suggestion_hit_id = suggestion_hit[mongodb_controller.HIT_ID]
        feedback_id = suggestion_hit[mongodb_controller.FEEDBACK_ID]
        problem_id = suggestion_hit[mongodb_controller.PROBLEM_ID]
        idea_id = suggestion_hit[mongodb_controller.IDEA_ID]
        suggestions = mturk_controller.get_suggestion_hit_results(suggestion_hit_id)
        if suggestions == "FAIL":
            continue
        for suggestion in suggestions:
            if mongodb_controller.contains_suggestion(suggestion[mongodb_controller.SUGGESTION_ID]):
                continue
            mongodb_controller.increment_suggestion_hit_count_by_one(suggestion_hit_id)
            mongodb_controller.increment_suggestion_count_by_one(idea_id)

            # replace time with a readable one and add to DB
            epoch_time_ms = long(suggestion.pop(mongodb_controller.TIME_CREATED))
            epoch_time = epoch_time_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
            suggestion[mongodb_controller.TIME_CREATED] = readable_time
            # add feedback_id, problem_id, idea_id
            suggestion[mongodb_controller.PROBLEM_ID] = problem_id
            suggestion[mongodb_controller.IDEA_ID] = idea_id
            suggestion[mongodb_controller.FEEDBACK_ID] = feedback_id
            mongodb_controller.add_suggestion(suggestion)
    # elapsed = time.clock()
    # elapsed = elapsed - start
    # print "Done updating suggestions! Time spent:", elapsed*1000
