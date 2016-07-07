import cherrypy
from constants import *
import mongodb_controller as mc
from jinja2 import Environment, PackageLoader
from utility_functions import check_problem_access, make_links_list, convert_object_id_to_readable_time
import well_ranked_counters
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
    db_problems = mc.get_problems_by_user(cherrypy.session[USERNAME_KEY])
    problems = []
    for problem in db_problems:
        # add counts
        counter = well_ranked_counters.WellRankedSchemaCounter()
        problem[SCHEMA_COUNT] = counter.get_count(problem[mc.PROBLEM_ID])
        counter = well_ranked_counters.WellRankedInspirationCounter()
        problem[INSPIRATION_COUNT] = counter.get_count(problem[mc.PROBLEM_ID])
        counter = well_ranked_counters.WellRankedIdeaCounter()
        problem[IDEA_COUNT] = counter.get_count(problem[mc.PROBLEM_ID])
        counter = well_ranked_counters.WellRankedSuggestionCounter()
        problem[SUGGESTION_COUNT] = counter.get_count(problem[mc.PROBLEM_ID])

        # add links
        problem[EDIT_PAGE_LINK] = EDIT_LINK_FORMAT.format(problem[mc.SLUG])
        problem[SCHEMAS_PAGE_LINK] = SCHEMAS_LINK_FORMAT.format(problem[mc.SLUG])
        problem[IDEAS_PAGE_LINK] = IDEAS_LINK_FORMAT.format(problem[mc.SLUG])
        problem[INSPIRATIONS_PAGE_LINK] = INSPIRATIONS_LINK_FORMAT.format(problem[mc.SLUG])
        problem[SUGGESTIONS_PAGE_LINK] = SUGGESTIONS_LINK_FORMAT.format(problem[mc.SLUG])
        problem[VIEW_PAGE_LINK] = VIEW_LINK_FORMAT.format(problem[mc.SLUG])

        problem[TIME_CREATED] = convert_object_id_to_readable_time(problem["_id"])
        problems.append(problem)
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
        inspiration_dicts = list(mc.get_well_ranked_inspirations(problem_id))
        for inspiration in inspiration_dicts:
            problem_text = mc.get_problem_description(problem_id)
            schema_text = mc.get_schema_text(inspiration[mc.SCHEMA_ID])
            inspiration[PROBLEM_TEXT_FIELD] = problem_text
            inspiration[SCHEMA_TEXT_FIELD] = schema_text
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        template = env.get_template('inspirations_card.html')
        return template.render(inspirations=inspiration_dicts, problem_id=problem_id,
                               problem_stage=mc.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_ideas_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        idea_dicts = list(mc.get_well_ranked_ideas(problem_id))
        for idea in idea_dicts:
            problem_text = mc.get_problem_description(problem_id)
            inspiration_id = idea[mc.INSPIRATION_ID]
            schema_text = mc.get_schema_text_from_inspiration(inspiration_id)
            inspiration_summary = mc.get_inspiration_summary(inspiration_id)
            idea[PROBLEM_TEXT_FIELD] = problem_text
            idea[SCHEMA_TEXT_FIELD] = schema_text
            idea[INSPIRATION_TEXT_FIELD] = inspiration_summary
            idea[FEEDBACKS_NUM] = len(list(mc.get_feedback_dicts(idea[IDEA_ID])))
            idea[SUGGESTIONS_PAGE_LINK] = SUGGESTIONS_FOR_IDEA_LINK_FORMAT.format(idea[mc.SLUG])
        [schemas_page_link, inspirations_page_link, ideas_page_link] = make_links_list(problem_slug, problem_id)
        template = env.get_template('ideas.html')
        return template.render(ideas=idea_dicts, problem_id=problem_id,
                               problem_stage=mc.get_stage(problem_id),
                               schemas_page_link=schemas_page_link, inspirations_page_link=inspirations_page_link,
                               ideas_page_link=ideas_page_link)


def render_edit_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        problem_dict = mc.get_problem_dict(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=problem_dict[mc.SCHEMA_ASSIGNMENTS_NUM], problem_id=problem_id,
                               title=problem_dict[mc.TITLE], operation="edit", description=problem_dict[mc.DESCRIPTION])


def render_view_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        problem_dict = mc.get_problem_dict(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=problem_dict[mc.SCHEMA_ASSIGNMENTS_NUM], problem_id=problem_id, operation="view",
                               title=problem_dict[mc.TITLE], description=problem_dict[mc.DESCRIPTION])


def render_suggestions_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        ideas = []
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        for idea_dict in mc.get_ideas(problem_id):
            idea_id = idea_dict[mc.IDEA_ID]
            idea = {
                mc.IDEA_ID: idea_id,
                mc.TEXT: idea_dict[mc.TEXT],
                FEEDBACKS_FIELD: get_feedbacks_with_suggestions(idea_id)
            }
            ideas.append(idea)
        template = env.get_template('suggestions.html')
        print 'this is render suggestion', ideas
        return template.render(ideas=ideas, problem_id=problem_id)


def render_suggestions_page_for_idea(idea_slug):
    if USERNAME_KEY not in cherrypy.session:
        raise cherrypy.HTTPRedirect("sign_in")
    idea_dict = mc.get_idea_dict_for_slug(idea_slug)
    idea_id = idea_dict[mc.IDEA_ID]
    feedbacks_with_suggestions = get_feedbacks_with_suggestions(idea_id)
    idea_text = idea_dict[mc.TEXT]
    problem_id = idea_dict[mc.PROBLEM_ID]
    template = env.get_template('suggestions_for_idea.html')
    return template.render(feedbacks=feedbacks_with_suggestions, idea_id=idea_id, idea_text=idea_text,
                           problem_id=problem_id)


def get_feedbacks_with_suggestions(idea_id):
    feedbacks_with_suggestions = []
    for feedback_dict in mc.get_feedback_dicts(idea_id):
        feedback_id = feedback_dict[mc.FEEDBACK_ID]
        suggestions = []
        for suggestion in mc.get_suggestions_for_feedback(feedback_id):
            suggestions.append(suggestion)
        feedback_dict[SUGGESTIONS_FIELD] = suggestions
        feedbacks_with_suggestions.append(feedback_dict)
    return feedbacks_with_suggestions


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
    if message is not None:
        return "404 Page not found! Message: {}".format(message)
    return "404 Page not found!"


def error_page_403(status, message, traceback, version):
    return "403 Forbidden! Message: {}".format(message)


def unanticipated_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        "<html><body>Sorry, an error occurred. Please contact the admin</body></html>"
    ]
