"""
Cherrypy server. Used to start the webpage, get input over Rest API,
send it to MTurk runnable. We are not dealing with MTurk in Python
since MTurk's Java SDK is more recommendable/documented/exemplified.
We are not using Java for server since Python is less painful.

To run, enter "python server.py" in terminal.
"""

import os
import cherrypy
# to not flood mturk
# import mock_mturk_controller as mturk_controller
import mturk_controller
import mongodb_controller
import datetime

COOKIE_NAME = "user_id"
PROBLEM_COMPLETION_STATUS = "schema_count"
PROBLEM_FOR_FRONTEND_ID = "problem_id"
# format example: 23 Apr 2012 4:00 PM
READABLE_TIME_FORMAT = "%d %b %Y %I:%M %p"


class StaticPageLoader(object):
    # homepage
    @cherrypy.expose
    def index(self):
        # if COOKIE_NAME in cherrypy.session:
        #     return open('problem_results.html')
        return open('index.html')

    @cherrypy.expose
    def projects(self):
        return open('projects.html')

    @cherrypy.expose
    def newproject(self):
        return open('newproject.html')

    @cherrypy.expose
    def login(self):
        return open('login.html')



class PostproblemHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        problem = data['problem']

        hit_id = mturk_controller.create_schema_making_hit(problem)
        if hit_id == "FAIL":
            return {"success": False}
        # get user_id either from mongodb insertion or from session
        user_id = get_user_id()
        print "user", user_id, "posted a problem"
        # add problem to the database
        mongodb_controller.add_problem(hit_id, problem, user_id)

        return {"success": True}



def get_user_id():
    if COOKIE_NAME in cherrypy.session:
        return cherrypy.session[COOKIE_NAME]
    user_id = mongodb_controller.add_user()
    cherrypy.session[COOKIE_NAME] = user_id
    return user_id


class GetproblemsHandler(object):
    exposed = True

    # get requests go here
    @cherrypy.tools.json_out()
    def GET(self):
        # get user_id either from mongodb insertion or from session
        user_id = get_user_id()
        print "got a /getproblems request from", user_id
        problems = mongodb_controller.get_problems_by_user(user_id)
        print "user's problems:", problems
        for problem in problems:
            hit_id = problem[mongodb_controller.PROBLEM_HIT_ID]
            schema_count = mturk_controller.get_schema_making_status(hit_id)
            problem[PROBLEM_COMPLETION_STATUS] = schema_count

            # rename hit_id key to problem_id
            problem[PROBLEM_FOR_FRONTEND_ID] = hit_id
            problem.pop(mongodb_controller.PROBLEM_HIT_ID, None)
        return {"problems": problems}


class GetschemasHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        hit_id = data['problem_id']

        print "got a /getschemas request for", hit_id
        schema_dicts = mturk_controller.get_schema_making_results(hit_id)

        # replace time with a readable one and add to DB
        for schema_dict in schema_dicts:
            # pop epoch time
            epoch_time_ms = long(schema_dict.pop(mongodb_controller.SCHEMA_TIME))
            epoch_time = epoch_time_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
            # add readable time
            schema_dict[mongodb_controller.SCHEMA_TIME] = readable_time
            mongodb_controller.add_schema(schema_dict)

            # rename hit_id key to problem_id
            schema_dict[PROBLEM_FOR_FRONTEND_ID] = hit_id
            schema_dict.pop(mongodb_controller.PROBLEM_HIT_ID, None)

        return {"schemas": schema_dicts}


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
        # configuration for serving static files like css/js that the html uses
        # e.g. http://hostname/static/js/my.js would go to ./public/js/my.js
        '/static': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),  # cherrypy requires absolute path
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        },
        # /submit is for post requests, so create a method dispatcher
        '/postproblem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/getproblems': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/getschemas': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    # class for serving static homepage
    webapp = StaticPageLoader()
    # all requests sent to /postproblem go to this class
    webapp.postproblem = PostproblemHandler()
    # all requests sent to /getproblems go to this class
    webapp.getproblems = GetproblemsHandler()
    # all requests sent to /getschemas go to this class
    webapp.getschemas = GetschemasHandler()
    # start the server
    cherrypy.quickstart(webapp, '/', conf)
