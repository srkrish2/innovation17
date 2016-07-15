import abc
import mongodb_controller as mc
from constants import *


def get_count_dicts_for_user(username):
    result = []
    for problem_dict in mc.get_problems_by_user(username):
        problem_id = problem_dict[mc.PROBLEM_ID]
        for_result = {mc.PROBLEM_ID: problem_id}
        counter = WellRankedSchemaCounter()
        for_result[SCHEMA_COUNT] = counter.get_count(problem_id)
        counter = WellRankedInspirationCounter()
        for_result[INSPIRATION_COUNT] = counter.get_count(problem_id)
        counter = WellRankedIdeaCounter()
        for_result[IDEA_COUNT] = counter.get_count(problem_id)
        counter = WellRankedSuggestionCounter()
        for_result[SUGGESTION_COUNT] = counter.get_count(problem_id)
        result.append(for_result)
    return result


class WellRankedCounter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_dicts(self, problem_id):
        return []

    @abc.abstractmethod
    def is_ranking_disabled(self):
        return True

    def get_count(self, problem_id):
        well_ranked_count = 0
        for dictionary in self.get_dicts(problem_id):
            if self.is_ranking_disabled() or dictionary[WELL_RANKED]:
                well_ranked_count += 1
        return well_ranked_count


class WellRankedSchemaCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_schema_dicts(problem_id)

    def is_ranking_disabled(self):
        return HOW_MANY_SCHEMA_RANKS == 0


class WellRankedInspirationCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_inspirations(problem_id)

    def is_ranking_disabled(self):
        return HOW_MANY_INSPIRATION_RANKS == 0


class WellRankedIdeaCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_ideas(problem_id)

    def is_ranking_disabled(self):
        return HOW_MANY_IDEA_RANKS == 0


class WellRankedSuggestionCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_suggestions_for_problem(problem_id)

    def is_ranking_disabled(self):
        return HOW_MANY_SUGGESTION_RANKS == 0
