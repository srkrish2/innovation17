import cherrypy
from constants import *
import mongodb_controller as mc
from jinja2 import Environment, PackageLoader
from utility_functions import check_problem_access, make_links_list
env = Environment(loader=PackageLoader('renderers', '/templates'))


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
    problems = mc.get_problems_by_user(cherrypy.session[USERNAME_KEY])
    template = env.get_template('problems.html')
    return template.render(problems=problems)


def render_schemas_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        schemas = list(mc.get_well_ranked_schemas(problem_id))
        template = env.get_template('schemas.html')
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        return template.render(schemas=schemas, problem_id=problem_id,
                               problem_stage=mc.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_inspirations_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        inspirations = mc.get_inspirations(problem_id)
        template = env.get_template('inspirations_card.html')
        inspiration_dicts_list = []
        for inspiration in inspirations:
            problem_text = mc.get_problem_description(problem_id)
            schema_text = mc.get_schema_text(inspiration[mc.SCHEMA_ID])
            inspiration["problem_text"] = problem_text
            inspiration["schema_text"] = schema_text
            inspiration_dicts_list.append(inspiration)
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        return template.render(inspirations=inspiration_dicts_list, problem_id=problem_id,
                               problem_stage=mc.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_ideas_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        ideas = mc.get_ideas(problem_id)
        template = env.get_template('ideas.html')
        ideas_dicts_list = []
        for idea in ideas:
            problem_text = mc.get_problem_description(problem_id)
            inspiration_id = idea[mc.INSPIRATION_ID]
            schema_text = mc.get_schema_text_from_inspiration(inspiration_id)
            inspiration_summary = mc.get_inspiration_summary(inspiration_id)
            idea["problem_text"] = problem_text
            idea["schema_text"] = schema_text
            idea["inspiration_text"] = inspiration_summary
            idea[SUGGESTIONS_PAGE_LINK] = "/{}/suggestions".format(idea[mc.SLUG])
            ideas_dicts_list.append(idea)
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        return template.render(ideas=ideas_dicts_list, problem_id=problem_id,
                               problem_stage=mc.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_edit_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        [title, description, count_goal] = mc.get_problem_fields(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=count_goal, problem_id=problem_id, title=title,
                               operation="edit", description=description)


def render_view_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        [title, description, count_goal] = mc.get_problem_fields(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=count_goal, problem_id=problem_id, title=title,
                               operation="view", description=description)


def render_suggestions_page(idea_slug):
    idea_dict = mc.get_idea_dict_for_slug(idea_slug)
    idea_id = idea_dict[mc.IDEA_ID]
    feedbacks_with_suggestions = []
    for feedback_dict in mc.get_feedback_dicts(idea_id):
        feedback_id = feedback_dict[mc.FEEDBACK_ID]
        suggestions = []
        for suggestion in mc.get_suggestion_dicts(feedback_id):
            suggestions.append(suggestion)
        feedback_dict["suggestions"] = suggestions
        feedbacks_with_suggestions.append(feedback_dict)
    idea_text = idea_dict[mc.TEXT]
    problem_id = idea_dict[mc.PROBLEM_ID]
    template = env.get_template('suggestions.html')
    return template.render(feedbacks=feedbacks_with_suggestions, idea_id=idea_id, idea_text=idea_text,
                           problem_id=problem_id)


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
