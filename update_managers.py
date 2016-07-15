import mongodb_controller as mc
from constants import *
import mt_to_db_pullers
import abc
import rank_functions


def update_hit_results_for_problem(problem_id):
    schema_updater.update(problem_id)
    inspiration_updater.update(problem_id)
    idea_updater.update(problem_id)
    suggestion_updater.update(problem_id)

    if HOW_MANY_SCHEMA_RANKS > 0:
        rank_functions.post_rank_hit_for_new_schemas(problem_id)
        rank_functions.update_schema_ranks(problem_id)
    if HOW_MANY_INSPIRATION_RANKS > 0:
        rank_functions.post_rank_hit_for_new_inspirations(problem_id)
        rank_functions.update_inspiration_ranks(problem_id)
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


schema_updater = SchemaUpdater()
inspiration_updater = InspirationUpdater()
idea_updater = IdeaUpdater()
suggestion_updater = SuggestionUpdater()

schema_hit_object = mt_to_db_pullers.SchemaHIT()
inspiration_hit_object = mt_to_db_pullers.InspirationHIT()
idea_hit_object = mt_to_db_pullers.IdeaHIT()
suggestion_hit_object = mt_to_db_pullers.SuggestionHIT()
