import datetime
import subprocess


def process_problem(problem):
    """
    Processes the problem submission and returns a message for front end
    :return: if success, time when the results will be ready
    """
    print "problem description: ", problem
    # run the jarred java file for submitting mturk task, passing problem as args[0]
    p = subprocess.Popen(['java', '-jar', 'SchemaMaking.jar', problem],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    #  * "SUCCESS"
    #  * HIT_ID
    #  * DURATION (in seconds)
    #  * URL

    jar_output_file = p.stdout
    first_line = jar_output_file.readline().rstrip()
    if first_line == "FAIL":
        print "SchemaMaking.jar: FAIL"
        print jar_output_file.readline().rstrip()
        # TODO: decide what todo
        return "FAIL"
    if first_line != "SUCCESS":
        print "UNEXPECTED! neither fail/success"
        return "FAIL"

    print "SchemaMaking.jar first line:", first_line

    hit_id = jar_output_file.readline().rstrip()
    duration = jar_output_file.readline().rstrip()
    url = jar_output_file.readline().rstrip()

    print "hit_id =", hit_id
    print "duration =", duration
    print "url =", url

    # get finish time
    current_time = datetime.datetime.now()
    finish_time = current_time + datetime.timedelta(0, int(duration))
    return [hit_id, finish_time]


def get_hit_results(hit_id):
    p = subprocess.Popen(['java', '-jar', 'SchemaMakingResults.jar', hit_id],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # output format:
    # "SUCCESS"
    # "--[ANSWER START]--"
    #  answer
    # "--[ANSWER END]--"
    # "--[END]--"

    jar_output_file = p.stdout
    if jar_output_file.readline().rstrip() == "FAIL":
        print "SchemaMakingResults.jar: FAIL"
        print jar_output_file.readline().rstrip()
        # TODO: decide what todo
        return "FAIL"

    answers = []
    header = jar_output_file.readline().rstrip()
    while True:
        if header == "--[ANSWER START]--":
            line = jar_output_file.readline().rstrip()
            answer = ""
            while line != "--[ANSWER END]--":
                answer += line
                line = jar_output_file.readline().rstrip()
            print "ANSWER:", answer
            answers.append(answer)
            header = jar_output_file.readline().rstrip()
        else:
            break
    # TODO: what to do with answers
    return '////////n'.join(answers)
