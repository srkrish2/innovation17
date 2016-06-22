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
import updaters
import authorization
from utility_functions import convert_input_count, check_problem_access, get_problem_parameters, make_links_list
from constants import USERNAME_KEY, PREVIOUS_URL_KEY, READABLE_TIME_FORMAT
from jinja2 import Environment, PackageLoader

PROBLEM_ID = "problem_id"
SUGGESTIONS_PAGE_LINK = "suggestions_page_link"
env = Environment(loader=PackageLoader('server', '/templates'))
# import passlib.hash
# sha256_crypt = passlib.hash.sha256_crypt


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
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("sign_in")

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
        schemas = list(mongodb_controller.get_well_ranked_schemas(problem_id))
        template = env.get_template('schemas.html')
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
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
            idea[SUGGESTIONS_PAGE_LINK] = "/{}/suggestions".format(idea[mongodb_controller.SLUG])
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
    idea_dict = mongodb_controller.get_idea_dict_for_slug(idea_slug)
    idea_id = idea_dict[mongodb_controller.IDEA_ID]
    feedbacks_with_suggestions = []
    for feedback_dict in mongodb_controller.get_feedback_dicts(idea_id):
        feedback_id = feedback_dict[mongodb_controller.FEEDBACK_ID]
        suggestions = []
        for suggestion in mongodb_controller.get_suggestion_dicts(feedback_id):
            suggestions.append(suggestion)
        feedback_dict["suggestions"] = suggestions
        feedbacks_with_suggestions.append(feedback_dict)
    idea_text = idea_dict[mongodb_controller.TEXT]
    problem_id = idea_dict[mongodb_controller.PROBLEM_ID]

    print str(feedbacks_with_suggestions), idea_id, idea_text, problem_id
    template = env.get_template('suggestions.html')
    return template.render(feedbacks=feedbacks_with_suggestions, idea_id=idea_id, idea_text=idea_text,
                           problem_id=problem_id)


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


class PublishProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        [title, description, schema_count_goal] = mongodb_controller.get_problem_fields(problem_id)
        hit_id = mturk_controller.create_schema_making_hit(description, schema_count_goal)
        if hit_id == "FAIL":
            return {"success": False}
        mongodb_controller.set_schema_stage(problem_id)
        mongodb_controller.insert_new_schema_hit(problem_id, schema_count_goal, hit_id)
        return {"success": True}


class CountUpdatesHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    def GET(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        username = cherrypy.session[USERNAME_KEY]
        thread = Thread(target=updaters.update_hit_results, args=[username])
        thread.start()
        return mongodb_controller.get_counts_for_user(username)


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
        elif _type == "idea":
            mongodb_controller.set_idea_rejected_flag(_id, to_reject)


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
        problem_id = idea_dict[PROBLEM_ID]
        problem_text = mongodb_controller.get_problem_description(problem_id)
        idea_text = idea_dict[mongodb_controller.TEXT]
        for feedback in feedbacks:
            hit_id = mturk_controller.create_suggestion_hit(problem_text, idea_text, feedback, count_goal)
            if hit_id == "FAIL":
                return {"success": False}
            feedback_id = ''.join(random.sample(string.hexdigits, 8))
            mongodb_controller.add_feedback(feedback_id, feedback, idea_id)
            mongodb_controller.insert_new_suggestion_hit(problem_id, idea_id, feedback_id, count_goal, hit_id)
        mongodb_controller.idea_launched(idea_id)
        mongodb_controller.increment_suggestion_count_goal(idea_id, count_goal)
        mongodb_controller.set_suggestion_stage(problem_id)
        return {"success": True,
                SUGGESTIONS_PAGE_LINK: "/{}/suggestions".format(idea_dict[mongodb_controller.SLUG])}


class MoreSuggestionsHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def GET(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        count = data["count"]
        feedback_id = data["feedback_id"]

        count_goal = convert_input_count(count)
        if count_goal == -1:
            return {"success": False}

        feedback_dict = mongodb_controller.get_feedback_dict(feedback_id)
        idea_id = feedback_dict[mongodb_controller.IDEA_ID]
        idea_dict = mongodb_controller.get_idea_dict(idea_id)
        problem_id = idea_dict[PROBLEM_ID]
        problem_text = mongodb_controller.get_problem_description(problem_id)
        idea_text = idea_dict[mongodb_controller.TEXT]
        feedback_text = feedback_dict[mongodb_controller.TEXT]

        hit_id = mturk_controller.create_suggestion_hit(problem_text, idea_text, feedback_text, count_goal)
        if hit_id == "FAIL":
            return {"success": False}
        mongodb_controller.insert_new_suggestion_hit(problem_id, idea_id, feedback_id, count_goal, hit_id)
        mongodb_controller.increment_suggestion_count_goal(idea_id, count_goal)


class SuggestionUpdatesHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        thread = Thread(target=updaters.update_suggestions, args=[problem_id])
        thread.start()
        return mongodb_controller.get_suggestion_counts(problem_id)


def relaunch_schema_task(problem_id, assignments_num):
    description = mongodb_controller.get_problem_description(problem_id)
    hit_id = mturk_controller.create_schema_making_hit(description, assignments_num)
    if hit_id == "FAIL":
        return {"success": False}
    mongodb_controller.insert_new_schema_hit(problem_id, assignments_num, hit_id)
    mongodb_controller.increment_schema_count_goal(problem_id, assignments_num)
    return {"success": True}


class MoreSchemasHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        count = convert_input_count(data["count"])
        if count == -1:
            return {"success": False}
        return relaunch_schema_task(problem_id, count)


def relaunch_idea_task(inspiration_id, count):
    inspiration = mongodb_controller.get_inspiration_dict(inspiration_id)
    inspiration_id = inspiration[mongodb_controller.INSPIRATION_ID]
    problem_id = inspiration_id[mongodb_controller.PROBLEM_ID]
    problem_description = mongodb_controller.get_problem_description(problem_id)
    source_link = inspiration[mongodb_controller.INSPIRATION_LINK]
    image_link = inspiration[mongodb_controller.INSPIRATION_ADDITIONAL]
    explanation = inspiration[mongodb_controller.INSPIRATION_REASON]
    hit_id = mturk_controller.create_idea_hit(problem_description, source_link, image_link, explanation, count)
    schema_id = inspiration[mongodb_controller.SCHEMA_ID]
    if hit_id == "FAIL":
        return {"success": False}
    mongodb_controller.insert_new_idea_hit(problem_id, schema_id, inspiration_id, count, hit_id)
    mongodb_controller.increment_idea_count_goal(problem_id, count)


class MoreIdeasHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        inspiration_id = data["inspiration_id"]
        count = convert_input_count(data["count"])
        if count == -1:
            return {"success": False}
        return relaunch_idea_task(inspiration_id, count)


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
            'tools.sessions.storage_path': "./session_data/",
            'tools.sessions.timeout': 365*24*60
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
        },
        '/more_schemas': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/more_suggestions': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    # class for serving static homepage
    webapp = HtmlPageLoader()

    webapp.post_sign_in = authorization.SignInHandler()
    webapp.save_new_problem = SaveNewProblemHandler()
    webapp.post_new_problem = PostNewProblemHandler()
    webapp.publish_problem = PublishProblemHandler()
    webapp.post_new_account = authorization.NewAccountHandler()
    webapp.get_count_updates = CountUpdatesHandler()
    webapp.post_inspiration_task = InspirationTaskHandler()
    webapp.delete_problem = DeleteProblemHandler()
    webapp.post_problem_edit = ProblemEditHandler()
    webapp.post_idea_task = IdeaTaskHandler()
    webapp.post_reject = RejectHandler()
    webapp.post_feedback = FeedbackHandler()
    webapp.suggestion_updates = SuggestionUpdatesHandler()
    webapp.get_accepted_schemas_count = AcceptedSchemasCountHandler()
    webapp.more_schemas = MoreSchemasHandler()
    webapp.more_suggestions = MoreSuggestionsHandler()

    cherrypy.tree.mount(webapp, '/', conf)

    static_conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),  # cherrypy requires absolute path
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public',
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
