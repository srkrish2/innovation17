import subprocess
import mongodb_controller
import abc


class HITCreator:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_popen_args_arr(self):
        return

    @abc.abstractmethod
    def get_creator_name(self):
        return

    def post(self):
        args_arr = self.get_popen_args_arr()
        p = subprocess.Popen(args_arr, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # output format:
        #  * "SUCCESS"
        #  * HIT_ID
        #  * URL
        jar_output_file = p.stdout
        first_line = jar_output_file.readline().rstrip()
        if first_line == "FAIL":
            print "{}: FAIL".format(self.get_creator_name())
            print jar_output_file.readline().rstrip()
            return "FAIL"
        if first_line != "SUCCESS":
            print "UNEXPECTED! neither fail/success: {}".format(first_line)
            return "FAIL"
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

    def get_popen_args_arr(self):
        return ['java', '-jar', 'SchemaMaking.jar', self.problem, str(self.count_goal)]


class InspirationHITCreator(HITCreator):
    def __init__(self, s, goal):
        self.schema = s
        self.count_goal = goal

    def get_creator_name(self):
        return "InspirationHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostInspirationHIT.jar', self.schema, str(self.count_goal)]


class IdeaHITCreator(HITCreator):
    def __init__(self, prob, src_link, img_link, exp, goal):
        self.problem = prob
        self.source_link = src_link
        self.image_link = img_link
        self.explanation = exp
        self.count_goal = goal

    def get_creator_name(self):
        return "IdeaHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostIdeaHIT.jar', self.problem, self.source_link, self.image_link, self.explanation,
                str(self.count_goal)]


class SuggestionHITCreator(HITCreator):
    def __init__(self, prob, idea, feed, goal):
        self.problem = prob
        self.idea = idea
        self.feedback = feed
        self.count_goal = goal

    def get_creator_name(self):
        return "SuggestionHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostSuggestionHIT.jar', self.problem, self.idea, self.feedback, str(self.count_goal)]


class RankSchemaHITCreator(HITCreator):
    def __init__(self, schema, goal):
        self.schema = schema
        self.count_goal = goal

    def get_creator_name(self):
        return "RankSchemaHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostRankSchemaHIT.jar', self.schema, str(self.count_goal)]


class RankInspirationHITCreator(HITCreator):
    def __init__(self, problem, schema, i_link, i_add, i_reas, goal):
        self.problem = problem
        self.schema = schema
        self.i_link = i_link
        self.i_additional = i_add
        self.i_reason = i_reas
        self.count_goal = goal

    def get_creator_name(self):
        return "RankInspirationHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostRankInspirationHIT.jar', self.problem, self.schema, self.i_link,
                self.i_additional, self.i_reason, str(self.count_goal)]


class RankIdeaHITCreator(HITCreator):
    def __init__(self, problem, idea, goal):
        self.problem = problem
        self.idea = idea
        self.count_goal = goal

    def get_creator_name(self):
        return "RankIdeaHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostRankIdeaHIT.jar', self.problem, self.idea, str(self.count_goal)]


class RankSuggestionHITCreator(HITCreator):
    def __init__(self, problem, idea, feedback, suggestion, goal):
        self.problem = problem
        self.idea = idea
        self.feedback = feedback
        self.suggestion = suggestion
        self.count_goal = goal

    def get_creator_name(self):
        return "RankSuggestionHITCreator"

    def get_popen_args_arr(self):
        return ['java', '-jar', 'PostRankSuggestionHIT.jar', self.problem, self.idea, self.feedback, self.suggestion,
                str(self.count_goal)]


def get_schema_making_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'SchemaMakingResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    # "--[ANSWER START]--"
    #  assignment_id
    #  worker_id
    #  epoch_time_ms
    #  answer
    # "--[ANSWER END]--"
    # "--[END]--"

    jar_output_file = p.stdout
    if jar_output_file.readline().rstrip() == "FAIL":
        print "SchemaMakingResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"

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
                mongodb_controller.TEXT: answer_text,
                mongodb_controller.TIME_CREATED: epoch_time_ms_string,
                mongodb_controller.WORKER_ID: worker_id,
                mongodb_controller.SCHEMA_ID: assignment_id
            }
            schemas.append(schema)

            header = jar_output_file.readline().rstrip()
        else:
            break
    return schemas


def get_inspiration_hit_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'InspirationHITResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    # assignments_count
    #  assignmentId
    #  worker_id
    #  epoch_time_ms
    #     # "--[ANSWER START]--"
    #     #  answer
    #     # "--[ANSWER END]--"

    jar_output_file = p.stdout
    if jar_output_file.readline().rstrip() == "FAIL":
        print "InspirationHITResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"

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
            mongodb_controller.INSPIRATION_LINK: answers[0],
            mongodb_controller.INSPIRATION_ADDITIONAL: answers[1],
            mongodb_controller.INSPIRATION_SUMMARY: answers[2],
            mongodb_controller.INSPIRATION_REASON: answers[3],
            mongodb_controller.TIME_CREATED: epoch_time_ms_string,
            mongodb_controller.WORKER_ID: worker_id,
            mongodb_controller.INSPIRATION_ID: assignment_id
        }
        inspirations.append(inspiration)
    return inspirations


def get_idea_hit_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'IdeaHITResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    #  assignments_count
    #  assignmentId
    #  worker_id
    #  epoch_time_ms
    # "--[ANSWER START]--"
    #  answer
    # "--[ANSWER END]--"

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "IdeaHITResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "neither success nor fail: {}".format(first_line)

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
            mongodb_controller.TEXT: answers[0],
            mongodb_controller.TITLE: answers[1],
            mongodb_controller.TIME_CREATED: epoch_time_ms_string,
            mongodb_controller.WORKER_ID: worker_id,
            mongodb_controller.IDEA_ID: assignment_id
        }
        ideas.append(idea)
    return ideas


def get_suggestion_hit_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'SuggestionHITResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    #  assignments_count
    #  assignmentId
    #  worker_id
    #  epoch_time_ms
    # "--[ANSWER START]--"
    #  answer
    # "--[ANSWER END]--"

    jar_output_file = p.stdout
    if jar_output_file.readline().rstrip() == "FAIL":
        print "SuggestionHITResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"

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
            mongodb_controller.TEXT: answer_text,
            mongodb_controller.TIME_CREATED: epoch_time_ms_string,
            mongodb_controller.WORKER_ID: worker_id,
            mongodb_controller.SUGGESTION_ID: assignment_id
        }
        suggestions.append(suggestion)
    return suggestions


def get_ranking_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'RankSchemaHITResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  "SUCCESS"
    #  how_many
    #  assignment_id
    #  worker_id
    #  epoch_time_ms
    #  answer: GOOD or BAD

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "RankSchemaHITResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        return "FAIL"
    how_many = int(jar_output_file.readline().rstrip())
    ranks = []
    for i in xrange(how_many):
        assignment_id = jar_output_file.readline().rstrip()
        worker_id = jar_output_file.readline().rstrip()
        epoch_time_ms_string = jar_output_file.readline().rstrip()
        rank = int(jar_output_file.readline().rstrip())
        rank_dict = {
            mongodb_controller.RANK: rank,
            mongodb_controller.TIME_CREATED: epoch_time_ms_string,
            mongodb_controller.WORKER_ID: worker_id,
            mongodb_controller.RANK_ID: assignment_id
        }
        ranks.append(rank_dict)
    return ranks
