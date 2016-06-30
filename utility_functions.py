import cherrypy
import mongodb_controller
from constants import *


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


def get_problem_parameters(no_count=False):
    if USERNAME_KEY not in cherrypy.session:
        raise cherrypy.HTTPError(403)
    owner_username = cherrypy.session[USERNAME_KEY]
    data = cherrypy.request.json
    title = data["title"]
    description = data["description"]
    if no_count:
        return owner_username, title, description
    schema_assignments_num = convert_input_count(data["schema_assignments_num"])
    return owner_username, title, description, schema_assignments_num


def convert_input_count(user_input):
    if not isinstance(user_input, int):
        try:
            count = int(user_input)
        except ValueError:
            print "Casting fail!!!"
            count = -1
    else:
        count = user_input
    return count


def make_links_list(slug, problem_id):
    schemas_page_link = SCHEMAS_LINK_FORMAT.format(slug)
    inspirations_page_link = INSPIRATIONS_LINK_FORMAT.format(slug)
    ideas_page_link = IDEAS_LINK_FORMAT.format(slug)
    stage = mongodb_controller.get_stage(problem_id)
    if stage == mongodb_controller.STAGE_SUGGESTION:
        return schemas_page_link, inspirations_page_link, ideas_page_link
    if stage != mongodb_controller.STAGE_IDEA:
        ideas_page_link = ""
    elif stage != mongodb_controller.STAGE_INSPIRATION:
        inspirations_page_link = ""
    return schemas_page_link, inspirations_page_link, ideas_page_link
