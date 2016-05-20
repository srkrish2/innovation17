import datetime
import subprocess
import mongodb_controller


def create_schema_making_hit(problem):
    print "problem description: ", problem
    # run the jarred java file for submitting mturk task, passing problem as args[0]
    p = subprocess.Popen(['java', '-jar', 'SchemaMaking.jar', problem],
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
        print "UNEXPECTED! neither fail/success"
        return "FAIL"

    print "SchemaMaking.jar first line:", first_line

    hit_id = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()

    print "hit_id =", hit_id
    print "url =", url

    return hit_id


def get_schema_making_status(hit_id):
    p = subprocess.Popen(['java', '-jar', 'SchemaMakingStatus.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # submitted_assignments_count if success
    # else:
    # FAIL
    # localizedMessage
    jar_output_file = p.stdout
    submitted_assignments_count = jar_output_file.readline().rstrip()
    if submitted_assignments_count == "FAIL":
        print "SchemaMakingStatus - FAIL"
        print "message:", jar_output_file.readline().rstrip()
        return 0
    print "get_schema_making_status:", "count =", submitted_assignments_count
    return submitted_assignments_count


def get_schema_making_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'SchemaMakingResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    # "--[ANSWER START]--"
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
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            answer_text = ""
            line = jar_output_file.readline().rstrip()
            while line != "--[ANSWER END]--":
                answer_text += line + '\n'
                line = jar_output_file.readline().rstrip()
            print "ANSWER:", answer_text

            schema = {
                mongodb_controller.SCHEMA_HIT_ID: hit_id,
                mongodb_controller.SCHEMA_TEXT: answer_text,
                mongodb_controller.SCHEMA_TIME: epoch_time_ms_string,
                mongodb_controller.SCHEMA_WORKER_ID: worker_id
            }
            schemas.append(schema)

            header = jar_output_file.readline().rstrip()
        else:
            break
    return schemas

"""
def get_schema_ranking_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'SchemaMakingResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    # "--[ANSWER START]--"
    #  worker_id
    #  epoch_time_ms
    #  answer: GOOD or BAD
    # "--[ANSWER END]--"
    # "--[END]--"

    jar_output_file = p.stdout
    if jar_output_file.readline().rstrip() == "FAIL":
        print "SchemaRankingResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        return "FAIL"

    ranks = []
    header = jar_output_file.readline().rstrip()
    while True:
        if header == "--[ANSWER START]--":
            worker_id = jar_output_file.readline().rstrip()
            epoch_time_ms_string = jar_output_file.readline().rstrip()
            rank = jar_output_file.readline().rstrip()

            print "RANK:", rank

            rank = {

            }
            ranks.append(rank)

            header = jar_output_file.readline().rstrip()
        else:
            break
    return ranks
"""