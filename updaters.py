import mongodb_controller as mc
from constants import *
import hit_objects
import abc


def update_hit_results(username):
    for problem_id in mc.get_users_problem_ids(username):
        if not mc.did_reach_schema_count_goal(problem_id):
            schema_updater = SchemaUpdater()
            schema_updater.update(problem_id)
        if not mc.did_reach_inspiration_count_goal(problem_id):
            inspiration_updater = InspirationUpdater()
            inspiration_updater.update(problem_id)
        if not mc.did_reach_idea_count_goal(problem_id):
            idea_updater = IdeaUpdater()
            idea_updater.update(problem_id)
        counter = WellRankedSchemaCounter()
        counter.update(problem_id)
        counter = WellRankedInspirationCounter()
        counter.update(problem_id)
        counter = WellRankedIdeaCounter()
        counter.update(problem_id)


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

    @abc.abstractmethod
    def get_rank_item_hit_dict(self, item_id):
        return

    @abc.abstractmethod
    def get_rank_item_hit_object(self):
        return

    def update(self, problem_id):
        for hit_dict in self.get_hit_dicts(problem_id):
            if hit_dict[mc.COUNT] < hit_dict[mc.COUNT_GOAL]:
                hit_object = self.get_hit_object()
                hit_object.pull_results(hit_dict)
        for item_dict in self.get_item_dicts(problem_id):
            item_id = self.get_item_id(item_dict)
            rank_item_hit_dict = self.get_rank_item_hit_dict(item_id)
            count = rank_item_hit_dict[mc.COUNT]
            count_goal = rank_item_hit_dict[mc.COUNT_GOAL]
            if count < count_goal:
                hit_object = self.get_rank_item_hit_object()
                hit_object.pull_results(rank_item_hit_dict)


class SchemaUpdater(Updater):
    def get_hit_dicts(self, problem_id):
        return mc.get_schema_hits(problem_id)

    def get_hit_object(self):
        return hit_objects.SchemaHIT()

    def get_item_dicts(self, problem_id):
        return mc.get_schema_dicts(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.SCHEMA_ID]

    def get_rank_item_hit_dict(self, item_id):
        return mc.get_rank_schema_hit_dict(item_id)

    def get_rank_item_hit_object(self):
        return hit_objects.RankSchemaHIT()


class InspirationUpdater(Updater):
    def get_hit_dicts(self, problem_id):
        return mc.get_inspiration_hits(problem_id)

    def get_hit_object(self):
        return hit_objects.InspirationHIT()

    def get_item_dicts(self, problem_id):
        return mc.get_inspirations(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.INSPIRATION_ID]

    def get_rank_item_hit_dict(self, item_id):
        return mc.get_rank_inspiration_hit_dict(item_id)

    def get_rank_item_hit_object(self):
        return hit_objects.RankInspirationHIT()


class IdeaUpdater(Updater):
    def get_hit_dicts(self, problem_id):
        return mc.get_idea_hits(problem_id)

    def get_hit_object(self):
        return hit_objects.IdeaHIT()

    def get_item_dicts(self, problem_id):
        return mc.get_ideas(problem_id)

    def get_item_id(self, item_dict):
        return item_dict[mc.IDEA_ID]

    def get_rank_item_hit_dict(self, item_id):
        return mc.get_rank_idea_hit_dict(item_id)

    def get_rank_item_hit_object(self):
        return hit_objects.RankIdeaHIT()


class WellRankedCounter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_dicts(self, problem_id):
        return []

    @abc.abstractmethod
    def set_count(self, problem_id, count):
        return

    def update(self, problem_id):
        well_ranked_count = 0
        for dictionary in self.get_dicts(problem_id):
            if dictionary[mc.RANK] >= MIN_RANK:
                well_ranked_count += 1
        self.set_count(problem_id, well_ranked_count)


class WellRankedSchemaCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_schema_dicts(problem_id)

    def set_count(self, problem_id, count):
        mc.set_schema_count(problem_id, count)


class WellRankedInspirationCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_inspirations(problem_id)

    def set_count(self, problem_id, count):
        mc.set_inspiration_count(problem_id, count)


class WellRankedIdeaCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_ideas(problem_id)

    def set_count(self, problem_id, count):
        mc.set_idea_count(problem_id, count)


###############################################################################

def update_suggestions(problem_id):
    for suggestion_hit_dict in mc.get_suggestion_hits(problem_id):
        if suggestion_hit_dict[mc.COUNT_GOAL] == suggestion_hit_dict[mc.COUNT]:
            continue
        hit_object = hit_objects.SuggestionHIT()
        hit_object.pull_results(suggestion_hit_dict)
