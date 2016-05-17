"""
Cherrypy server. Used to start the webpage, get input over Rest API,
send it to MTurk runnable. We are not dealing with MTurk in Python
since MTurk's Java SDK is more recommendable/documented/exeplified.
We are not using Java for server since Python is less painful.

To run, enter "python server.py" in terminal.
"""

import os
import cherrypy
import datetime
import mturk_controller

COOKIE_NAME = "user_id"

# TODO: back these up in filesystem
# TODO: keep hit_id in user sessions
user_to_hit_id = {}
# TODO: what if they have several hits
user_to_time = {}


class StaticPageLoader(object):
    # homepage
    @cherrypy.expose
    def index(self):
        if COOKIE_NAME in cherrypy.session:
            return open('problem_results.html')
        return open('problem_entry.html')


class GetresultsHandler(object):
    exposed = True

    # post requests go here
    def GET(self):
        if COOKIE_NAME in cherrypy.session:
            print "user with key_data =", cherrypy.session[COOKIE_NAME], "wants his results"
            finish_time = user_to_time[cherrypy.session[COOKIE_NAME]]
            if finish_time < datetime.datetime.now():
                # TODO: let them get whatever is done?
                return "you're here too early"
            else:
                hit_id = user_to_hit_id[cherrypy.session[COOKIE_NAME]]
                return mturk_controller.get_hit_results(hit_id)
        else:
            print "User that made a GET request doesn't have our cookie"


class SubmitHandler(object):
    exposed = True

    # post requests go here
    def POST(self, problem):
        [hit_id, finish_time] = mturk_controller.process_problem(problem)
        # create a session for the user using problem as identification
        key_data = problem[:20]
        cherrypy.session[COOKIE_NAME] = key_data

        user_to_hit_id[key_data] = hit_id
        user_to_time[key_data] = finish_time

        # return the finish time
        # format example: 23 Apr 2012 4:00 PM
        readable_finish_time = finish_time.strftime("%d %b %Y %I:%M %p")
        print "finish_time=", readable_finish_time
        return readable_finish_time


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
    # all requests sent to /submit go to this class
    webapp.submit = SubmitHandler()
    # all requests sent to /getresults go to this class
    webapp.getresults = GetresultsHandler()
    # start the server
    cherrypy.quickstart(webapp, '/', conf)
