import abc
from constants import *
import update_managers
import time
import mongodb_controller as mc


class Waiter(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, pool, problem_id):
        self.pool = pool
        self.problem_id = problem_id

    def wait_until_done(self):
        async_result = self.pool.apply_async(self.wait_for_count)
        return async_result.get()

    def wait_for_count(self):
        while True:
            update_managers.update_hit_results_for_problem(self.problem_id)
            if self.is_done():
                return True
            time.sleep(PERIOD)

    def is_done(self):
        for hit_dict in self.get_hit_dicts():
            if hit_dict[COUNT] != hit_dict[COUNT_GOAL]:
                return False
        if self.needs_ranking():
            for item_dict in self.get_item_dicts():
                if not item_dict[POSTED_FOR_RANK]:
                    return False
            for rank_item_hit_dict in self.get_rank_item_hit_dicts():
                if not rank_item_hit_dict[SUBMITTED_BY_WORKER]:
                    return False
        return True

    @abc.abstractmethod
    def get_hit_dicts(self):
        return []

    @abc.abstractmethod
    def needs_ranking(self):
        return False

    @abc.abstractmethod
    def get_item_dicts(self):
        return []

    def get_rank_item_hit_dicts(self):
        return []


class SchemaStageWaiter(Waiter):

    def get_hit_dicts(self):
        return mc.get_schema_hits(self.problem_id)

    def needs_ranking(self):
        return HOW_MANY_SCHEMA_RANKS > 0

    def get_item_dicts(self):
        return mc.get_schema_dicts(self.problem_id)

    def get_rank_item_hit_dicts(self):
        return mc.search_rank_schema_hits({})


class InspirationStageWaiter(Waiter):

    def get_hit_dicts(self):
        return mc.get_inspiration_hits(self.problem_id)

    def needs_ranking(self):
        return HOW_MANY_INSPIRATION_RANKS > 0

    def get_item_dicts(self):
        return mc.get_inspirations(self.problem_id)

    def get_rank_item_hit_dicts(self):
        return mc.search_rank_inspiration_hits({})


class IdeaStageWaiter(Waiter):

    def get_hit_dicts(self):
        return mc.get_idea_hits(self.problem_id)

    def needs_ranking(self):
        return HOW_MANY_IDEA_RANKS > 0

    def get_item_dicts(self):
        return mc.get_ideas(self.problem_id)
