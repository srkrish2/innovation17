"""
Cherrypy server. Used to start the webpage, get input over Rest API,
send it to MTurk runnable. We are not dealing with MTurk in Python
since MTurk's Java SDK is more recommendable/documented/exemplified.
We are not using Java for server since Python is less painful.

To run, enter "python server.py" in terminal.
"""

import os
import cherrypy
import random
import string
import mturk_controller
import mongodb_controller
import datetime
from threading import Thread
import time

from jinja2 import Environment, PackageLoader
# import passlib.hash
env = Environment(loader=PackageLoader('server', '/templates'))
# sha256_crypt = passlib.hash.sha256_crypt


PROBLEM_ID = "problem_id"
# format example: 23 Apr 2012 4:00 PM
READABLE_TIME_FORMAT = "%d %b %Y %I:%M %p"
PREVIOUS_URL_KEY = "previous_url"
USERNAME_KEY = "username"


@cherrypy.popargs('problem_slug')
class HtmlPageLoader(object):

    @cherrypy.expose
    def index(self):
        return render_homepage()

    @cherrypy.expose
    def home(self):
        return render_homepage()

    @cherrypy.expose
    def problems(self):
        return render_problems_page()

    @cherrypy.expose
    def edit(self, problem_slug):
        return render_edit_page(problem_slug)

    @cherrypy.expose
    def view(self, problem_slug):
        return render_view_page(problem_slug)

    @cherrypy.expose
    def schemas(self, problem_slug):
        return render_schemas_page(problem_slug)

    @cherrypy.expose
    def inspirations(self, problem_slug):
        return render_inspirations_page(problem_slug)

    @cherrypy.expose
    def ideas(self, problem_slug):
        return render_ideas_page(problem_slug)

    @cherrypy.expose
    def log_out(self):
        cherrypy.session.pop(USERNAME_KEY)
        return render_homepage()

    @cherrypy.expose
    def sign_in(self):
        return open("sign_in.html")

    @cherrypy.expose
    def register(self):
        return open("register.html")

    @cherrypy.expose
    def new_problem(self):
        return render_new_problem()

    @cherrypy.expose
    def account_edit(self):
        return render_account_edit_page()

    @cherrypy.expose
    def profile_info(self):
        return render_profile()

    @cherrypy.expose
    def suggestions(self, problem_slug):
        return render_suggestions_page(problem_slug)


###############################################################################
############################RENDERING FUNCTIONS################################
###############################################################################

def render_homepage():
    if USERNAME_KEY in cherrypy.session:
        template = env.get_template('home.html')
        return template.render()
    else:
        raise cherrypy.HTTPRedirect("sign_in")


def render_problems_page():
    if USERNAME_KEY not in cherrypy.session:
        cherrypy.session[PREVIOUS_URL_KEY] = "problems"
        raise cherrypy.HTTPRedirect("sign_in")
    problems = mongodb_controller.get_problems_by_user(cherrypy.session[USERNAME_KEY])
    template = env.get_template('problems.html')
    return template.render(problems=problems)


def render_schemas_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        schemas = mongodb_controller.get_schemas_for_problem(problem_id)
        template = env.get_template('schemas.html')
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        print schemas
        return template.render(schemas=schemas, problem_id=problem_id,
                               problem_stage=mongodb_controller.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_inspirations_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        inspirations = mongodb_controller.get_inspirations(problem_id)
        template = env.get_template('inspirations_card.html')
        inspiration_dicts_list = []
        for inspiration in inspirations:
            problem_text = mongodb_controller.get_problem_description(problem_id)
            schema_text = mongodb_controller.get_schema_text(inspiration[mongodb_controller.SCHEMA_ID])
            inspiration["problem_text"] = problem_text
            inspiration["schema_text"] = schema_text
            inspiration_dicts_list.append(inspiration)
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        return template.render(inspirations=inspiration_dicts_list, problem_id=problem_id,
                               problem_stage=mongodb_controller.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_ideas_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        ideas = mongodb_controller.get_ideas(problem_id)
        template = env.get_template('ideas.html')
        ideas_dicts_list = []
        for idea in ideas:
            problem_text = mongodb_controller.get_problem_description(problem_id)
            inspiration_id = idea[mongodb_controller.INSPIRATION_ID]
            schema_text = mongodb_controller.get_schema_text_from_inspiration(inspiration_id)
            inspiration_summary = mongodb_controller.get_inspiration_summary(inspiration_id)
            idea["problem_text"] = problem_text
            idea["schema_text"] = schema_text
            idea["inspiration_text"] = inspiration_summary
            ideas_dicts_list.append(idea)
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        return template.render(ideas=ideas_dicts_list, problem_id=problem_id,
                               problem_stage=mongodb_controller.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_edit_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        [title, description, count_goal] = mongodb_controller.get_problem_fields(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=count_goal, problem_id=problem_id, title=title,
                               operation="edit", description=description)


def render_view_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        [title, description, count_goal] = mongodb_controller.get_problem_fields(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=count_goal, problem_id=problem_id, title=title,
                               operation="view", description=description)


def render_suggestions_page(idea_slug):
    suggestions = []
    for suggestion in mongodb_controller.get_suggestions(idea_slug):
        suggestions.append(suggestion)
    idea_text = mongodb_controller.get_idea_text(idea_slug)
    return str(suggestions), idea_text
    # template = env.get_template('suggestions.html')
    # return template.render(suggestions=suggestions, idea_text=idea_text)


def render_new_problem():
    template = env.get_template('new_problem.html')
    return template.render()


def render_account_edit_page():
    template = env.get_template('account_edit.html')
    return template.render()


def render_profile():
    template = env.get_template('profile_info.html')
    return template.render()


def error_page_404(status, message, traceback, version):
    # if message is not None:
    #     return "404 Page not found! Message: {}".format(message)
    return "404 Page not found!"


def error_page_403(status, message, traceback, version):
    return "403 Forbidden! Message: {}".format(message)


def unanticipated_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        "<html><body>Sorry, an error occurred. Please contact the admin</body></html>"
    ]

###############################################################################
################################UTILITY FUNCTIONS##############################
###############################################################################


def check_problem_access(problem_slug):
    if USERNAME_KEY in cherrypy.session:
        username = cherrypy.session[USERNAME_KEY]
        if mongodb_controller.does_user_have_problem(username, problem_slug):
            return True
        else:
            raise cherrypy.HTTPError(404, "You, {}, aren't allowed here".format(username))
    else:
        cherrypy.session[PREVIOUS_URL_KEY] = "problems"
        raise cherrypy.HTTPRedirect("/sign_in")


def get_problem_parameters():
    if USERNAME_KEY not in cherrypy.session:
        raise cherrypy.HTTPError(403)
    owner_username = cherrypy.session[USERNAME_KEY]
    data = cherrypy.request.json
    title = data["title"]
    description = data["description"]
    schema_count_goal = convert_input_count(data["schema_count_goal"])

    return owner_username, title, description, schema_count_goal


def convert_input_count(user_input):
    if not isinstance(user_input, int):
        try:
            schema_count_goal = int(user_input)
        except ValueError:
            print "Casting fail!!!"
            schema_count_goal = -1
    return schema_count_goal


def make_links_list(slug, problem_id):
    schemas_page_link = "/{}/schemas".format(slug)
    inspirations_page_link = "/{}/inspirations".format(slug)
    ideas_page_link = "/{}/ideas".format(slug)
    stage = mongodb_controller.get_stage(problem_id)
    if stage != mongodb_controller.STAGE_IDEA:
        ideas_page_link = ""
    elif stage != mongodb_controller.STAGE_INSPIRATION:
        inspirations_page_link = ""
    return schemas_page_link, inspirations_page_link, ideas_page_link

###############################################################################
##################################AJAX HANDLERS################################
###############################################################################


class SaveNewProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        [owner_username, title, description, schema_count_goal] = get_problem_parameters()
        if schema_count_goal == -1:
            return {"success": False}
        problem_id = ''.join(random.sample(string.hexdigits, 8))
        time_created = datetime.datetime.now().strftime(READABLE_TIME_FORMAT)
        mongodb_controller.save_problem(problem_id, title, description, owner_username, schema_count_goal, time_created)
        return {
            "success": True,
            "url": "problems"
        }


class PostNewProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        [owner_username, title, description, schema_count_goal] = get_problem_parameters()
        if schema_count_goal == -1:
            return {"success": False}

        problem_id = ''.join(random.sample(string.hexdigits, 8))
        time_created = datetime.datetime.now().strftime(READABLE_TIME_FORMAT)
        mongodb_controller.save_problem(problem_id, title, description, owner_username, schema_count_goal, time_created)

        hit_id = mturk_controller.create_schema_making_hit(description, schema_count_goal)
        if hit_id == "FAIL":
            return {"success": False}
        mongodb_controller.set_schema_stage(problem_id)
        mongodb_controller.insert_new_schema_hit(problem_id, schema_count_goal, hit_id)
        return {
            "success": True,
            "url": "problems"
        }


def publish_problem(problem_id):
    [title, description, schema_count_goal] = mongodb_controller.get_problem_fields(problem_id)
    hit_id = mturk_controller.create_schema_making_hit(description, schema_count_goal)
    if hit_id == "FAIL":
        return {"success": False}
    mongodb_controller.set_schema_stage(problem_id)
    mongodb_controller.insert_new_schema_hit(problem_id, schema_count_goal, hit_id)
    return {"success": True}


class PublishProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        return publish_problem(data[PROBLEM_ID])

###############################################################################

def pull_schema_hit_results(schema_hit):
    schema_hit_id = schema_hit[mongodb_controller.HIT_ID]
    problem_id = schema_hit[mongodb_controller.PROBLEM_ID]
    schema_dicts = mturk_controller.get_schema_making_results(schema_hit_id)
    if schema_dicts == "FAIL":
        print "mturk_controller.update_schemas_for_problem - FAIL!"
        return
    new_schemas_count = 0
    # replace time with a readable one and add to DB
    for schema_dict in schema_dicts:
        schema_id = schema_dict[mongodb_controller.SCHEMA_ID]
        if mongodb_controller.contains_schema(schema_id):
            print "schema is contained already"
            continue

        # pop epoch time
        epoch_time_ms = long(schema_dict.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        schema_dict[mongodb_controller.TIME_CREATED] = readable_time
        # add problem_id and status
        schema_dict[mongodb_controller.STATUS] = mongodb_controller.STATUS_ACCEPTED
        schema_dict[mongodb_controller.PROBLEM_ID] = problem_id
        mongodb_controller.add_schema(schema_dict)
        new_schemas_count += 1
    mongodb_controller.increment_schema_hit_count(schema_hit_id, new_schemas_count)
    return new_schemas_count


def update_schemas_for_problem(problem_id):
    new_schemas_count = 0
    for schema_hit in mongodb_controller.get_schema_hits(problem_id):
        if schema_hit[mongodb_controller.COUNT] != schema_hit[mongodb_controller.COUNT_GOAL]:
            new_schemas_count += pull_schema_hit_results(schema_hit)
    mongodb_controller.increment_schema_count(problem_id, new_schemas_count)

###############################################################################

def pull_inspiration_hit_results(inspiration_hit):
    inspiration_hit_id = inspiration_hit[mongodb_controller.HIT_ID]
    schema_id = inspiration_hit[mongodb_controller.SCHEMA_ID]
    problem_id = inspiration_hit[mongodb_controller.PROBLEM_ID]
    inspirations = mturk_controller.get_inspiration_hit_results(inspiration_hit_id)
    if inspirations == "FAIL":
        print "mturk_controller.get_inspiration_hit_results - FAIL!"
        return
    new_inspirations_count = 0
    for inspiration in inspirations:
        inspiration_id = inspiration[mongodb_controller.INSPIRATION_ID]
        if mongodb_controller.contains_inspiration(inspiration_id):
            continue
        # replace time with a readable one
        epoch_time_ms = long(inspiration.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        inspiration[mongodb_controller.TIME_CREATED] = readable_time
        # add problem id, schema id, and status
        inspiration[mongodb_controller.PROBLEM_ID] = problem_id
        inspiration[mongodb_controller.SCHEMA_ID] = schema_id
        inspiration[mongodb_controller.STATUS] = mongodb_controller.STATUS_ACCEPTED
        mongodb_controller.add_inspiration(inspiration)
        new_inspirations_count += 1
    mongodb_controller.increment_inspiration_hit_count(inspiration_hit_id, new_inspirations_count)
    return new_inspirations_count


def update_inspirations_for_problem(problem_id):
    new_inspirations_count = 0
    for inspiration_hit in mongodb_controller.get_inspiration_hits(problem_id):
        if inspiration_hit[mongodb_controller.COUNT] != inspiration_hit[mongodb_controller.COUNT_GOAL]:
            new_inspirations_count += pull_inspiration_hit_results(inspiration_hit)
    mongodb_controller.increment_inspiration_count(problem_id, new_inspirations_count)

###############################################################################

def pull_idea_hit_results(idea_hit):
    idea_hit_id = idea_hit[mongodb_controller.HIT_ID]
    schema_id = idea_hit[mongodb_controller.SCHEMA_ID]
    inspiration_id = idea_hit[mongodb_controller.INSPIRATION_ID]
    problem_id = idea_hit[mongodb_controller.PROBLEM_ID]

    ideas = mturk_controller.get_idea_hit_results(idea_hit_id)
    new_ideas_count = 0
    for idea in ideas:
        idea_id = idea[mongodb_controller.IDEA_ID]
        if mongodb_controller.contains_idea(idea_id):
            continue
        # replace time with a readable one
        epoch_time_ms = long(idea.pop(mongodb_controller.TIME_CREATED))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        idea[mongodb_controller.TIME_CREATED] = readable_time
        # add problem id, schema id, inspiration_id, and status
        idea[mongodb_controller.PROBLEM_ID] = problem_id
        idea[mongodb_controller.SCHEMA_ID] = schema_id
        idea[mongodb_controller.INSPIRATION_ID] = inspiration_id
        idea[mongodb_controller.STATUS] = mongodb_controller.STATUS_ACCEPTED
        mongodb_controller.add_idea(idea)
        new_ideas_count += 1
    mongodb_controller.increment_inspiration_hit_count(idea_hit_id, new_ideas_count)
    return new_ideas_count


def update_ideas_for_problem(problem_id):
    new_ideas_count = 0
    for idea_hit in mongodb_controller.get_idea_hits(problem_id):
        if idea_hit[mongodb_controller.COUNT] != idea_hit[mongodb_controller.COUNT_GOAL]:
            new_ideas_count += pull_idea_hit_results(idea_hit)
    mongodb_controller.increment_idea_count(problem_id, new_ideas_count)

###############################################################################

def update_hit_results(username):
    start = time.clock()
    for problem_id in mongodb_controller.get_users_problem_ids(username):
        if not mongodb_controller.did_reach_schema_count_goal(problem_id):
            update_schemas_for_problem(problem_id)
        if not mongodb_controller.did_reach_inspiration_count_goal(problem_id):
            update_inspirations_for_problem(problem_id)
        if not mongodb_controller.did_reach_idea_count_goal(problem_id):
            update_ideas_for_problem(problem_id)
    elapsed = time.clock()
    elapsed = elapsed - start
    # print "Done updating! Time spent:", elapsed*1000


class CountUpdatesHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    def GET(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        username = cherrypy.session[USERNAME_KEY]
        thread = Thread(target=update_hit_results, args=[username])
        thread.start()
        return mongodb_controller.get_counts_for_user(username)


def relaunch_schema_task(problem_id, assignments_num):
    problem_fields = mongodb_controller.get_problem_fields(problem_id)
    description = problem_fields[mongodb_controller.DESCRIPTION]
    hit_id = mturk_controller.create_schema_making_hit(description, assignments_num)
    if hit_id == "FAIL":
        return {"success": False}
    mongodb_controller.insert_new_schema_hit(problem_id, assignments_num, hit_id)
    mongodb_controller.increment_schema_count_goal(problem_id, assignments_num)
    return {"success": True}


class InspirationTaskHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        owner_username = cherrypy.session[USERNAME_KEY]
        data = cherrypy.request.json
        problem_id = data['problem_id']
        if not mongodb_controller.does_user_have_problem_with_id(owner_username, problem_id):
            raise cherrypy.HTTPError(403)
        count_goal = convert_input_count(data['count_goal'])
        if count_goal == -1:
            return {"success": False}

        for schema in mongodb_controller.get_accepted_schemas(problem_id):
            # submitted_schema_count += 1
            hit_id = mturk_controller.create_inspiration_hit(schema[mongodb_controller.TEXT], count_goal)
            if hit_id == "FAIL":
                print "submitting one of the schemas for create_inspiration_hit FAILED!!"
                continue
            schema_id = schema[mongodb_controller.SCHEMA_ID]
            mongodb_controller.insert_new_inspiration_hit(problem_id, schema_id, count_goal, hit_id)
            mongodb_controller.set_schema_processed_status(schema_id)
        mongodb_controller.set_inspiration_stage(problem_id)
        mongodb_controller.increment_inspiration_count_goal(problem_id, count_goal)
        return {"success": True,
                "url": "problems"}


class IdeaTaskHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        owner_username = cherrypy.session[USERNAME_KEY]
        data = cherrypy.request.json
        problem_id = data['problem_id']
        if not mongodb_controller.does_user_have_problem_with_id(owner_username, problem_id):
            raise cherrypy.HTTPError(403)
        count_goal = convert_input_count(data['count_goal'])
        if count_goal == -1:
            return {"success": False}

        for inspiration in mongodb_controller.get_accepted_inspirations(problem_id):
            problem_description = mongodb_controller.get_problem_description(inspiration[PROBLEM_ID])
            source_link = inspiration[mongodb_controller.INSPIRATION_LINK]
            image_link = inspiration[mongodb_controller.INSPIRATION_ADDITIONAL]
            explanation = inspiration[mongodb_controller.INSPIRATION_REASON]

            hit_id = mturk_controller.create_idea_hit(problem_description, source_link,
                                                      image_link, explanation, count_goal)
            # add the hit_id to schema
            if hit_id == "FAIL":
                print "submitting one of the inspirations create_idea_hit FAILED!!"
                continue
            inspiration_id = inspiration[mongodb_controller.INSPIRATION_ID]
            schema_id = inspiration[mongodb_controller.SCHEMA_ID]
            mongodb_controller.insert_new_idea_hit(problem_id, schema_id, inspiration_id, count_goal, hit_id)
            mongodb_controller.set_inspiration_processed_status(inspiration_id)
        mongodb_controller.set_idea_stage(problem_id)
        mongodb_controller.increment_idea_count_goal(problem_id, count_goal)
        return {"success": True,
                "url": "problems"}


class RejectHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        to_reject = data['to_reject']
        _type = data['type']
        _id = data['id']
        if _type == "schema":
            mongodb_controller.set_schema_rejected_flag(_id, to_reject)
        elif _type == "inspiration":
            mongodb_controller.set_inspiration_rejected_flag(_id, to_reject)


class FeedbackHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        idea_id = data["idea_id"]
        feedbacks = data["feedbacks"]

        count_goal = convert_input_count(data['count_goal'])
        if count_goal == -1:
            return {"success": False}

        idea_dict = mongodb_controller.get_idea_dict(idea_id)
        problem_text = mongodb_controller.get_problem_fields(idea_dict[PROBLEM_ID])[mongodb_controller.DESCRIPTION]
        idea_text = idea_dict[mongodb_controller.TEXT]

        for feedback in feedbacks:
            hit_id = mturk_controller.create_suggestion_hit(problem_text, idea_text, feedback, count_goal)
            # add the hit_id to schema
            if hit_id == "FAIL":
                return {"success": False}
            mongodb_controller.save_feedback(idea_id, feedback, count_goal, hit_id, idea_dict[PROBLEM_ID])
            mongodb_controller.idea_launched(idea_id)
        idea_dict = mongodb_controller.get_idea_dict(idea_id)
        return {"success": True,
                "suggestion_page_link": idea_dict[mongodb_controller.SUGGESTIONS_PAGE_LINK]}


def update_suggestions(problem_id):
    start = time.clock()
    idea_to_count = {}
    for feedback in mongodb_controller.get_feedbacks(problem_id):
        suggestion_hit_id = feedback[mongodb_controller.SUGGESTION_HIT_ID]
        suggestions = mturk_controller.get_suggestion_hit_results(suggestion_hit_id)
        if suggestions == "FAIL":
            continue
        idea_id = feedback[mongodb_controller.IDEA_ID]
        for suggestion in suggestions:
            if idea_id in idea_to_count:
                idea_to_count[idea_id] += 1
            else:
                idea_to_count[idea_id] = 1
            # replace time with a readable one and add to DB
            epoch_time_ms = long(suggestion.pop(mongodb_controller.TIME_CREATED))
            epoch_time = epoch_time_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
            suggestion[mongodb_controller.TIME_CREATED] = readable_time
            # add problem id
            suggestion[mongodb_controller.PROBLEM_ID] = problem_id
            # add idea id
            suggestion[mongodb_controller.IDEA_ID] = idea_id
            # add feedback text
            suggestion[mongodb_controller.FEEDBACK_TEXT] = feedback[mongodb_controller.TEXT]
            mongodb_controller.add_suggestion(suggestion)
    mongodb_controller.update_suggestions_count(idea_to_count)
    elapsed = time.clock()
    elapsed = elapsed - start
    # print "Done updating suggestions! Time spent:", elapsed*1000


class SuggestionUpdatesHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        thread = Thread(target=update_suggestions, args=[problem_id])
        thread.start()
        return mongodb_controller.get_suggestion_counts(problem_id)


class AcceptedSchemasCountHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        count = mongodb_controller.get_accepted_schemas_count(problem_id)
        return {"count": count}


class ProblemEditHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        if not mongodb_controller.does_user_have_problem_with_id(cherrypy.session[USERNAME_KEY], data[PROBLEM_ID]):
            raise cherrypy.HTTPError(403)
        mongodb_controller.edit_problem(data)
        return {"success": True,
                "url": "problems"}


class NewAccountHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        username = data['username']
        email = data['email']
        password = data['password']

        result = {
            "success": False
        }
        if "@" not in email:
            result["issue"] = "Illegal email"
            print "Illegal email"
            return result
        if mongodb_controller.is_email_in_use(email):
            result["issue"] = "Email already in use"
            print "Email already in use"
            return result
        if mongodb_controller.is_username_taken(username):
            result["issue"] = "This username is already taken"
            print "This username is already taken"
            return result

        # encrypt the password
        # password_hash = sha256_crypt.encrypt(password)

        mongodb_controller.new_account(username, email, password)  # password_hash)
        result["success"] = True
        cherrypy.session[USERNAME_KEY] = username
        if PREVIOUS_URL_KEY in cherrypy.session:
            result["url"] = cherrypy.session[PREVIOUS_URL_KEY]
            cherrypy.session.pop(PREVIOUS_URL_KEY)
        else:
            result["url"] = "index"
        return result


class SignInHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        name = data['name']
        password = data['password']

        is_email = '@' in name
        success = False
        if is_email:
            if mongodb_controller.is_email_in_use(name):
                hashed_password = mongodb_controller.get_password_for_email(name)
                if password == hashed_password:
                    # if sha256_crypt.verify(password, hashed_password):
                    success = True
                    name = mongodb_controller.get_username_from_email(name)
        elif mongodb_controller.is_username_taken(name):
            hashed_password = mongodb_controller.get_password_for_username(name)
            if password == hashed_password:
                # if sha256_crypt.verify(password, hashed_password):
                success = True
        result = {}
        if not success:
            result["success"] = False
            result["url"] = "index"
            return result
        else:
            result["success"] = True
            cherrypy.session[USERNAME_KEY] = name
            if PREVIOUS_URL_KEY in cherrypy.session:
                result["url"] = cherrypy.session[PREVIOUS_URL_KEY]
                cherrypy.session.pop(PREVIOUS_URL_KEY)
            else:
                result["url"] = "index"
            return result


class DeleteProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        if not mongodb_controller.does_user_have_problem_with_id(cherrypy.session[USERNAME_KEY], data[PROBLEM_ID]):
            raise cherrypy.HTTPError(403)
        mongodb_controller.delete_problem(data[PROBLEM_ID])


if __name__ == '__main__':
    # server configurations
    conf = {
        # configure sessions for identifying users.
        # Using filesystem backend to not lose sessions between reboots.
        '/': {
            'tools.sessions.on': True,
            'tools.sessions.storage_type': "file",
            'tools.sessions.storage_path': "./session_data/"
        },
        # these are for rest api requests, not html pages, so create method dispatchers
        '/save_new_problem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_new_account': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/get_count_updates': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_sign_in': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_inspiration_task': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/publish_problem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/delete_problem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_new_problem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_problem_edit': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_idea_task': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_reject': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_feedback': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/suggestion_updates': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/get_accepted_schemas_count': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    # class for serving static homepage
    webapp = HtmlPageLoader()

    webapp.post_sign_in = SignInHandler()
    webapp.save_new_problem = SaveNewProblemHandler()
    webapp.post_new_problem = PostNewProblemHandler()
    webapp.publish_problem = PublishProblemHandler()
    webapp.post_new_account = NewAccountHandler()
    webapp.get_count_updates = CountUpdatesHandler()
    webapp.post_inspiration_task = InspirationTaskHandler()
    webapp.delete_problem = DeleteProblemHandler()
    webapp.post_problem_edit = ProblemEditHandler()
    webapp.post_idea_task = IdeaTaskHandler()
    webapp.post_reject = RejectHandler()
    webapp.post_feedback = FeedbackHandler()
    webapp.suggestion_updates = SuggestionUpdatesHandler()
    webapp.get_accepted_schemas_count = AcceptedSchemasCountHandler()

    cherrypy.tree.mount(webapp, '/', conf)

    static_conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),  # cherrypy requires absolute path
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    cherrypy.tree.mount(None, '/static', static_conf)

    cherrypy.config.update({'error_page.404': error_page_404,
                            'error_page.403': error_page_403,
                            'request.error_response': unanticipated_error  # ,
                            # 'server.socket_host': '192.168.1.100',
                            # 'server.socket_port': 8080
                            })

    cherrypy.engine.start()
    cherrypy.engine.block()
