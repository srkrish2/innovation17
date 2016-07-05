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
        hit_dicts = self.get_hit_dicts()
        for hit_dict in hit_dicts:
            if hit_dict[COUNT] != hit_dict[COUNT_GOAL]:
                return False
            for item_dict in self.get_item_dicts():
                rank_item_hit_dict = self.get_rank_hit_dicts(item_dict)
                if rank_item_hit_dict[COUNT] != rank_item_hit_dict[COUNT_GOAL]:
                    return False
        return True

    @abc.abstractmethod
    def get_hit_dicts(self):
        return []

    @abc.abstractmethod
    def get_item_dicts(self):
        return []

    @abc.abstractmethod
    def get_rank_hit_dicts(self, item_dict):
        return []


class SchemaStageWaiter(Waiter):

    def get_hit_dicts(self):
        return mc.get_schema_hits(self.problem_id)

    def get_item_dicts(self):
        return mc.get_schema_dicts(self.problem_id)

    def get_rank_hit_dicts(self, item_dict):
        return mc.get_rank_schema_hit_dict(item_dict[SCHEMA_ID])


class InspirationStageWaiter(Waiter):

    def get_hit_dicts(self):
        return mc.get_inspiration_hits(self.problem_id)

    def get_item_dicts(self):
        return mc.get_inspirations(self.problem_id)

    def get_rank_hit_dicts(self, item_dict):
        return mc.get_rank_inspiration_hit_dict(item_dict[INSPIRATION_ID])


class IdeaStageWaiter(Waiter):

    def get_hit_dicts(self):
        return mc.get_idea_hits(self.problem_id)

    def get_item_dicts(self):
        return mc.get_ideas(self.problem_id)

    def get_rank_hit_dicts(self, item_dict):
        return mc.get_rank_idea_hit_dict(item_dict[IDEA_ID])
