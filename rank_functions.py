from constants import *
import mongodb_controller as mc
import mturk_controller
import mt_to_db_pullers
from utility_functions import is_valid_url


def post_rank_hit_for_new_schemas(problem_id):
    schema_dicts = list(mc.get_new_schema_dicts(problem_id))
    if len(schema_dicts) < HOW_MANY_SCHEMAS_IN_ONE_RANK_HIT:
        return
    batch = []
    for schema_dict in schema_dicts:
        batch.append(schema_dict[SCHEMA_ID])
        if len(batch) == HOW_MANY_SCHEMAS_IN_ONE_RANK_HIT:
            schemas = []
            for i in xrange(HOW_MANY_SCHEMAS_IN_ONE_RANK_HIT):
                schema_id = batch[i]
                schemas.append(mc.get_schema_text(schema_id))
                mc.set_schema_posted_for_rank(schema_id)
            problem_text = mc.get_problem_description(problem_id)
            rank_hit_creator = mturk_controller.RankSchemaHITCreator(problem_text, schemas, HOW_MANY_SCHEMA_RANKS)
            rank_item_hit_id = rank_hit_creator.post()
            if rank_item_hit_id == "FAIL":
                print "FAIL when posting rank hit!"
                continue
            mc.insert_new_rank_schema_hit(batch, rank_item_hit_id, problem_id)
            batch = []


def post_rank_hit_for_new_inspirations(problem_id):
    for rank_item_hit_dict in mc.get_new_inspiration_dicts(problem_id):
        inspiration_id = rank_item_hit_dict[INSPIRATION_ID]
        inspiration_dict = mc.get_inspiration_dict(inspiration_id)
        schema_id = inspiration_dict[SCHEMA_ID]
        schema_text = mc.get_schema_text(schema_id)
        inspiration_link = inspiration_dict[INSPIRATION_LINK]
        if is_valid_url(inspiration_link):
            rank_hit_creator = mturk_controller.RankInspirationHITCreator(schema_text, inspiration_link,
                                                                          HOW_MANY_INSPIRATION_RANKS)
            rank_item_hit_id = rank_hit_creator.post()
            if rank_item_hit_id == "FAIL":
                print "FAIL when posting rank hit!"
                continue
            mc.insert_new_rank_inspiration_hit(inspiration_id, rank_item_hit_id, problem_id)
        mc.set_inspiration_posted_for_rank(inspiration_id)


def post_rank_hit_for_new_suggestions(problem_id):
    query = {
        PROBLEM_ID: problem_id,
        POSTED_FOR_RANK: False
    }
    suggestion_dicts = list(mc.search_suggestions(query))
    if len(suggestion_dicts) < HOW_MANY_SUGGESTIONS_IN_ONE_RANK_HIT:
        return
    batch = []
    for suggestion_dict in suggestion_dicts:
        idea_id = suggestion_dict[IDEA_ID]
        idea_dict = mc.get_idea_dict(idea_id)
        feedback_id = suggestion_dict[FEEDBACK_ID]
        feedback_dict = mc.get_feedback_dict(feedback_id)
        batch.append(suggestion_dict[SUGGESTION_ID])
        if len(batch) == HOW_MANY_SUGGESTIONS_IN_ONE_RANK_HIT:
            suggestion_texts = []
            for suggestion_id in batch:
                suggestion_texts.append(mc.get_suggestion_dict(suggestion_id)[TEXT])
                mc.set_suggestion_posted_for_rank(suggestion_id)
            problem_text = mc.get_problem_description(problem_id)
            idea_text = idea_dict[TEXT]
            feedback_text = feedback_dict[TEXT]
            rank_hit_creator = mturk_controller.RankSuggestionHITCreator(problem_text, idea_text, feedback_text,
                                                                         suggestion_texts,
                                                                         HOW_MANY_SUGGESTIONS_IN_ONE_RANK_HIT)
            rank_item_hit_id = rank_hit_creator.post()
            if rank_item_hit_id == "FAIL":
                print "FAIL when posting rank hit!"
                continue
            mc.insert_new_rank_suggestion_hit(batch, rank_item_hit_id, problem_id)
            batch = []


def update_schema_ranks(problem_id):
    query = {
        PROBLEM_ID: problem_id,
        SUBMITTED_BY_WORKER: False
    }
    for rank_item_hit_dict in mc.search_rank_schema_hits(query):
        accepted_num = mt_to_db_pullers.pull_rank_schema_results(rank_item_hit_dict)
        if accepted_num == RESTART:
            for schema_id in rank_item_hit_dict[SCHEMA_IDS]:
                mc.set_schema_posted_for_rank(schema_id, False)
            print "restarted..."
            continue
        elif accepted_num == FAIL or accepted_num == 0:
            continue
        for schema_id in rank_item_hit_dict[SCHEMA_IDS]:
            category1_sum = 0
            category2_sum = 0
            for schema_rank_dict in mc.get_schema_rank_dicts(schema_id):
                category1_sum += schema_rank_dict[CATEGORY1]
                category2_sum += schema_rank_dict[CATEGORY2]
            category1_average = category1_sum/accepted_num
            category2_average = category2_sum/accepted_num
            if category1_average >= MIN_CATEGORY_RANK and category2_average >= MIN_CATEGORY_RANK:
                mc.schema_set_well_ranked(schema_id)


def update_inspiration_ranks(problem_id):
    query = {
        PROBLEM_ID: problem_id,
        SUBMITTED_BY_WORKER: False
    }
    for rank_item_hit_dict in mc.search_rank_inspiration_hits(query):
        accepted_num = mt_to_db_pullers.pull_rank_inspiration_results(rank_item_hit_dict)
        if accepted_num == FAIL or accepted_num == 0:
            continue
        inspiration_id = rank_item_hit_dict[INSPIRATION_ID]
        inspiration_rank_dicts = mc.get_inspiration_rank_dicts(inspiration_id)
        rank = 0
        for inspiration_rank_dict in inspiration_rank_dicts:
            rank += inspiration_rank_dict[RANK]
        rank /= accepted_num
        if rank >= MIN_CATEGORY_RANK:
            mc.inspiration_set_well_ranked(inspiration_id)


def update_suggestion_ranks(problem_id):
    query = {
        PROBLEM_ID: problem_id,
        SUBMITTED_BY_WORKER: False
    }
    for rank_item_hit_dict in mc.search_rank_suggestion_hits(query):
        accepted_num = mt_to_db_pullers.pull_rank_suggestion_results(rank_item_hit_dict)
        if accepted_num == FAIL or accepted_num == 0:
            continue
        for suggestion_id in rank_item_hit_dict[SUGGESTION_IDS]:
            rank = 0
            for suggestion_rank_dict in mc.get_suggestion_rank_dicts(suggestion_id):
                rank += suggestion_rank_dict[RANK]
            rank_average = rank/accepted_num
            if rank_average >= MIN_CATEGORY_RANK:
                mc.suggestion_set_well_ranked(suggestion_id)
