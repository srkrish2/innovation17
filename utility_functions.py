import cherrypy
import mongodb_controller
from constants import USERNAME_KEY, PREVIOUS_URL_KEY


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
    else:
        schema_count_goal = user_input
    return schema_count_goal


def make_links_list(slug, problem_id):
    schemas_page_link = "/{}/schemas".format(slug)
    inspirations_page_link = "/{}/inspirations".format(slug)
    ideas_page_link = "/{}/ideas".format(slug)
    stage = mongodb_controller.get_stage(problem_id)
    if stage == mongodb_controller.STAGE_SUGGESTION:
        return schemas_page_link, inspirations_page_link, ideas_page_link
    if stage != mongodb_controller.STAGE_IDEA:
        ideas_page_link = ""
    elif stage != mongodb_controller.STAGE_INSPIRATION:
        inspirations_page_link = ""
    return schemas_page_link, inspirations_page_link, ideas_page_link