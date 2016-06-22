import mongodb_controller as mc
import mturk_controller
import datetime
from constants import READABLE_TIME_FORMAT, HOW_MANY_RANKS, MIN_RANK


def update_hit_results(username):
    # start = time.clock()
    for problem_id in mc.get_users_problem_ids(username):
        if not mc.did_reach_schema_count_goal(problem_id):
            update_schemas_for_problem(problem_id)
        if not mc.did_reach_inspiration_count_goal(problem_id):
            update_inspirations_for_problem(problem_id)
        if not mc.did_reach_idea_count_goal(problem_id):
            update_ideas_for_problem(problem_id)
        update_problems_schema_count(problem_id)
        update_problems_inspiration_count(problem_id)
    # elapsed = time.clock()
    # elapsed = elapsed - start
    # print "Done updating! Time spent:", elapsed*1000


###############################################################################

def update_schemas_for_problem(problem_id):
    for schema_hit in mc.get_schema_hits(problem_id):
        if schema_hit[mc.COUNT] != schema_hit[mc.COUNT_GOAL]:
            pull_schema_hit_results(schema_hit)
    for schema in mc.get_schema_dicts(problem_id):
        schema_id = schema[mc.SCHEMA_ID]
        rank_schema_hit_dict = mc.get_rank_schema_hit_dict(schema_id)
        count = rank_schema_hit_dict[mc.COUNT]
        count_goal = rank_schema_hit_dict[mc.COUNT_GOAL]
        if count < count_goal:
            pull_rank_schema_hit_results(rank_schema_hit_dict)


def pull_schema_hit_results(schema_hit):
    schema_hit_id = schema_hit[mc.HIT_ID]
    problem_id = schema_hit[mc.PROBLEM_ID]
    schema_dicts = mturk_controller.get_schema_making_results(schema_hit_id)
    if schema_dicts == "FAIL":
        print "mturk_controller.get_schema_making_results - FAIL!"
        return
    for schema_dict in schema_dicts:
        schema_id = schema_dict[mc.SCHEMA_ID]
        if mc.contains_schema(schema_id):
            continue

        # pop epoch time
        epoch_time_ms = long(schema_dict.pop(mc.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        schema_dict[mc.TIME_CREATED] = readable_time
        # add problem_id, status, and rank
        schema_dict[mc.STATUS] = mc.STATUS_ACCEPTED
        schema_dict[mc.PROBLEM_ID] = problem_id
        schema_dict[mc.RANK] = 0
        mc.add_schema(schema_dict)

        # launch rank schema
        rank_schema_hit_id = mturk_controller.create_rank_schema_hit(schema_dict[mc.TEXT],
                                                                     HOW_MANY_RANKS)
        mc.insert_new_rank_schema_hit(schema_id, HOW_MANY_RANKS, rank_schema_hit_id)
        mc.increment_schema_hit_count_by_one(schema_hit_id)


def pull_rank_schema_hit_results(rank_schema_hit):
    rank_schema_hit_id = rank_schema_hit[mc.HIT_ID]
    schema_id = rank_schema_hit[mc.SCHEMA_ID]
    rank_dicts = mturk_controller.get_ranking_results(rank_schema_hit_id)
    if rank_dicts == "FAIL":
        print "mturk_controller.get_ranking_results - FAIL!"
        return
    new_ranks_count = 0
    for rank_dict in rank_dicts:
        rank_id = rank_dict[mc.RANK_ID]
        if mc.contains_schema_rank(rank_id):
            continue
        # pop epoch time
        epoch_time_ms = long(rank_dict.pop(mc.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        rank_dict[mc.TIME_CREATED] = readable_time
        # add schema_id
        rank_dict[mc.SCHEMA_ID] = schema_id

        mc.add_schema_rank(rank_dict)
        new_ranks_count += 1
        mc.increment_schema_rank(schema_id, rank_dict[mc.RANK])
    mc.increment_rank_schema_hit_count(rank_schema_hit_id, new_ranks_count)
    return new_ranks_count


def update_problems_schema_count(problem_id):
    well_ranked_count = 0
    for schema_dict in mc.get_schema_dicts(problem_id):
        # schema_id = schema_dict[mc.SCHEMA_ID]
        # rank_schema_hit_dict = mc.get_rank_schema_hit_dict(schema_id)
        # count = rank_schema_hit_dict[mc.COUNT]
        # count_goal = rank_schema_hit_dict[mc.COUNT_GOAL]
        if schema_dict[mc.RANK] >= MIN_RANK:
            well_ranked_count += 1
    mc.set_schema_count(problem_id, well_ranked_count)


def update_problems_inspiration_count(problem_id):
    well_ranked_count = 0
    for inspiration_dict in mc.get_inspirations(problem_id):
        if inspiration_dict[mc.RANK] >= MIN_RANK:
            well_ranked_count += 1
    mc.set_inspiration_count(problem_id, well_ranked_count)


###############################################################################

def update_inspirations_for_problem(problem_id):
    for inspiration_hit in mc.get_inspiration_hits(problem_id):
        if inspiration_hit[mc.COUNT] != inspiration_hit[mc.COUNT_GOAL]:
            pull_inspiration_hit_results(inspiration_hit)
    for inspiration_dict in mc.get_inspirations(problem_id):
        inspiration_id = inspiration_dict[mc.INSPIRATION_ID]
        rank_inspiration_hit_dict = mc.get_rank_inspiration_hit_dict(inspiration_id)
        count = rank_inspiration_hit_dict[mc.COUNT]
        count_goal = rank_inspiration_hit_dict[mc.COUNT_GOAL]
        if count < count_goal:
            pull_rank_inspiration_hit_results(rank_inspiration_hit_dict)


def pull_inspiration_hit_results(inspiration_hit):
    inspiration_hit_id = inspiration_hit[mc.HIT_ID]
    schema_id = inspiration_hit[mc.SCHEMA_ID]
    problem_id = inspiration_hit[mc.PROBLEM_ID]
    inspirations = mturk_controller.get_inspiration_hit_results(inspiration_hit_id)
    if inspirations == "FAIL":
        print "mturk_controller.get_inspiration_hit_results - FAIL!"
        return
    new_inspirations_count = 0
    for inspiration in inspirations:
        inspiration_id = inspiration[mc.INSPIRATION_ID]
        if mc.contains_inspiration(inspiration_id):
            continue
        # replace time with a readable one
        epoch_time_ms = long(inspiration.pop(mc.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        inspiration[mc.TIME_CREATED] = readable_time
        # add problem id, schema id, status, and rank
        inspiration[mc.PROBLEM_ID] = problem_id
        inspiration[mc.SCHEMA_ID] = schema_id
        inspiration[mc.STATUS] = mc.STATUS_ACCEPTED
        inspiration[mc.RANK] = 0

        mc.add_inspiration(inspiration)
        new_inspirations_count += 1

        # launch rank task
        problem_text = mc.get_problem_description(problem_id)
        schema_text = mc.get_schema_text(schema_id)
        inspiration_link = inspiration[mc.INSPIRATION_LINK]
        inspiration_additional = inspiration[mc.INSPIRATION_ADDITIONAL]
        inspiration_reason = inspiration[mc.INSPIRATION_REASON]
        rank_inspiration_hit_id = mturk_controller.create_rank_inspiration_hit(problem_text, schema_text,
                inspiration_link, inspiration_additional, inspiration_reason, HOW_MANY_RANKS)
        mc.insert_new_rank_inspiration_hit(inspiration_id, HOW_MANY_RANKS, rank_inspiration_hit_id)
    mc.increment_inspiration_hit_count(inspiration_hit_id, new_inspirations_count)


def pull_rank_inspiration_hit_results(rank_inspiration_hit_dict):
    rank_inspiration_hit_id = rank_inspiration_hit_dict[mc.HIT_ID]
    inspiration_id = rank_inspiration_hit_dict[mc.INSPIRATION_ID]
    rank_dicts = mturk_controller.get_ranking_results(rank_inspiration_hit_id)
    if rank_dicts == "FAIL":
        print "mturk_controller.get_ranking_results - FAIL!"
        return
    new_ranks_count = 0
    for rank_dict in rank_dicts:
        rank_id = rank_dict[mc.RANK_ID]
        if mc.contains_inspiration_rank(rank_id):
            continue
        # pop epoch time
        epoch_time_ms = long(rank_dict.pop(mc.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        rank_dict[mc.TIME_CREATED] = readable_time
        # add inspiration id
        rank_dict[mc.INSPIRATION_ID] = inspiration_id

        mc.insert_inspiration_rank(rank_dict)
        new_ranks_count += 1
        mc.increment_inspiration_rank(inspiration_id, rank_dict[mc.RANK])
    mc.increment_rank_inspiration_hit_count(rank_inspiration_hit_id, new_ranks_count)
    return new_ranks_count


###############################################################################

def pull_idea_hit_results(idea_hit):
    idea_hit_id = idea_hit[mc.HIT_ID]
    schema_id = idea_hit[mc.SCHEMA_ID]
    inspiration_id = idea_hit[mc.INSPIRATION_ID]
    problem_id = idea_hit[mc.PROBLEM_ID]

    ideas = mturk_controller.get_idea_hit_results(idea_hit_id)
    new_ideas_count = 0
    for idea in ideas:
        idea_id = idea[mc.IDEA_ID]
        if mc.contains_idea(idea_id):
            continue
        # replace time with a readable one
        epoch_time_ms = long(idea.pop(mc.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        idea[mc.TIME_CREATED] = readable_time
        # add problem id, schema id, inspiration_id, and status
        idea[mc.PROBLEM_ID] = problem_id
        idea[mc.SCHEMA_ID] = schema_id
        idea[mc.INSPIRATION_ID] = inspiration_id
        idea[mc.STATUS] = mc.STATUS_NEW
        mc.add_idea(idea)
        new_ideas_count += 1
    mc.increment_inspiration_hit_count(idea_hit_id, new_ideas_count)
    return new_ideas_count


def update_ideas_for_problem(problem_id):
    new_ideas_count = 0
    for idea_hit in mc.get_idea_hits(problem_id):
        if idea_hit[mc.COUNT] != idea_hit[mc.COUNT_GOAL]:
            new_ideas_count += pull_idea_hit_results(idea_hit)
    mc.increment_idea_count(problem_id, new_ideas_count)


###############################################################################

def update_suggestions(problem_id):
    # start = time.clock()
    for suggestion_hit in mc.get_suggestion_hits(problem_id):
        if suggestion_hit[mc.COUNT_GOAL] == suggestion_hit[mc.COUNT]:
            continue
        suggestion_hit_id = suggestion_hit[mc.HIT_ID]
        feedback_id = suggestion_hit[mc.FEEDBACK_ID]
        problem_id = suggestion_hit[mc.PROBLEM_ID]
        idea_id = suggestion_hit[mc.IDEA_ID]
        suggestions = mturk_controller.get_suggestion_hit_results(suggestion_hit_id)
        if suggestions == "FAIL":
            continue
        for suggestion in suggestions:
            if mc.contains_suggestion(suggestion[mc.SUGGESTION_ID]):
                continue
            mc.increment_suggestion_hit_count_by_one(suggestion_hit_id)
            mc.increment_suggestion_count_by_one(idea_id)

            # replace time with a readable one and add to DB
            epoch_time_ms = long(suggestion.pop(mc.TIME_CREATED))
            epoch_time = epoch_time_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
            suggestion[mc.TIME_CREATED] = readable_time
            # add feedback_id, problem_id, idea_id
            suggestion[mc.PROBLEM_ID] = problem_id
            suggestion[mc.IDEA_ID] = idea_id
            suggestion[mc.FEEDBACK_ID] = feedback_id
            mc.add_suggestion(suggestion)
    # elapsed = time.clock()
    # elapsed = elapsed - start
    # print "Done updating suggestions! Time spent:", elapsed*1000
