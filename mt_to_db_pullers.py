import mongodb_controller as mc
import datetime
from constants import *
import abc
import mturk_controller


def add_readable_time(mturk_dict):
    # pop epoch time
    epoch_time_ms = long(mturk_dict.pop(TIME_CREATED))
    epoch_time = epoch_time_ms / 1000.0
    readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
    # add readable time
    mturk_dict[TIME_CREATED] = readable_time


class HITObject:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_mturk_dicts(self, hit_id):
        return []

    @abc.abstractmethod
    def get_item_id_from_mturk_dict(self, mturk_dict):
        return ""

    @abc.abstractmethod
    def is_contained(self, item_id):
        return True

    @abc.abstractmethod
    def add_useful_fields(self, schema_dict, hit_dict):
        return

    @abc.abstractmethod
    def add_mturk_dict_to_db(self, schema_dict):
        return

    @abc.abstractmethod
    def increment_count(self, hit_id, new_dicts_count):
        return

    def pull_results(self, hit_dict):
        hit_id = hit_dict[HIT_ID]
        mturk_dicts = self.get_mturk_dicts(hit_id)
        if mturk_dicts == "FAIL":
            print "FAIL when getting mturk dicts!"
            return
        new_dicts_count = 0
        for mturk_dict in mturk_dicts:
            item_id = self.get_item_id_from_mturk_dict(mturk_dict)
            if self.is_contained(item_id):
                continue
            add_readable_time(mturk_dict)
            mturk_dict[POSTED_FOR_RANK] = False
            mturk_dict[WELL_RANKED] = False
            self.add_useful_fields(mturk_dict, hit_dict)
            self.add_mturk_dict_to_db(mturk_dict)
            new_dicts_count += 1
        self.increment_count(hit_id, new_dicts_count)


class SchemaHIT(HITObject):

    def get_item_id_from_mturk_dict(self, schema_dict):
        return schema_dict[SCHEMA_ID]

    def get_mturk_dicts(self, schema_hit_id):
        result_getter = mturk_controller.GeneratedSchemas()
        return result_getter.get_results(schema_hit_id)

    def is_contained(self, schema_id):
        return mc.contains_schema(schema_id)

    def add_useful_fields(self, schema_dict, schema_hit_dict):
        # add problem_id, status, and rank
        schema_dict[STATUS] = mc.STATUS_ACCEPTED
        schema_dict[PROBLEM_ID] = schema_hit_dict[PROBLEM_ID]

    def add_mturk_dict_to_db(self, schema_dict):
        mc.add_schema(schema_dict)

    def increment_count(self, schema_hit_id, new_dicts_count):
        mc.increment_schema_hit_count(schema_hit_id, new_dicts_count)


class InspirationHIT(HITObject):

    def get_mturk_dicts(self, inspiration_hit_id):
        result_getter = mturk_controller.GeneratedInspirations()
        return result_getter.get_results(inspiration_hit_id)

    def get_item_id_from_mturk_dict(self, inspiration_dict):
        return inspiration_dict[INSPIRATION_ID]

    def is_contained(self, inspiration_id):
        return mc.contains_inspiration(inspiration_id)

    def add_useful_fields(self, inspiration_dict, inspiration_hit_dict):
        # add problem id, schema id, status, and rank
        inspiration_dict[PROBLEM_ID] = inspiration_hit_dict[PROBLEM_ID]
        inspiration_dict[SCHEMA_ID] = inspiration_hit_dict[SCHEMA_ID]
        inspiration_dict[STATUS] = mc.STATUS_ACCEPTED

    def add_mturk_dict_to_db(self, inspiration_dict):
        mc.add_inspiration(inspiration_dict)

    def increment_count(self, inspiration_hit_id, new_dicts_count):
        mc.increment_inspiration_hit_count(inspiration_hit_id, new_dicts_count)


class IdeaHIT(HITObject):

    def get_mturk_dicts(self, hit_id):
        result_getter = mturk_controller.GeneratedIdeas()
        result = result_getter.get_results(hit_id)
        return result

    def get_item_id_from_mturk_dict(self, mturk_dict):
        return mturk_dict[IDEA_ID]

    def is_contained(self, idea_id):
        return mc.contains_idea(idea_id)

    def add_useful_fields(self, idea_dict, hit_dict):
        # add problem id, schema id, inspiration_id, and status
        idea_dict[PROBLEM_ID] = hit_dict[PROBLEM_ID]
        idea_dict[SCHEMA_ID] = hit_dict[SCHEMA_ID]
        idea_dict[INSPIRATION_ID] = hit_dict[INSPIRATION_ID]
        idea_dict[STATUS] = mc.STATUS_NEW

    def add_mturk_dict_to_db(self, idea_dict):
        mc.add_idea(idea_dict)

    def increment_count(self, idea_hit_id, new_ideas_count):
        mc.increment_idea_hit_count(idea_hit_id, new_ideas_count)


class SuggestionHIT(HITObject):

    def get_mturk_dicts(self, suggestion_hit_id):
        result_getter = mturk_controller.GeneratedSuggestions()
        return result_getter.get_results(suggestion_hit_id)

    def get_item_id_from_mturk_dict(self, mturk_dict):
        return mturk_dict[SUGGESTION_ID]

    def is_contained(self, suggestion_id):
        return mc.contains_suggestion(suggestion_id)

    def add_useful_fields(self, suggestion_dict, hit_dict):
        # add feedback_id, problem_id, idea_id
        suggestion_dict[PROBLEM_ID] = hit_dict[PROBLEM_ID]
        suggestion_dict[IDEA_ID] = hit_dict[IDEA_ID]
        suggestion_dict[FEEDBACK_ID] = hit_dict[FEEDBACK_ID]

    def add_mturk_dict_to_db(self, suggestion_dict):
        mc.add_suggestion(suggestion_dict)

    def increment_count(self, suggestion_hit_id, new_suggestions_count):
        mc.increment_suggestion_hit_count(suggestion_hit_id, new_suggestions_count)


def pull_rank_schema_results(hit_dict):
    hit_id = hit_dict[HIT_ID]
    result_getter = mturk_controller.GeneratedSchemaRanks()
    mturk_dicts = result_getter.get_results(hit_id)
    if mturk_dicts == FAIL:
        print "FAIL when getting mturk dicts!"
        return FAIL
    elif mturk_dicts == RESTART:
        print "Need to RESTART!"
        mc.rank_schema_hit_set_submitted(hit_id)
        return RESTART

    schema_ids = hit_dict[SCHEMA_IDS]
    if len(mturk_dicts) > 0:
        mc.rank_schema_hit_set_submitted(hit_id)
    for mturk_dict in mturk_dicts:
        add_readable_time(mturk_dict)
        ranks = mturk_dict[RANKS_FIELD]
        for i in xrange(0, len(ranks), 2):
            schema_id = schema_ids[i/2]
            schema_rank_for_db = {
                RANK_ID: mturk_dict[RANK_ID],
                CATEGORY1: ranks[i],
                CATEGORY2: ranks[i+1],
                TIME_CREATED: mturk_dict[TIME_CREATED],
                WORKER_ID: mturk_dict[WORKER_ID],
                SCHEMA_ID: schema_id
            }
            mc.insert_schema_rank(schema_rank_for_db)
    return len(mturk_dicts)  # return how many assignments were accepted


def pull_rank_inspiration_results(hit_dict):
    hit_id = hit_dict[HIT_ID]
    inspiration_id = hit_dict[INSPIRATION_ID]
    result_getter = mturk_controller.GeneratedInspirationRanks()
    mturk_dicts = result_getter.get_results(hit_id)
    if mturk_dicts == FAIL:
        print "FAIL when getting mturk dicts!"
        return FAIL
    if len(mturk_dicts) > 0:
        mc.rank_inspiration_hit_set_submitted(hit_id)
    for mturk_dict in mturk_dicts:
        add_readable_time(mturk_dict)
        mturk_dict[INSPIRATION_ID] = inspiration_id
        mc.insert_inspiration_rank(mturk_dict)
    return len(mturk_dicts)


def pull_rank_suggestion_results(hit_dict):
    hit_id = hit_dict[HIT_ID]
    result_getter = mturk_controller.GeneratedSuggestionRanks()
    mturk_dicts = result_getter.get_results(hit_id)
    if mturk_dicts == FAIL:
        print "FAIL when getting mturk dicts!"
        return FAIL

    suggestion_ids = hit_dict[SUGGESTION_IDS]
    if len(mturk_dicts) > 0:
        mc.rank_suggestion_hit_set_submitted(hit_id)
    for mturk_dict in mturk_dicts:
        # rank_dict = {
        #     RANKS_FIELD: ranks,
        #     TIME_CREATED: epoch_time_ms_string,
        #     WORKER_ID: worker_id,
        #     RANK_ID: assignment_id
        # }
        add_readable_time(mturk_dict)
        ranks = mturk_dict[RANKS_FIELD]
        for i in xrange(len(ranks)):
            suggestion_id = suggestion_ids[i]
            suggestion_rank_for_db = {
                RANK_ID: mturk_dict[RANK_ID],
                RANK: ranks[i],
                TIME_CREATED: mturk_dict[TIME_CREATED],
                WORKER_ID: mturk_dict[WORKER_ID],
                SUGGESTION_ID: suggestion_id
            }
            mc.insert_suggestion_rank(suggestion_rank_for_db)
    return len(mturk_dicts)  # return how many assignments were accepted