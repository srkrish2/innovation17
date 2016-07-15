import mongodb_controller as mc
from constants import *
import mt_to_db_pullers
import abc
import mturk_controller


def update_hit_results_for_problem(problem_id):
    schema_updater.update(problem_id)
    inspiration_updater.update(problem_id)
    idea_updater.update(problem_id)
    suggestion_updater.update(problem_id)

    if HOW_MANY_SCHEMA_RANKS > 0:
        post_rank_hit_for_new_schemas(problem_id)
        update_schema_ranks(problem_id)
    if HOW_MANY_INSPIRATION_RANKS > 0:
        post_rank_hit_for_new_inspirations(problem_id)
        update_inspiration_ranks(problem_id)
    # if HOW_MANY_SUGGESTION_RANKS > 0:
    #     post_rank_hit_for_new_suggestions(problem_id)
    #     update_suggestion_ranks(problem_id)


def update_hit_results(username):
    for problem_id in mc.get_users_problem_ids(username):
        problem_dict = mc.get_problem_dict(problem_id)
        if problem_dict is not None:
            if (not problem_dict[LAZY]) or (problem_dict[STAGE] == STAGE_SUGGESTION):
                update_hit_results_for_problem(problem_id)
        else:
            print "Didn't find problem with id =", problem_id


class Updater(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_hit_dicts(self, problem_id):
        return []

    @abc.abstractmethod
    def get_hit_object(self):
        return

    @abc.abstractmethod
    def get_item_dicts(self, problem_id):
        return []

    @abc.abstractmethod
    def get_item_id(self, item_dict):
        return

    def update(self, problem_id):
        for hit_dict in self.get_hit_dicts(problem_id):
            if hit_dict[COUNT] < hit_dict[COUNT_GOAL]:
                hit_object = self.get_hit_object()
                hit_object.pull_results(hit_dict)


class SchemaUpdater(Updater):

    def __init__(self):
        self.last_generated_ones = []

    def get_hit_dicts(self, problem_id):
        return mc.get_schema_hits(problem_id)

    def get_hit_object(self):
        return schema_hit_object

    def get_item_dicts(self, problem_id):
        return mc.get_schema_dicts(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.SCHEMA_ID]


class InspirationUpdater(Updater):
    def get_hit_dicts(self, problem_id):
        return mc.get_inspiration_hits(problem_id)

    def get_hit_object(self):
        return inspiration_hit_object

    def get_item_dicts(self, problem_id):
        return mc.get_inspirations(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.INSPIRATION_ID]


class IdeaUpdater(Updater):
    def get_hit_dicts(self, problem_id):
        return mc.get_idea_hits(problem_id)

    def get_hit_object(self):
        return idea_hit_object

    def get_item_dicts(self, problem_id):
        return mc.get_ideas(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.IDEA_ID]


class SuggestionUpdater(Updater):
    def get_hit_dicts(self, problem_id):
        return mc.get_suggestion_hits(problem_id)

    def get_hit_object(self):
        return suggestion_hit_object

    def get_item_dicts(self, problem_id):
        return mc.get_suggestions(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.SUGGESTION_ID]


def post_rank_hit_for_new_schemas(problem_id):
    schema_dicts = mc.get_new_schema_dicts(problem_id)
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


def update_schema_ranks(problem_id):
    query = {
        PROBLEM_ID: problem_id,
        SUBMITTED_BY_WORKER: False
    }
    for rank_item_hit_dict in mc.find_rank_schema_hit_dicts_with_query(query):
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


def post_rank_hit_for_new_inspirations(problem_id):
    for rank_item_hit_dict in mc.get_new_inspiration_dicts(problem_id):
        inspiration_id = rank_item_hit_dict[INSPIRATION_ID]
        inspiration_dict = mc.get_inspiration_dict(inspiration_id)
        schema_id = inspiration_dict[SCHEMA_ID]
        schema_text = mc.get_schema_text(schema_id)
        inspiration_link = inspiration_dict[INSPIRATION_LINK]
        rank_hit_creator = mturk_controller.RankInspirationHITCreator(schema_text, inspiration_link,
                                                                      HOW_MANY_INSPIRATION_RANKS)
        rank_item_hit_id = rank_hit_creator.post()
        mc.insert_new_rank_inspiration_hit(inspiration_id, rank_item_hit_id)


def update_inspiration_ranks(problem_id):
    for inspiration_dict in mc.get_inspirations(problem_id):
        inspiration_id = inspiration_dict[INSPIRATION_ID]
        query = {
            INSPIRATION_ID: inspiration_id,
            SUBMITTED_BY_WORKER: False
        }
        for rank_item_hit_dict in mc.find_rank_inspiration_hits_dict_with_query(query):
            accepted_num = mt_to_db_pullers.pull_rank_inspiration_results(rank_item_hit_dict)
            if accepted_num == FAIL or accepted_num == 0:
                continue
            inspiration_rank_dicts = mc.get_inspiration_rank_dicts(inspiration_id)
            rank = 0
            for inspiration_rank_dict in inspiration_rank_dicts:
                rank += inspiration_rank_dict[RANK]
            rank /= accepted_num
            if rank >= MIN_CATEGORY_RANK:
                mc.inspiration_set_well_ranked(inspiration_id)


schema_updater = SchemaUpdater()
inspiration_updater = InspirationUpdater()
idea_updater = IdeaUpdater()
suggestion_updater = SuggestionUpdater()

schema_hit_object = mt_to_db_pullers.SchemaHIT()
inspiration_hit_object = mt_to_db_pullers.InspirationHIT()
idea_hit_object = mt_to_db_pullers.IdeaHIT()
suggestion_hit_object = mt_to_db_pullers.SuggestionHIT()
