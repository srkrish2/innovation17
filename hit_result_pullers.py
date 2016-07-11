import mongodb_controller as mc
import datetime
from constants import *
import abc
import mturk_controller


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

    def add_readable_time(self, mturk_dict):
        # pop epoch time
        epoch_time_ms = long(mturk_dict.pop(mc.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        mturk_dict[TIME_CREATED] = readable_time

    @abc.abstractmethod
    def add_useful_fields(self, schema_dict, hit_dict):
        return

    @abc.abstractmethod
    def add_mturk_dict_to_db(self, schema_dict):
        return

    @abc.abstractmethod
    def needs_to_post_rank(self):
        return

    @abc.abstractmethod
    def get_rank_hit_creator(self, mturk_dict):
        return

    @abc.abstractmethod
    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        return

    @abc.abstractmethod
    def increment_item_rank(self, mturk_dict):
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
            self.add_readable_time(mturk_dict)
            self.add_useful_fields(mturk_dict, hit_dict)
            if self.needs_to_post_rank():
                mturk_dict[RANK] = 0
            self.add_mturk_dict_to_db(mturk_dict)
            new_dicts_count += 1
            if HOW_MANY_RANKS != 0:
                if self.needs_to_post_rank():
                    rank_hit_creator = self.get_rank_hit_creator(mturk_dict)
                    rank_item_hit_id = rank_hit_creator.post()
                    if rank_item_hit_id == "FAIL":
                        print "FAIL when posting rank hit!"
                        continue
                    self.save_rank_hit(rank_item_hit_id, mturk_dict)
                else:
                    self.increment_item_rank(mturk_dict)
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

    def needs_to_post_rank(self):
        return True

    def get_rank_hit_creator(self, mturk_dict):
        return mturk_controller.RankSchemaHITCreator(mturk_dict[TEXT], HOW_MANY_RANKS)

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        schema_id = mturk_dict[SCHEMA_ID]
        mc.insert_new_rank_schema_hit(schema_id, HOW_MANY_RANKS, rank_item_hit_id)

    def increment_item_rank(self, mturk_dict):
        return

    def increment_count(self, schema_hit_id, new_dicts_count):
        mc.increment_schema_hit_count(schema_hit_id, new_dicts_count)


class RankSchemaHIT(HITObject):

    def get_mturk_dicts(self, rank_schema_hit_id):
        result_getter = mturk_controller.GeneratedRanks()
        return result_getter.get_results(rank_schema_hit_id)

    def get_item_id_from_mturk_dict(self, rank_dict):
        return rank_dict[RANK_ID]

    def is_contained(self, rank_id):
        return mc.contains_schema_rank(rank_id)

    def add_useful_fields(self, rank_dict, rank_schema_hit_dict):
        # add schema_id
        rank_dict[SCHEMA_ID] = rank_schema_hit_dict[SCHEMA_ID]

    def add_mturk_dict_to_db(self, rank_dict):
        mc.add_schema_rank(rank_dict)

    def needs_to_post_rank(self):
        return False

    def get_rank_hit_creator(self, mturk_dict):
        return

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        return

    def increment_item_rank(self, mturk_dict):
        mc.increment_schema_rank(mturk_dict[SCHEMA_ID], mturk_dict[RANK])

    def increment_count(self, rank_schema_hit_id, new_dicts_count):
        mc.increment_rank_schema_hit_count(rank_schema_hit_id, new_dicts_count)


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

    def needs_to_post_rank(self):
        return True

    def get_rank_hit_creator(self, mturk_dict):
        problem_text = mc.get_problem_description(mturk_dict[PROBLEM_ID])
        schema_text = mc.get_schema_text(mturk_dict[SCHEMA_ID])
        inspiration_link = mturk_dict[INSPIRATION_LINK]
        inspiration_additional = mturk_dict[INSPIRATION_ADDITIONAL]
        inspiration_reason = mturk_dict[INSPIRATION_REASON]
        return mturk_controller.RankInspirationHITCreator(problem_text, schema_text, inspiration_link,
                                                          inspiration_additional, inspiration_reason, HOW_MANY_RANKS)

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        inspiration_id = mturk_dict[INSPIRATION_ID]
        mc.insert_new_rank_inspiration_hit(inspiration_id, HOW_MANY_RANKS, rank_item_hit_id)

    def increment_item_rank(self, mturk_dict):
        return

    def increment_count(self, inspiration_hit_id, new_dicts_count):
        mc.increment_inspiration_hit_count(inspiration_hit_id, new_dicts_count)


class RankInspirationHIT(HITObject):

    def get_mturk_dicts(self, rank_inspiration_hit_id):
        result_getter = mturk_controller.GeneratedRanks()
        return result_getter.get_results(rank_inspiration_hit_id)

    def get_item_id_from_mturk_dict(self, rank_dict):
        return rank_dict[RANK_ID]

    def is_contained(self, rank_id):
        return mc.contains_inspiration_rank(rank_id)

    def add_useful_fields(self, rank_dict, hit_dict):
        # add inspiration id
        rank_dict[INSPIRATION_ID] = hit_dict[INSPIRATION_ID]

    def add_mturk_dict_to_db(self, rank_dict):
        mc.insert_inspiration_rank(rank_dict)

    def needs_to_post_rank(self):
        return False

    def get_rank_hit_creator(self, mturk_dict):
        return

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        return

    def increment_item_rank(self, mturk_dict):
        mc.increment_inspiration_rank(mturk_dict[INSPIRATION_ID], mturk_dict[RANK])

    def increment_count(self, rank_inspiration_hit_id, new_dicts_count):
        mc.increment_rank_inspiration_hit_count(rank_inspiration_hit_id, new_dicts_count)


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

    def needs_to_post_rank(self):
        return True

    def get_rank_hit_creator(self, mturk_dict):
        problem_text = mc.get_problem_description(mturk_dict[PROBLEM_ID])
        idea_text = mturk_dict[TEXT]
        return mturk_controller.RankIdeaHITCreator(problem_text, idea_text, HOW_MANY_RANKS)

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        idea_id = mturk_dict[IDEA_ID]
        mc.insert_new_rank_idea_hit(idea_id, HOW_MANY_RANKS, rank_item_hit_id)

    def increment_item_rank(self, mturk_dict):
        return

    def increment_count(self, idea_hit_id, new_ideas_count):
        mc.increment_idea_hit_count(idea_hit_id, new_ideas_count)


class RankIdeaHIT(HITObject):

    def get_mturk_dicts(self, hit_id):
        result_getter = mturk_controller.GeneratedRanks()
        return result_getter.get_results(hit_id)

    def get_item_id_from_mturk_dict(self, mturk_dict):
        return mturk_dict[RANK_ID]

    def is_contained(self, idea_rank_id):
        return mc.contains_idea_rank(idea_rank_id)

    def add_useful_fields(self, mturk_dict, hit_dict):
        # add idea id
        mturk_dict[IDEA_ID] = hit_dict[IDEA_ID]

    def add_mturk_dict_to_db(self, idea_rank_dict):
        mc.insert_idea_rank(idea_rank_dict)

    def needs_to_post_rank(self):
        return False

    def get_rank_hit_creator(self, mturk_dict):
        return

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        return

    def increment_item_rank(self, mturk_dict):
        mc.increment_idea_rank(mturk_dict[IDEA_ID], mturk_dict[RANK])

    def increment_count(self, rank_idea_hit_id, new_dicts_count):
        mc.increment_rank_idea_hit_count(rank_idea_hit_id, new_dicts_count)


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

    def needs_to_post_rank(self):
        return True

    def get_rank_hit_creator(self, mturk_dict):
        problem_text = mc.get_problem_description(mturk_dict[PROBLEM_ID])
        idea_text = mc.get_idea_dict(mturk_dict[IDEA_ID])[TEXT]
        feedback_text = mc.get_feedback_dict(mturk_dict[FEEDBACK_ID])[TEXT]
        suggestion_text = mturk_dict[TEXT]
        return mturk_controller.RankSuggestionHITCreator(problem_text, idea_text, feedback_text, suggestion_text,
                                                         HOW_MANY_RANKS)

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        suggestion_id = mturk_dict[SUGGESTION_ID]
        mc.insert_new_rank_suggestion_hit(suggestion_id, HOW_MANY_RANKS, rank_item_hit_id)

    def increment_item_rank(self, mturk_dict):
        return

    def increment_count(self, suggestion_hit_id, new_suggestions_count):
        mc.increment_suggestion_hit_count(suggestion_hit_id, new_suggestions_count)


class RankSuggestionHIT(HITObject):

    def get_mturk_dicts(self, hit_id):
        result_getter = mturk_controller.GeneratedRanks()
        return result_getter.get_results(hit_id)

    def get_item_id_from_mturk_dict(self, mturk_dict):
        return mturk_dict[RANK_ID]

    def is_contained(self, suggestion_rank_id):
        return mc.contains_suggestion_rank(suggestion_rank_id)

    def add_useful_fields(self, mturk_dict, hit_dict):
        # add suggestion id
        mturk_dict[SUGGESTION_ID] = hit_dict[SUGGESTION_ID]

    def add_mturk_dict_to_db(self, idea_rank_dict):
        mc.insert_suggestion_rank(idea_rank_dict)

    def needs_to_post_rank(self):
        return False

    def get_rank_hit_creator(self, mturk_dict):
        return

    def save_rank_hit(self, rank_item_hit_id, mturk_dict):
        return

    def increment_item_rank(self, mturk_dict):
        mc.increment_suggestion_rank(mturk_dict[SUGGESTION_ID], mturk_dict[RANK])

    def increment_count(self, rank_suggestion_hit_id, new_dicts_count):
        mc.increment_rank_suggestion_hit_count(rank_suggestion_hit_id, new_dicts_count)
