"""
Cherrypy server. Used to start the webpage, get input over Rest API,
send it to MTurk runnable. We are not dealing with MTurk in Python
since MTurk's Java SDK is more recommendable/documented/exemplified.
We are not using Java for server since Python is less painful.

To run, enter "python server.py" in terminal.
"""

import os
import cherrypy
import datetime
import mturk_controller
import mongodb_controller

COOKIE_NAME = "user_id"


class StaticPageLoader(object):
    # homepage
    @cherrypy.expose
    def index(self):
        if COOKIE_NAME in cherrypy.session:
            return open('problem_results.html')
        return open('problem_entry.html')


class PostproblemHandler(object):
    exposed = True

    # post requests go here
    def POST(self, problem):
        [hit_id, finish_time] = mturk_controller.create_schema_making_hit(problem)
        # get user_id either from mongodb insertion or from session
        user_id = get_user_id()
        print "user", user_id, "posted a problem"
        # add problem to the database
        mongodb_controller.add_problem(hit_id, problem, user_id, finish_time)

        # return the finish time
        # format example: 23 Apr 2012 4:00 PM
        readable_finish_time = finish_time.strftime("%d %b %Y %I:%M %p")
        print "finish_time=", readable_finish_time
        return readable_finish_time


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
        print "user", user_id, "wants his problems"
        problems = mongodb_controller.get_problems_by_user(user_id)
        return {"problems": problems}


class GetschemasHandler(object):
    exposed = True

    # get requests go here
    @cherrypy.tools.json_out()
    def GET(self, problem_id):
        hit_id = mongodb_controller.get_hit_id(problem_id)
        answers = mturk_controller.get_schema_making_results(hit_id)
        return answers


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
        '/submit': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/getresults': {
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
