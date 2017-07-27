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
from utility_functions import convert_input_count, generate_id
from constants import *
import renderers
import well_ranked_counters
import launchers
import translation
import datetime


class HtmlPageLoader(object):

    def _cp_dispatch(self, vpath):
        if vpath[0] == "task":
            vpath.pop(0)
            if len(vpath) == 3:  # lang/task_type/worker_id
                cherrypy.request.params['lang'] = vpath.pop(0)  # first
                cherrypy.request.params['worker_id'] = vpath.pop()  # last
                print "new vpath =", vpath
                return self
            if len(vpath) == 4:  # /lang/ps1/schema_id/worker_id
                cherrypy.request.params['lang'] = vpath.pop(0)  # first
                cherrypy.request.params['worker_id'] = vpath.pop()  # last
                cherrypy.request.params['schema_id'] = vpath.pop()  # last
                return self

        elif len(vpath) == 3:
            if vpath.pop(0) != "problem":
                vpath.pop(-1)
            cherrypy.request.params['problem_slug'] = vpath.pop(0)
            return self

    @cherrypy.expose
    def sc1(self, lang, worker_id):
        if lang not in languages:
            raise cherrypy.HTTPError(404)
        return renderers.render_schema1(languages[lang], worker_id)

    @cherrypy.expose
    def sc2(self):
        return renderers.render_schema2()

    @cherrypy.expose
    def survey(self):
        return renderers.render_survey()

    @cherrypy.expose
    def ps1(self, lang, worker_id, schema_id):
        return renderers.render_inspiration(languages[lang], worker_id, schema_id)

    @cherrypy.expose
    def ns_ps1(self, lang, worker_id):
        return renderers.render_inspiration(languages[lang], worker_id)

    @cherrypy.expose
    def ps2(self):
        return renderers.render_idea()

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

    @cherrypy.expose
    def trans_insp_ch(self):
        return renderers.render_trans_insp(CHINESE)

    @cherrypy.expose
    def trans_insp_ru(self):
        return renderers.render_trans_insp(CHINESE)

    @cherrypy.expose
    def trans_idea_ch(self):
        return renderers.render_trans_insp(CHINESE)

    @cherrypy.expose
    def trans_insp_ru(self):
        return renderers.render_trans_insp(CHINESE)


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
        # MOCK
        data = cherrypy.request.json
        print data["languages"]
        extra_languages = [RUSSIAN, CHINESE]
        if input_problem_dict[LAZY]:
            thread = Thread(target=launchers.start_lazy_problem, args=[description, schema_assignments_num, problem_id])
            thread.start()
        elif len(extra_languages) > 0:
            import time
            for language in extra_languages:
                thread = Thread(target=translation.get_translation, args=[problem_id, description, language])
                thread.start()
                time.sleep(10)
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


class SubmitTaskHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        data = cherrypy.request.json
        print data
        type = data[TYPE]
        if type == SCHEMA1:
            adjust_schema_dict(data)
            mc.add_schema(data)
            return {"url": "/sc2"}

        elif type == SCHEMA2:
            adjust_schema_dict(data)
            mc.add_schema(data)
            return {"url": "/survey"}

        elif type == INSPIRATION:
            print str(dict(cherrypy.session))
            adjust_inspiration_dict(data)
            cherrypy.session[INSPIRATION_LINK] = data[INSPIRATION_LINK]
            cherrypy.session[INSPIRATION_ID] = data[INSPIRATION_ID]
            mc.add_inspiration(data)
            return {"url": "/ps2"}

        elif type == IDEA:
            adjust_idea_dict(data)
            mc.add_idea(data)
            return {"url": "/survey"}
        if type == SURVEY:
            del data[TYPE]
            if PROBLEM1 in cherrypy.session:
                data[TASK] = SCHEMA
            elif NO_SCHEMA in cherrypy.session:
                data[TASK] = PS_NS_TASK
            elif PROBLEM_ID in cherrypy.session:
                data[TASK] = PS_TASK
            mc.insert_worker(data)
            return {SUCCESS: True}


class PostRatingHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        data = cherrypy.request.json
        mc.insert_rating(data)


class SubmitTranslationHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        data = cherrypy.request.json
        # print data
        language = data[LANGUAGE]
        mc.insert_i_translation(data)
        if data[TYPE] == INSPIRATION:
            mc.update_inspiration({INSPIRATION_ID: data["id"]}, {"$set": {"translated": True}})
            inspiration_dict = mc.find_inspiration({LANGUAGE: language, "translated": {"$exists": False}})
            if inspiration_dict is None:
                return {"has_more": False}
            id = inspiration_dict[INSPIRATION_ID]
            original = inspiration_dict[SUMMARY]
            return {
                "id": id,
                "original": original,
                "has_more": True
            }


def adjust_schema_dict(d):
    # adjust dict to insert into db
    d[TEXT] = d.pop(SCHEMA)
    d[WELL_RANKED] = True
    d[SUBMIT_TIME] = datetime.datetime.now()
    d[ACCEPT_TIME] = cherrypy.session[ACCEPT_TIME]
    d[TIME_SPENT] = str(d[SUBMIT_TIME] - d[ACCEPT_TIME]).split('.')[0]
    d[INSPIRED_NUM] = 0
    d[SCHEMA_ID] = generate_id()


def adjust_inspiration_dict(d):
    d[INSPIRATION_ID] = generate_id()
    d[NO_SCHEMA] = cherrypy.session[NO_SCHEMA]
    if not d[NO_SCHEMA]:
        d[SCHEMA_ID] = cherrypy.session[SCHEMA_ID]
        mc.update_schema({SCHEMA_ID: d[SCHEMA_ID]}, {"$inc": {INSPIRED_NUM: 1}})
    else:
        query = {
            PROBLEM_ID: d[PROBLEM_ID],
            LANGUAGE: d[LANGUAGE],
            APPROVED: True
        }
        mc.update_translation(query, {"$inc": {NS_USE_COUNT: 1}})
    d[SUBMIT_TIME] = datetime.datetime.now()
    d[ACCEPT_TIME] = cherrypy.session[ACCEPT_TIME]
    d[TIME_SPENT] = str(d[SUBMIT_TIME] - d[ACCEPT_TIME]).split('.')[0]
    d[WELL_RANKED] = True


def adjust_idea_dict(d):
    d[IDEA_ID] = generate_id()
    d[NO_SCHEMA] = cherrypy.session[NO_SCHEMA]
    d[INSPIRATION_ID] = cherrypy.session[INSPIRATION_ID]
    d[TEXT] = d.pop(IDEA)
    d[SUBMIT_TIME] = datetime.datetime.now()
    d[ACCEPT_TIME] = cherrypy.session[ACCEPT_TIME]
    d[TIME_SPENT] = str(d[SUBMIT_TIME] - d[ACCEPT_TIME]).split('.')[0]
    d[WELL_RANKED] = True


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
        },
        '/submit_task': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_rating': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/submit_translation': {
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
    webapp.post_rating = PostRatingHandler()
    webapp.submit_task = SubmitTaskHandler()
    webapp.submit_translation = SubmitTranslationHandler()

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
                            'request.error_response': renderers.unanticipated_error,
                            'server.socket_host': 'ethings.jios.org',
                            'server.socket_port': 8080
                            })

    cherrypy.engine.start()
    cherrypy.engine.block()
