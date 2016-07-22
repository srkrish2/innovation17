import mongodb_controller as mc
import mturk_controller
from constants import *
from multiprocessing.pool import ThreadPool
import waiters
from utility_functions import generate_id, get_input_problem_dict, check_if_logged_in


def launch_schema_hit(problem_id, description, assignments_num):
    schema_hit_creator = mturk_controller.SchemaHITCreator(description, assignments_num)
    hit_id = schema_hit_creator.post()
    if hit_id == "FAIL":
        print "launch_schema_hit: FAIL!!"
        return
    mc.insert_new_schema_hit(problem_id, assignments_num, hit_id)


def post_inspiration_task(problem_id, count_goal):
    for schema in mc.get_schemas_for_inspiration_task(problem_id):
        inspiration_hit_creator = mturk_controller.InspirationHITCreator(schema[TEXT], count_goal)
        hit_id = inspiration_hit_creator.post()
        if hit_id == "FAIL":
            print "post_inspiration_task: FAIL!"
            continue
        schema_id = schema[SCHEMA_ID]
        mc.insert_new_inspiration_hit(problem_id, schema_id, count_goal, hit_id)
        mc.set_schema_processed_status(schema_id)


def post_idea_task(problem_id, count_goal):
    for inspiration in mc.get_inspirations_for_idea_task(problem_id):
        problem_description = mc.get_problem_description(inspiration[PROBLEM_ID])
        source_link = inspiration[INSPIRATION_LINK]
        explanation = inspiration[INSPIRATION_REASON]
        idea_hit_creator =\
            mturk_controller.IdeaHITCreator(problem_description, source_link, explanation, count_goal)
        hit_id = idea_hit_creator.post()
        # add the hit_id to schema
        if hit_id == "FAIL":
            print "post_idea_task: FAIL!"
            continue
        inspiration_id = inspiration[INSPIRATION_ID]
        schema_id = inspiration[SCHEMA_ID]
        mc.insert_new_idea_hit(problem_id, schema_id, inspiration_id, count_goal, hit_id)
        mc.set_inspiration_processed_status(inspiration_id)


def post_feedback(idea_dict, idea_id, feedbacks, count_goal):
    problem_id = idea_dict[PROBLEM_ID]
    problem_text = mc.get_problem_description(problem_id)
    idea_text = idea_dict[TEXT]
    for feedback in feedbacks:
        suggestion_hit_creator = mturk_controller.SuggestionHITCreator(problem_text, idea_text, feedback, count_goal)
        hit_id = suggestion_hit_creator.post()
        if hit_id == "FAIL":
            print "post_feedback: FAIL!"
            continue
        feedback_id = generate_id()
        mc.add_feedback(feedback_id, feedback, idea_id)
        mc.insert_new_suggestion_hit(problem_id, idea_id, feedback_id, count_goal, hit_id)
    mc.idea_launched(idea_id)


def publish_problem(problem_id):
    problem_dict = mc.get_problem_dict(problem_id)
    description = problem_dict[DESCRIPTION]
    schema_assignments_num = problem_dict[SCHEMA_ASSIGNMENTS_NUM]
    mc.set_schema_stage(problem_id)
    launch_schema_hit(problem_id, description, schema_assignments_num)


def start_lazy_problem(description, how_many_to_post, problem_id):
    launch_schema_hit(problem_id, description, how_many_to_post)

    pool = ThreadPool(processes=1)

    schema_stage_waiter = waiters.SchemaStageWaiter(pool, problem_id)
    done = schema_stage_waiter.wait_until_done()
    print "schema stage done!"

    mc.set_inspiration_stage(problem_id)
    post_inspiration_task(problem_id, HOW_MANY_INSPIRATIONS)

    inspiration_stage_waiter = waiters.InspirationStageWaiter(pool, problem_id)
    done = inspiration_stage_waiter.wait_until_done()
    print "inspiration stage done!"

    mc.set_idea_stage(problem_id)
    post_idea_task(problem_id, HOW_MANY_IDEAS)

    idea_stage_waiter = waiters.IdeaStageWaiter(pool, problem_id)
    done = idea_stage_waiter.wait_until_done()
    print "idea stage done!"


def relaunch_schema_task(problem_id, assignments_num):
    description = mc.get_problem_description(problem_id)
    launch_schema_hit(problem_id, description, assignments_num)


def save_problem(for_submit=False):
    username = check_if_logged_in()
    input_problem_dict = get_input_problem_dict()
    lazy = input_problem_dict[LAZY]
    schema_assignments_num = input_problem_dict[SCHEMA_ASSIGNMENTS_NUM]
    if not lazy and schema_assignments_num == -1:
        return {"success": False}
    if lazy:
        input_problem_dict[SCHEMA_ASSIGNMENTS_NUM] = HOW_MANY_SCHEMAS
    problem_id = input_problem_dict[PROBLEM_ID]
    if problem_id is None:  # new problem
        input_problem_dict[PROBLEM_ID] = generate_id()
        mc.insert_problem(input_problem_dict)
    else:
        mc.does_user_have_problem_with_id(username, problem_id)
        mc.edit_problem(input_problem_dict)
    result = {
        "success": True,
        "url": "problems"
    }
    if for_submit:
        result["input_problem_dict"] = input_problem_dict
    return result
