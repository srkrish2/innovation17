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
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        schemas = mongodb_controller.get_schemas(problem_id)
        template = env.get_template('schemas.html')
        return template.render(schemas=schemas, problem_id=problem_id)


def render_inspirations_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mongodb_controller.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        inspirations = mongodb_controller.get_inspirations(problem_id)
        template = env.get_template('inspirations_card.html')
        inspiration_dicts_list = []
        for inspiration in inspirations:
            problem_text = mongodb_controller.get_problem_text(inspiration[mongodb_controller.PROBLEM_ID])
            schema_text = mongodb_controller.get_schema_text(inspiration[mongodb_controller.SCHEMA_ID])
            inspiration["problem_text"] = problem_text
            inspiration["schema_text"] = schema_text
            inspiration_dicts_list.append(inspiration)
        return template.render(inspirations=inspiration_dicts_list)


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


class CountUpdatesHandler(object):
    exposed = True

    # post requests go here
    @cherrypy.tools.json_out()
    def GET(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        username = cherrypy.session[USERNAME_KEY]
        for problem_id in mongodb_controller.get_users_problem_ids(username):
            stage = mongodb_controller.get_stage(problem_id)
            if stage == mongodb_controller.STAGE_SCHEMA:
                update_schemas_for_problem(problem_id)
            elif stage == mongodb_controller.STAGE_INSPIRATION:
                update_inspirations_for_problem(problem_id)
            elif stage == mongodb_controller.STAGE_IDEA:
                update_ideas_for_problem(problem_id)
        return mongodb_controller.get_counts_for_user(username)


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
    if schema_count > 0:
        mongodb_controller.update_schema_count(hit_id, schema_count)


def update_inspirations_for_problem(problem_id):
    for schema_id in mongodb_controller.get_schema_ids(problem_id):
        inspiration_hit_id = mongodb_controller.get_inspiration_hit_id(schema_id)
        inspirations = mturk_controller.get_inspiration_hit_results(inspiration_hit_id)
        if inspirations == "FAIL":
            print "mturk_controller.get_inspiration_hit_results - FAIL!"
            return
        inspiration_count = 0
        for inspiration in inspirations:
            inspiration_count += 1
            # replace time with a readable one and add to DB
            epoch_time_ms = long(inspiration.pop(mongodb_controller.TIME_CREATED))
            epoch_time = epoch_time_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
            inspiration[mongodb_controller.TIME_CREATED] = readable_time
            # add problem/schema id/text
            inspiration[mongodb_controller.PROBLEM_ID] = problem_id
            inspiration[mongodb_controller.SCHEMA_ID] = schema_id
            mongodb_controller.add_inspiration(inspiration)
        if inspiration_count > 0:
            mongodb_controller.update_inspiration_count(problem_id, inspiration_count)


def update_ideas_for_problem(problem_id):
    for inspiration_id in mongodb_controller.get_inspiration_ids(problem_id):
        idea_hit_id = mongodb_controller.get_idea_hit_id(inspiration_id)
        ideas = mturk_controller.get_idea_hit_results(idea_hit_id)
        if ideas == "FAIL":
            print "mturk_controller.get_idea_hit_results - FAIL!"
            return
        ideas_count = 0
        for idea in ideas:
            ideas_count += 1
            # replace time with a readable one and add to DB
            epoch_time_ms = long(idea.pop(mongodb_controller.TIME_CREATED))
            epoch_time = epoch_time_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(epoch_time).strftime(READABLE_TIME_FORMAT)
            idea[mongodb_controller.TIME_CREATED] = readable_time
            # add problem/schema id/text
            idea[mongodb_controller.PROBLEM_ID] = problem_id
            idea[mongodb_controller.INSPIRATION_ID] = inspiration_id
            mongodb_controller.add_idea(idea)
        if ideas_count > 0:
            mongodb_controller.update_idea_count(problem_id, ideas_count)


class SaveNewProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        [owner_username, title, description, schema_count_goal] = get_problem_parameters()
        if schema_count_goal == -1:
            return {"success": False}
        temp_id = ''.join(random.sample(string.hexdigits, 8))
        time_created = datetime.datetime.now().strftime(READABLE_TIME_FORMAT)
        mongodb_controller.save_problem(temp_id, title, description, owner_username, schema_count_goal, time_created)
        return {
            "success": True,
            "url": "problems"
        }


def get_problem_parameters():
    if USERNAME_KEY not in cherrypy.session:
        raise cherrypy.HTTPError(403)
    owner_username = cherrypy.session[USERNAME_KEY]
    data = cherrypy.request.json
    title = data["title"]
    description = data["description"]

    schema_count_goal = data["schema_count_goal"]

    return owner_username, title, description, schema_count_goal


def convert_input_count(user_input):
    if not isinstance(user_input, int):
        try:
            schema_count_goal = int(user_input)
        except ValueError:
            print "Casting fail!!!"
            schema_count_goal = -1
    return schema_count_goal


class PostNewProblemHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        [owner_username, title, description, schema_count_goal] = get_problem_parameters()
        if schema_count_goal == -1:
            return {"success": False}

        hit_id = mturk_controller.create_schema_making_hit(description, schema_count_goal)
        if hit_id == "FAIL":
            return {"success": False}

        time_created = datetime.datetime.now().strftime(READABLE_TIME_FORMAT)
        mongodb_controller.save_problem(hit_id, title, description, owner_username, schema_count_goal, time_created)
        mongodb_controller.set_schema_stage(hit_id=hit_id)
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
        return publish_problem(data[PROBLEM_ID])


def publish_problem(temp_problem_id):
    description = mongodb_controller.get_problem_text(temp_problem_id)
    schema_count_goal = mongodb_controller.get_schema_count_goal(temp_problem_id)
    hit_id = mturk_controller.create_schema_making_hit(description, schema_count_goal)
    if hit_id == "FAIL":
        return {"success": False}
    mongodb_controller.set_schema_stage(temporary_id=temp_problem_id, hit_id=hit_id)
    return {"success": True, "new_id": hit_id}


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
        for schema in mongodb_controller.get_schemas(problem_id):
            hit_id = mturk_controller.create_inspiration_hit(schema[mongodb_controller.SCHEMA_TEXT], count_goal)
            if hit_id == "FAIL":
                print "create_inspiration_hit FAILED!! dunno how to handle"
                continue
            mongodb_controller.add_inspiration_hit_id_to_schema(hit_id, schema[mongodb_controller.SCHEMA_ID])
        mongodb_controller.set_inspiration_stage(problem_id, count_goal)
        return {"success": True,
                "url": "problems"}


class ProblemEditHandler(object):
    exposed = True

    @cherrypy.tools.json_in()
    def POST(self):
        if USERNAME_KEY not in cherrypy.session:
            raise cherrypy.HTTPError(403)
        data = cherrypy.request.json
        if not mongodb_controller.does_user_have_problem_with_id(cherrypy.session[USERNAME_KEY], data[PROBLEM_ID]):
            raise cherrypy.HTTPError(403)
        mongodb_controller.edit_problem(data)


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

        for inspiration in mongodb_controller.get_inspirations(problem_id):
            problem_text = mongodb_controller.get_problem_text(inspiration[PROBLEM_ID])
            link = inspiration[mongodb_controller.INSPIRATION_LINK]
            explanation = inspiration[mongodb_controller.INSPIRATION_REASON]

            hit_id = mturk_controller.create_idea_hit(problem_text, link, explanation, count_goal)
            # add the hit_id to schema
            if hit_id == "FAIL":
                print "create_idea_hit FAILED!! dunno how to handle"
                continue
            mongodb_controller.add_idea_hit_id_to_inspiration(hit_id, inspiration[mongodb_controller.INSPIRATION_ID])
        mongodb_controller.set_idea_stage(problem_id, count_goal)
        return {"success": True,
                "url": "problems"}


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
