import cherrypy
import mongodb_controller
from constants import *
from dateutil.tz import tzlocal
import re
import random
import string


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


def check_if_logged_in():
    if USERNAME_KEY not in cherrypy.session:
        raise cherrypy.HTTPError(403)
    else:
        return cherrypy.session[USERNAME_KEY]


def convert_input_count(user_input):
    if not isinstance(user_input, int):
        try:
            count = int(user_input)
        except ValueError:
            print "Casting fail! Input:", user_input
            count = -1
    else:
        count = user_input
    return count


def make_links_list(slug, problem_id):
    schemas_page_link = SCHEMAS_LINK_FORMAT.format(slug)
    inspirations_page_link = INSPIRATIONS_LINK_FORMAT.format(slug)
    ideas_page_link = IDEAS_LINK_FORMAT.format(slug)
    suggestions_page_link = SUGGESTIONS_LINK_FORMAT.format(slug)
    stage = mongodb_controller.get_stage(problem_id)
    if stage == mongodb_controller.STAGE_SUGGESTION:
        return schemas_page_link, inspirations_page_link, ideas_page_link, suggestions_page_link
    suggestions_page_link = ""
    if stage != mongodb_controller.STAGE_IDEA:
        ideas_page_link = ""
    elif stage != mongodb_controller.STAGE_INSPIRATION:
        inspirations_page_link = ""
    return schemas_page_link, inspirations_page_link, ideas_page_link, suggestions_page_link


def convert_object_id_to_readable_time(object_id):
    utc_time = object_id.generation_time
    local_tz = tzlocal()
    return utc_time.astimezone(local_tz).strftime(READABLE_TIME_FORMAT)


def slugify(s):
    s = s.lower()
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')
    s = re.sub('\W', '', s)
    s = s.replace('_', ' ')
    s = re.sub('\s+', ' ', s)
    s = s.strip()
    s = s.replace(' ', '-')
    return s


def get_input_problem_dict():
    data = cherrypy.request.json
    return {
        OWNER_USERNAME: cherrypy.session[USERNAME_KEY],
        TITLE: data[TITLE],
        DESCRIPTION: data[DESCRIPTION],
        SCHEMA_ASSIGNMENTS_NUM: convert_input_count(data[SCHEMA_ASSIGNMENTS_NUM]),
        LAZY: data[LAZY],
        PROBLEM_ID: data[PROBLEM_ID]
    }


def generate_id():
    return ''.join(random.sample(string.hexdigits, 8))
