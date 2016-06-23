import subprocess
import mongodb_controller


def create_schema_making_hit(problem, schema_count_goal):
    # run the jarred java file for submitting mturk task, passing problem as args[0]
    p = subprocess.Popen(['java', '-jar', 'SchemaMaking.jar', problem, str(schema_count_goal)],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  * "SUCCESS"
    #  * HIT_ID
    #  * URL

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "SchemaMaking.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        return "FAIL"

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()

    print "url =", url

    return hit_id


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


def create_inspiration_hit(schema, count_goal):
    # run the jarred java file for submitting mturk task, passing problem as args[0]
    p = subprocess.Popen(['java', '-jar', 'PostInspirationHIT.jar', schema, str(count_goal)],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  * "SUCCESS"
    #  * HIT_ID
    #  * URL

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "PostInspirationHIT.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        return "FAIL"

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()

    print "url =", url

    return hit_id


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


def create_idea_hit(problem, source_link, image_link, explanation, assignments_num):
    # run the jarred java file for submitting mturk task, passing problem as args[0]
    p = subprocess.Popen(['java', '-jar', 'PostIdeaHIT.jar', problem, source_link, image_link, explanation,
                          str(assignments_num)],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  * "SUCCESS"
    #  * HIT_ID
    #  * URL

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "PostIdeaHIT.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        print jar_output_file.readline().rstrip()
        return "FAIL"

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()

    print "url =", url

    return hit_id


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


def create_suggestion_hit(problem, idea, feedback, assignments_num):
    # run the jarred java file for submitting mturk task, passing problem as args[0]
    p = subprocess.Popen(['java', '-jar', 'PostSuggestionHIT.jar', problem, idea, feedback, str(assignments_num)],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  * "SUCCESS"
    #  * HIT_ID
    #  * URL

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "PostSuggestionHIT.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        return "FAIL"

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()

    print "url =", url

    return hit_id


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


def create_rank_schema_hit(schema, assignment_num):
    p = subprocess.Popen(['java', '-jar', 'PostRankSchemaHIT.jar', schema, str(assignment_num)],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  * "SUCCESS"
    #  * HIT_ID
    #  * URL

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "PostRankSchemaHIT.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        return "FAIL"

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()
    print "url =", url
    return hit_id


def create_rank_inspiration_hit(problem, schema, i_link, i_additional, i_reason, assignment_num):
    p = subprocess.Popen(['java', '-jar', 'PostRankInspirationHIT.jar', problem, schema, i_link, i_additional,
                         i_reason, str(assignment_num)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "PostRankInspirationHIT.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success: {}".format(first_line)
        return "FAIL"

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()
    print "url =", url
    return hit_id


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
