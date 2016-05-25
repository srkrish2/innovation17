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
from jinja2 import Environment, PackageLoader
import passlib.hash
env = Environment(loader=PackageLoader('server', '/templates'))
sha256_crypt = passlib.hash.sha256_crypt


COOKIE_NAME = "user_id"
PROBLEM_COMPLETION_STATUS = "schema_count"
PROBLEM_FOR_FRONTEND_ID = "problem_id"
# format example: 23 Apr 2012 4:00 PM
READABLE_TIME_FORMAT = "%d %b %Y %I:%M %p"


class HtmlPageLoader(object):

    # index
    @cherrypy.expose
    def index(self):
        return render_homepage()
        # return open('home.html')

    # homepage
    @cherrypy.expose
    def home(self):
        return render_homepage()
        # return open('home.html')

    @cherrypy.expose
    def projects(self):
        return render_projects()
        # return open('projects.html')

    @cherrypy.expose
    def new_project(self):
        return render_new_project()
        # return open('new_project.html')

    @cherrypy.expose
    def login(self):
        return open('login.html')

    @cherrypy.expose
    def schemas(self):
        return render_schemas()
        # return open('schemas.html')

    @cherrypy.expose
    def new_schema(self):
        return render_new_schema()
        # return open('new_schema.html')

    @cherrypy.expose
    def account_edit(self):
        return render_account_edit_page()
        # return open('account_edit.html')


def render_homepage():
    template = env.get_template('home.html')
    return template.render()
def render_account_edit_page():
    template = env.get_template('account_edit.html')
    return template.render()

def render_new_project():
    template = env.get_template('new_project.html');
    return template.render()

def render_projects():
    template = env.get_template('projects.html')
    return template.render()
def render_new_schema():
    template = env.get_template('new_schema.html')
    return template.render()

def render_schemas():
    template = env.get_template('schemas.html')
    return template.render()

class PostProblemHandler(object):
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


class GetProblemsHandler(object):
    exposed = True

    # get requests go here
    @cherrypy.tools.json_out()
    def GET(self):
        # get user_id either from mongodb insertion or from session
        user_id = get_user_id()
        print "got a /get_problems request from", user_id
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


class GetSchemasHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        hit_id = data['problem_id']

        print "got a /get_schemas request for", hit_id
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
            "success": False,
            "username_taken": False,
            "email_in_use": False
        }

        if mongodb_controller.is_email_in_use(email):
            result["email_in_use"] = True
            return result

        if mongodb_controller.is_username_taken(username):
            result["username_taken"] = True
            return result

        # encrypt the password
        password_hash = sha256_crypt.encrypt(password)

        mongodb_controller.new_account(username, email, password_hash)
        result["success"] = True
        return result


class SignInHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        name = data['name']
        password = data['password']

        if '@' in name:
            if mongodb_controller.is_email_in_use(name):
                hashed_password = mongodb_controller.get_password_for_email(name)
                if sha256_crypt.verify(password, hashed_password):
                    return {"success": True}
            return {"success": False}

        if mongodb_controller.is_username_taken(name):
            hashed_password = mongodb_controller.get_password_for_username(name)
            if sha256_crypt.verify(password, hashed_password):
                return {"success": True}
        return {"success": False}


class NewProjectHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        data = cherrypy.request.json
        title = data['title']
        description = data['description']
        category = data['category']
        return {"url": "index"}


class IsLoggedInHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self):
        return {"is_logged_in": COOKIE_NAME in cherrypy.session}


def render_account_edit_page():
    template = env.get_template('my_template.html')
    return template.render(link="https://realpython.com/blog/python/primer-on-jinja-templating")


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
        # these are for requests, not html pages, so create method dispatchers
        '/post_problem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/get_problems': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/get_schemas': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_sign_in': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_new_project': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_new_account': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/is_logged_in': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    # class for serving static homepage
    webapp = HtmlPageLoader()
    # all requests sent to /postproblem go to this class. The rest work the same way.
    webapp.post_problem = PostProblemHandler()
    webapp.get_problems = GetProblemsHandler()
    webapp.get_schemas = GetSchemasHandler()
    webapp.post_sign_in = SignInHandler()
    webapp.post_new_project = NewProjectHandler()
    webapp.post_new_account = NewAccountHandler()
    webapp.is_logged_in = IsLoggedInHandler()
    # start the server
    cherrypy.quickstart(webapp, '/', conf)
