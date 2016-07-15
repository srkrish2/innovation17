import subprocess
import abc
import os
from constants import *

MTURK_PATH = os.getcwd()+"/mturk/"


class HITCreator:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_jar_args(self):
        return []

    @abc.abstractmethod
    def get_creator_name(self):
        return

    def post(self):
        args = ['java', '-jar', MTURK_PATH+'MTurkSDK.jar']
        args.extend(self.get_jar_args())
        p = subprocess.Popen(args, cwd=MTURK_PATH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # output format:
        #  * "SUCCESS"
        #  * HIT_ID
        #  * URL
        jar_output_file = p.stdout
        first_line = jar_output_file.readline().rstrip()
        if first_line == FAIL:
            print "{}: FAIL".format(self.get_creator_name())
            print jar_output_file.readline().rstrip()
            return FAIL
        if first_line != SUCCESS:
            print "UNEXPECTED! neither fail/success: {}".format(first_line)
            return FAIL
        hit_id = jar_output_file.readline().rstrip()
        url = jar_output_file.readline().rstrip()
        print "url =", url
        return hit_id


class SchemaHITCreator(HITCreator):
    def __init__(self, p, goal):
        self.problem = p
        self.count_goal = goal

    def get_creator_name(self):
        return "SchemaHITCreator"

    def get_jar_args(self):
        return ["PostSchemaHIT", self.problem, str(self.count_goal)]


class InspirationHITCreator(HITCreator):
    def __init__(self, s, goal):
        self.schema = s
        self.count_goal = goal

    def get_creator_name(self):
        return "InspirationHITCreator"

    def get_jar_args(self):
        return ['PostInspirationHIT', self.schema, str(self.count_goal)]


class IdeaHITCreator(HITCreator):
    def __init__(self, prob, src_link, img_link, exp, goal):
        self.problem = prob
        self.source_link = src_link
        self.image_link = img_link
        self.explanation = exp
        self.count_goal = goal

    def get_creator_name(self):
        return "IdeaHITCreator"

    def get_jar_args(self):
        return ['PostIdeaHIT', self.problem, self.source_link, self.image_link, self.explanation,
                str(self.count_goal)]


class SuggestionHITCreator(HITCreator):
    def __init__(self, prob, idea, feed, goal):
        self.problem = prob
        self.idea = idea
        self.feedback = feed
        self.count_goal = goal

    def get_creator_name(self):
        return "SuggestionHITCreator"

    def get_jar_args(self):
        return ['PostSuggestionHIT', self.problem, self.idea, self.feedback, str(self.count_goal)]


class RankSchemaHITCreator(HITCreator):
    def __init__(self, problem, schemas, goal):
        self.problem = problem
        self.schemas = schemas
        self.count_goal = goal

    def get_creator_name(self):
        return "RankSchemaHITCreator"

    def get_jar_args(self):
        args = ['PostRankSchemaHIT', self.problem, str(len(self.schemas))]
        args.extend(self.schemas)
        args.append(str(self.count_goal))
        return args


class RankInspirationHITCreator(HITCreator):
    def __init__(self, schema, i_link, goal):
        self.schema = schema
        self.i_link = i_link
        self.count_goal = goal

    def get_creator_name(self):
        return "RankInspirationHITCreator"

    def get_jar_args(self):
        return ['PostRankInspirationHIT', self.schema, self.i_link, str(self.count_goal)]


class RankIdeaHITCreator(HITCreator):
    def __init__(self, problem, idea, goal):
        self.problem = problem
        self.idea = idea
        self.count_goal = goal

    def get_creator_name(self):
        return "RankIdeaHITCreator"

    def get_jar_args(self):
        return ['PostRankIdeaHIT', self.problem, self.idea, str(self.count_goal)]


class RankSuggestionHITCreator(HITCreator):
    def __init__(self, problem, idea, feedback, suggestions, goal):
        self.problem = problem
        self.idea = idea
        self.feedback = feedback
        self.suggestion1 = suggestions[0]
        self.suggestion2 = suggestions[1]
        self.suggestion3 = suggestions[2]
        self.count_goal = goal

    def get_creator_name(self):
        return "RankSuggestionHITCreator"

    def get_jar_args(self):
        return ['PostRankSuggestionHIT', self.problem, self.idea, self.feedback, self.suggestion1, self.suggestion2,
                self.suggestion3, str(self.count_goal)]

###################################################################
######################## RESULT PULLER ############################
###################################################################


class ResultPuller(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_command_name(self):
        return ""

    @abc.abstractmethod
    def get_data(self, jar_output_file):
        return

    def get_results(self, hit_id):
        args = ['java', '-jar', MTURK_PATH+'MTurkSDK.jar', self.get_command_name(), hit_id]
        p = subprocess.Popen(args, cwd=MTURK_PATH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        jar_output_file = p.stdout
        first_line = jar_output_file.readline().rstrip()
        if first_line == "FAIL":
            print "{}: FAIL".format(self.get_command_name())
            print jar_output_file.readline().rstrip()
            return "FAIL"
        if first_line != "SUCCESS":
            print "UNEXPECTED in {}! neither fail/success: {}".format(self.get_command_name(), first_line)
            print jar_output_file.readline().rstrip()
            return []
        return self.get_data(jar_output_file)


class GeneratedSchemas(ResultPuller):
    def get_command_name(self):
        return "SchemaHITResults"

    def get_data(self, jar_output_file):
        # output format:
        # "SUCCESS"
        # "--[ANSWER START]--"
        #  assignment_id
        #  worker_id
        #  epoch_time_ms
        #  answer
        # "--[ANSWER END]--"
        # "--[END]--"
        schemas = []
        header = jar_output_file.readline().rstrip()
        while True:
            if header == "--[ANSWER START]--":
                assignment_id = jar_output_file.readline().rstrip()
                worker_id = jar_output_file.readline().rstrip()
                epoch_time_ms_string = jar_output_file.readline().rstrip()
                answer_text = ""
                line = jar_output_file.readline().rstrip()
                while line != "--[ANSWER END]--":
                    answer_text += line + '\n'
                    line = jar_output_file.readline().rstrip()
                answer_text = answer_text.rstrip()

                schema = {
                    TEXT: answer_text,
                    TIME_CREATED: epoch_time_ms_string,
                    WORKER_ID: worker_id,
                    SCHEMA_ID: assignment_id
                }
                schemas.append(schema)

                header = jar_output_file.readline().rstrip()
            else:
                break
        return schemas


class GeneratedInspirations(ResultPuller):
    def get_command_name(self):
        return "InspirationHITResults"

    def get_data(self, jar_output_file):
        # output format:
        # "SUCCESS"
        # assignments_count
        #  assignmentId
        #  worker_id
        #  epoch_time_ms
        #     # "--[ANSWER START]--"
        #     #  answer
        #     # "--[ANSWER END]--"
        inspirations = []
        assignment_count = int(jar_output_file.readline().rstrip())
        for i in xrange(assignment_count):
            assignment_id = jar_output_file.readline().rstrip()
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            answers = []
            for j in xrange(4):
                jar_output_file.readline()
                answer_text = ""
                line = jar_output_file.readline().rstrip()
                while line != "--[ANSWER END]--":
                    answer_text += line + '\n'
                    line = jar_output_file.readline().rstrip()
                answer_text = answer_text.rstrip()
                answers.append(answer_text)

            inspiration = {
                INSPIRATION_LINK: answers[0],
                INSPIRATION_ADDITIONAL: answers[1],
                INSPIRATION_SUMMARY: answers[2],
                INSPIRATION_REASON: answers[3],
                TIME_CREATED: epoch_time_ms_string,
                WORKER_ID: worker_id,
                INSPIRATION_ID: assignment_id
            }
            inspirations.append(inspiration)
        return inspirations


class GeneratedIdeas(ResultPuller):
    def get_command_name(self):
        return "IdeaHITResults"

    def get_data(self, jar_output_file):
        # output format:
        # "SUCCESS"
        #  assignments_count
        #  assignmentId
        #  worker_id
        #  epoch_time_ms
        # "--[ANSWER START]--"
        #  answer
        # "--[ANSWER END]--"
        ideas = []
        assignment_count = int(jar_output_file.readline().rstrip())
        for i in xrange(assignment_count):
            assignment_id = jar_output_file.readline().rstrip()
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            answers = []
            for j in xrange(2):
                answer_text = ""
                jar_output_file.readline()
                line = jar_output_file.readline().rstrip()
                while line != "--[ANSWER END]--":
                    answer_text += line + '\n'
                    line = jar_output_file.readline().rstrip()
                answer_text = answer_text.rstrip()
                answers.append(answer_text)
            idea = {
                TEXT: answers[0],
                TITLE: answers[1],
                TIME_CREATED: epoch_time_ms_string,
                WORKER_ID: worker_id,
                IDEA_ID: assignment_id
            }
            ideas.append(idea)
        return ideas


class GeneratedSuggestions(ResultPuller):
    def get_command_name(self):
        return "SuggestionHITResults"

    def get_data(self, jar_output_file):
        # output format:
        # "SUCCESS"
        #  assignments_count
        #  assignmentId
        #  worker_id
        #  epoch_time_ms
        # "--[ANSWER START]--"
        #  answer
        # "--[ANSWER END]--"
        suggestions = []
        assignment_count = int(jar_output_file.readline().rstrip())
        for i in xrange(assignment_count):
            assignment_id = jar_output_file.readline().rstrip()
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            jar_output_file.readline()
            answer_text = ""
            line = jar_output_file.readline().rstrip()
            while line != "--[ANSWER END]--":
                answer_text += line + '\n'
                line = jar_output_file.readline().rstrip()
            answer_text = answer_text.rstrip()

            suggestion = {
                TEXT: answer_text,
                TIME_CREATED: epoch_time_ms_string,
                WORKER_ID: worker_id,
                SUGGESTION_ID: assignment_id
            }
            suggestions.append(suggestion)
        return suggestions


class GeneratedSchemaRanks(ResultPuller):
    def get_command_name(self):
        return "RankSchemaHITResults"

    def get_data(self, jar_output_file):
        # output format:
        #  "SUCCESS"
        #  assignments_num
        #  answers_num
        #  {{answers_num}} ranks
        #  assignment_id
        #  worker_id
        #  epoch_time_ms
        assignments_num = int(jar_output_file.readline().rstrip())
        rank_dicts = []
        if assignments_num == 0:
            return rank_dicts
        needs_restart = True
        for i in xrange(assignments_num):
            answers_num = int(jar_output_file.readline().rstrip())
            if answers_num == 0:
                continue
            needs_restart = False
            ranks = []
            for j in xrange(answers_num):
                ranks.append(int(jar_output_file.readline().rstrip()))
            assignment_id = jar_output_file.readline().rstrip()
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            rank_dict = {
                RANKS_FIELD: ranks,
                TIME_CREATED: epoch_time_ms_string,
                WORKER_ID: worker_id,
                RANK_ID: assignment_id
            }
            rank_dicts.append(rank_dict)
        if needs_restart:
            return RESTART
        return rank_dicts


class GeneratedInspirationRanks(ResultPuller):
    def get_command_name(self):
        return "RankInspirationHITResults"

    def get_data(self, jar_output_file):
        # output format:
        #  "SUCCESS" -- already processed
        #  assignments_num
        #  answers
        #  assignment_id
        #  worker_id
        #  epoch_time_ms
        assignments_num = int(jar_output_file.readline().rstrip())
        rank_dicts = []
        for i in xrange(assignments_num):
            rank = int(jar_output_file.readline().rstrip())
            explanation = jar_output_file.readline().rstrip()
            assignment_id = jar_output_file.readline().rstrip()
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            rank_dict = {
                RANK: rank,
                TIME_CREATED: epoch_time_ms_string,
                WORKER_ID: worker_id,
                RANK_ID: assignment_id
            }
            rank_dicts.append(rank_dict)
        return rank_dicts