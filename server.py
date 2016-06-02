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
# import passlib.hash
env = Environment(loader=PackageLoader('server', '/templates'))
# sha256_crypt = passlib.hash.sha256_crypt


COOKIE_NAME = "user_id"
PROBLEM_COMPLETION_STATUS = "schema_count"
PROBLEM_FOR_FRONTEND_ID = "problem_id"
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
    def schemas(self, problem_slug):
        return render_schemas_page(problem_slug)

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
    if USERNAME_KEY in cherrypy.session:
        username = cherrypy.session[USERNAME_KEY]
        if mongodb_controller.does_user_have_problem(username, problem_slug):
            hit_id = mongodb_controller.get_generate_schema_hit_id(username, problem_slug)
            schemas = mongodb_controller.get_schemas(hit_id)
            template = env.get_template('schemas.html')
            return template.render(schemas=schemas)
        else:
            raise cherrypy.HTTPError(404, "You, {}, don't have a problem named like {}".format(username, problem_slug))
    else:
        cherrypy.session[PREVIOUS_URL_KEY] = "{}/schemas".format(problem_slug)
        raise cherrypy.HTTPRedirect("sign_in")


def update_schemas_for_user(username):
    for generate_schema_hit_id in mongodb_controller.get_users_gen_schema_hit_ids(username):
        update_schemas_for_problem(generate_schema_hit_id)


def update_schemas_for_problem(hit_id):
    schema_dicts = mturk_controller.get_schema_making_results(hit_id)

    schema_count = 0
    # replace time with a readable one and add to DB
    for schema_dict in schema_dicts:
        schema_count += 1
        # pop epoch time
        epoch_time_ms = long(schema_dict.pop(mongodb_controller.SCHEMA_TIME))
        epoch_time = epoch_time_ms / 1000.0
        readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
        # add readable time
        schema_dict[mongodb_controller.SCHEMA_TIME] = readable_time
        mongodb_controller.add_schema(schema_dict)
    mongodb_controller.update_schema_count(hit_id, schema_count)


class SchemaCountUpdatesHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    def GET(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        username = cherrypy.session[USERNAME_KEY]
        update_schemas_for_user(username)
        return mongodb_controller.get_schema_counts_for_user(username)


class NewProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        owner_username = cherrypy.session[USERNAME_KEY]
        data = cherrypy.request.json
        title = data["title"]
        description = data["description"]

        casting_fail = False
        schema_count_goal = data["schema_count_goal"]
        if not isinstance(schema_count_goal, int):
            try:
                schema_count_goal = int(schema_count_goal)
            except ValueError:
                casting_fail = False

        if not casting_fail:
            hit_id = mturk_controller.create_schema_making_hit(description)
            print "MTurk controller output:", hit_id
        else:
            print "Casting fail!!!"

        result = {}
        if hit_id != "FAIL" and not casting_fail:
            time_created = datetime.datetime.now().strftime(READABLE_TIME_FORMAT)
            mongodb_controller.add_problem(hit_id, title, description, owner_username, schema_count_goal, time_created)
            result["success"] = True
            result["url"] = "problems"
            return result
        else:
            result["success"] = False
            return result


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
            return result
        if mongodb_controller.is_email_in_use(email):
            result["issue"] = "Email already in use"
            return result
        if mongodb_controller.is_username_taken(username):
            result["issue"] = "This username is already taken"
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


def render_new_problem():
    template = env.get_template('new_problem.html');
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
        '/post_new_problem': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_new_account': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/get_schema_count_updates': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        },
        '/post_sign_in': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher()
        }
    }
    # class for serving static homepage
    webapp = HtmlPageLoader()

    webapp.post_sign_in = SignInHandler()
    webapp.post_new_problem = NewProblemHandler()
    webapp.post_new_account = NewAccountHandler()
    webapp.get_schema_count_updates = SchemaCountUpdatesHandler()

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
                            'request.error_response': unanticipated_error#,
                            # 'server.socket_host': '192.168.1.85',
                            # 'server.socket_port': 8080
                            })

    cherrypy.engine.start()
    cherrypy.engine.block()
