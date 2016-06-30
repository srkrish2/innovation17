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
        result.append(for_result)
        counter = WellRankedSuggestionCounter()
        for_result[SUGGESTION_COUNT] = counter.get_count(problem_id)
        result.append(for_result)
    return result


def get_suggestion_counts_for_each_idea(problem_id):
    result = []
    for idea_dict in mc.get_ideas(problem_id):
        idea_id = idea_dict[IDEA_ID]
        counter = WellRankedIdeasSuggestionCounter()
        for_result = {
            IDEA_ID: idea_id,
            SUGGESTION_COUNT: counter.get_count(idea_id)
        }
        result.append(for_result)
    return result


class WellRankedCounter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_dicts(self, problem_id):
        return []

    def get_count(self, problem_id):
        well_ranked_count = 0
        for dictionary in self.get_dicts(problem_id):
            if dictionary[mc.RANK] >= MIN_RANK:
                well_ranked_count += 1
        return well_ranked_count


class WellRankedSchemaCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_schema_dicts(problem_id)


class WellRankedInspirationCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_inspirations(problem_id)


class WellRankedIdeaCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_ideas(problem_id)


class WellRankedSuggestionCounter(WellRankedCounter):
    def get_dicts(self, problem_id):
        return mc.get_suggestions_for_problem(problem_id)


class WellRankedIdeasSuggestionCounter(WellRankedCounter):
    def get_dicts(self, idea_id):
        return mc.get_suggestions_for_idea(idea_id)
