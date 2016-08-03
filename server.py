"""
Cherrypy server. Used to start the webpage, get input over Rest API,
send it to MTurk runnable. We are not dealing with MTurk in Python
since MTurk's Java SDK is more recommendable/documented/exemplified.
We are not using Java for server since Python is less painful.
"""

import os
import cherrypy
import mongodb_controller as mc
from threading import Thread
import update_managers
import authorization
from utility_functions import convert_input_count
from constants import *
import renderers
import well_ranked_counters
import launchers


class HtmlPageLoader(object):

    def _cp_dispatch(self, vpath):
        if len(vpath) == 3:
            if vpath.pop(0) != "problem":
                vpath.pop(-1)
            cherrypy.request.params['problem_slug'] = vpath.pop(0)
            # print "new vpath =", vpath
            return self

    @cherrypy.expose
    def index(self):
        return renderers.render_homepage()

    @cherrypy.expose
    def home(self):
        return renderers.render_homepage()

    @cherrypy.expose
    def problems(self):
        return renderers.render_problems_page()

    @cherrypy.expose
    def edit(self, problem_slug):
        return renderers.render_edit_page(problem_slug)

    @cherrypy.expose
    def view(self, problem_slug):
        return renderers.render_view_page(problem_slug)

    @cherrypy.expose
    def schemas(self, problem_slug):
        return renderers.render_schemas_page(problem_slug)

    @cherrypy.expose
    def inspirations(self, problem_slug):
        return renderers.render_inspirations_page(problem_slug)

    @cherrypy.expose
    def ideas(self, problem_slug):
        return renderers.render_ideas_page(problem_slug)

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
        return renderers.render_new_problem()

    @cherrypy.expose
    def account_edit(self):
        return renderers.render_account_edit_page()

    @cherrypy.expose
    def profile_info(self):
        return renderers.render_profile()

    @cherrypy.expose
    def suggestions(self, problem_slug):
        return renderers.render_suggestions_page(problem_slug)


class SaveProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        return launchers.save_problem()


class SubmitProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        result_dict = launchers.save_problem(True)
        if not result_dict["success"]:
            return result_dict
        input_problem_dict = result_dict["input_problem_dict"]
        problem_id = input_problem_dict[PROBLEM_ID]
        description = input_problem_dict[DESCRIPTION]
        schema_assignments_num = input_problem_dict[SCHEMA_ASSIGNMENTS_NUM]
        mc.set_schema_stage(problem_id)
        if input_problem_dict[LAZY]:
            thread = Thread(target=launchers.start_lazy_problem, args=[description, schema_assignments_num, problem_id])
            thread.start()
        else:
            thread = Thread(target=launchers.launch_schema_hit, args=[problem_id, description, schema_assignments_num])
            thread.start()
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
        thread = Thread(target=launchers.publish_problem, args=[problem_id])
        thread.start()
        return {"success": True}


class CountUpdatesHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        username = cherrypy.session[USERNAME_KEY]
        thread = Thread(target=update_managers.update_hit_results, args=[username])
        thread.start()
        return well_ranked_counters.get_count_dicts_for_user(username)


class InspirationTaskHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        owner_username = cherrypy.session[USERNAME_KEY]
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        if not mc.does_user_have_problem_with_id(owner_username, problem_id):
            raise cherrypy.HTTPError(403)
        count_goal = convert_input_count(data['count_goal'])
        if count_goal == -1:
            return {"success": False}
        mc.set_inspiration_stage(problem_id)
        thread = Thread(target=launchers.post_inspiration_task, args=[problem_id, count_goal])
        thread.start()
        return {"success": True,
                "url": "problems"}


class IdeaTaskHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            # print 184
            raise cherrypy.HTTPError(403)
        owner_username = cherrypy.session[USERNAME_KEY]
        data = cherrypy.request.json
        print data
        problem_id = data['problem_id']
        if not mc.does_user_have_problem_with_id(owner_username, problem_id):
            # print 190
            raise cherrypy.HTTPError(403)
        count_goal = convert_input_count(data['count_goal'])
        if count_goal == -1:
            return {"success": False}
        mc.set_idea_stage(problem_id)
        thread = Thread(target=launchers.post_idea_task, args=[problem_id, count_goal])
        thread.start()
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
            mc.set_schema_rejected_flag(_id, to_reject)
        elif _type == "inspiration":
            mc.set_inspiration_rejected_flag(_id, to_reject)
        elif _type == "idea":
            mc.set_idea_rejected_flag(_id, to_reject)


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
        idea_dict = mc.get_idea_dict(idea_id)
        mc.set_suggestion_stage(idea_dict[PROBLEM_ID])
        thread = Thread(target=launchers.post_feedback, args=[idea_dict, idea_id, feedbacks, count_goal])
        thread.start()
        return {"success": True}


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
        feedback_dict = mc.get_feedback_dict(feedback_id)
        idea_id = feedback_dict[IDEA_ID]
        idea_dict = mc.get_idea_dict(idea_id)
        feedbacks = [feedback_dict[TEXT]]
        thread = Thread(target=launchers.post_feedback, args=[idea_dict, idea_id, feedbacks, count_goal])
        thread.start()


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
        thread = Thread(target=launchers.relaunch_schema_task, args=[problem_id, count])
        thread.start()
        return {"success": True}


class AcceptedSchemasCountHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        problem_id = data[PROBLEM_ID]
        count = mc.get_accepted_schemas_count(problem_id)
        return {"count": count}


class DeleteProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        if not mc.does_user_have_problem_with_id(cherrypy.session[USERNAME_KEY], data[PROBLEM_ID]):
            raise cherrypy.HTTPError(403)
        mc.delete_problem(data[PROBLEM_ID])


class GetFeedbacksHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        idea_id = data[IDEA_ID]
        feedback_dicts = mc.get_feedback_dicts(idea_id)
        result = []
        for feedback_dict in feedback_dicts:
            for_result = {
                FEEDBACK_ID: feedback_dict[FEEDBACK_ID],
                TEXT: feedback_dict[TEXT]
            }
            result.append(for_result)
        return {FEEDBACKS_FIELD: result}


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
        '/save_problem': {
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
        '/submit_problem': {
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
        '/get_accepted_schemas_count': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/more_schemas': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/more_suggestions': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/get_feedbacks': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    # class for serving static homepage
    webapp = HtmlPageLoader()

    webapp.post_sign_in = authorization.SignInHandler()
    webapp.save_problem = SaveProblemHandler()
    webapp.submit_problem = SubmitProblemHandler()
    webapp.publish_problem = PublishProblemHandler()
    webapp.post_new_account = authorization.NewAccountHandler()
    webapp.get_count_updates = CountUpdatesHandler()
    webapp.post_inspiration_task = InspirationTaskHandler()
    webapp.delete_problem = DeleteProblemHandler()
    webapp.post_idea_task = IdeaTaskHandler()
    webapp.post_reject = RejectHandler()
    webapp.post_feedback = FeedbackHandler()
    webapp.get_accepted_schemas_count = AcceptedSchemasCountHandler()
    webapp.more_schemas = MoreSchemasHandler()
    webapp.more_suggestions = MoreSuggestionsHandler()
    webapp.get_feedbacks = GetFeedbacksHandler()

    cherrypy.tree.mount(webapp, '/', conf)

    static_conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),  # cherrypy requires absolute path
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public',
        }
    }
    cherrypy.tree.mount(None, '/static', static_conf)

    cherrypy.config.update({'error_page.404': renderers.error_page_404,
                            'error_page.403': renderers.error_page_403,
                            'request.error_response': renderers.unanticipated_error
                            # 'server.socket_host': '192.168.1.147',
                            # 'server.socket_port': 8080
                            })

    cherrypy.engine.start()
    cherrypy.engine.block()
