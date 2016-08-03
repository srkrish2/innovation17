import cherrypy
from constants import *
import mongodb_controller as mc
from jinja2 import Environment, PackageLoader
from utility_functions import check_problem_access, make_links_list, convert_object_id_to_readable_time
import well_ranked_counters
import abc
import datetime

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
        problem[SCHEMA_COUNT] = counter.get_count(problem[PROBLEM_ID])
        counter = well_ranked_counters.WellRankedInspirationCounter()
        problem[INSPIRATION_COUNT] = counter.get_count(problem[PROBLEM_ID])
        counter = well_ranked_counters.WellRankedIdeaCounter()
        problem[IDEA_COUNT] = counter.get_count(problem[PROBLEM_ID])
        counter = well_ranked_counters.WellRankedSuggestionCounter()
        problem[SUGGESTION_COUNT] = counter.get_count(problem[PROBLEM_ID])

        # add links
        problem[EDIT_PAGE_LINK] = EDIT_LINK_FORMAT.format(problem[SLUG])
        problem[SCHEMAS_PAGE_LINK] = SCHEMAS_LINK_FORMAT.format(problem[SLUG])
        problem[IDEAS_PAGE_LINK] = IDEAS_LINK_FORMAT.format(problem[SLUG])
        problem[INSPIRATIONS_PAGE_LINK] = INSPIRATIONS_LINK_FORMAT.format(problem[SLUG])
        problem[SUGGESTIONS_PAGE_LINK] = SUGGESTIONS_LINK_FORMAT.format(problem[SLUG])
        problem[VIEW_PAGE_LINK] = VIEW_LINK_FORMAT.format(problem[SLUG])

        problem[TIME_CREATED] = convert_object_id_to_readable_time(problem["_id"])
        problems.append(problem)
    template = env.get_template('problems.html')
    return template.render(problems=problems)


def render_schemas_page(problem_slug):
    renderer = SchemasPageRenderer(problem_slug)
    return renderer.render()


def render_inspirations_page(problem_slug):
    renderer = InspirationsPageRenderer(problem_slug)
    return renderer.render()


def render_ideas_page(problem_slug):
    renderer = IdeasPageRenderer(problem_slug)
    return renderer.render()


def render_suggestions_page(problem_slug):
    renderer = SuggestionsPageRenderer(problem_slug)
    return renderer.render()


class StagePageRenderer(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, problem_slug):
        self.problem_slug = problem_slug

    @abc.abstractmethod
    def get_template_filename(self):
        return

    @abc.abstractmethod
    def get_items(self, problem_id):
        return

    def render(self):
        if check_problem_access(self.problem_slug) is True:
            problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], self.problem_slug)
            items = self.get_items(problem_id)
            template = env.get_template(self.get_template_filename())
            [schemas_link, insps_link, ideas_link, suggs_link] = make_links_list(self.problem_slug, problem_id)
            return template.render(items=items, problem_id=problem_id,
                                   problem_stage=mc.get_stage(problem_id),
                                   schemas_page_link=schemas_link, inspirations_page_link=insps_link,
                                   ideas_page_link=ideas_link, suggestions_page_link=suggs_link)


class SchemasPageRenderer(StagePageRenderer):

    def get_template_filename(self):
        return 'schemas.html'

    def get_items(self, problem_id):
        return list(mc.get_well_ranked_schemas(problem_id))


class InspirationsPageRenderer(StagePageRenderer):

    def get_template_filename(self):
        return 'inspirations_card.html'

    def get_items(self, problem_id):
        if HOW_MANY_INSPIRATION_RANKS > 0:
            inspiration_dicts = list(mc.get_well_ranked_inspirations(problem_id))
        else:
            inspiration_dicts = list(mc.get_inspirations(problem_id))
        for inspiration in inspiration_dicts:
            problem_text = mc.get_problem_description(problem_id)
            try:
                schema_text = mc.get_schema_text(inspiration[SCHEMA_ID])
            except:
                schema_text = "no_schema"
            inspiration[SCHEMA_TEXT_FIELD] = schema_text
            inspiration[PROBLEM_TEXT_FIELD] = problem_text
        return inspiration_dicts


class IdeasPageRenderer(StagePageRenderer):

    def get_template_filename(self):
        return 'ideas.html'

    def get_items(self, problem_id):
        if HOW_MANY_IDEA_RANKS > 0:
            idea_dicts = list(mc.get_well_ranked_ideas(problem_id))
        else:
            idea_dicts = list(mc.get_ideas(problem_id))
        for idea in idea_dicts:
            problem_text = mc.get_problem_description(problem_id)
            inspiration_id = idea[mc.INSPIRATION_ID]
            schema_text = mc.get_schema_text_from_inspiration(inspiration_id)
            inspiration_summary = mc.get_inspiration_summary(inspiration_id)
            idea[PROBLEM_TEXT_FIELD] = problem_text
            idea[SCHEMA_TEXT_FIELD] = schema_text
            idea[INSPIRATION_TEXT_FIELD] = inspiration_summary
            idea[FEEDBACKS_NUM] = len(list(mc.get_feedback_dicts(idea[IDEA_ID])))
        return idea_dicts


class SuggestionsPageRenderer(StagePageRenderer):

    def get_template_filename(self):
        return 'suggestions.html'

    def get_items(self, problem_id):
        result = []
        if HOW_MANY_IDEA_RANKS > 0:
            idea_dicts = mc.get_well_ranked_ideas(problem_id)
        else:
            idea_dicts = mc.get_ideas(problem_id)
        for idea_dict in idea_dicts:
            idea_id = idea_dict[mc.IDEA_ID]
            idea = {
                mc.IDEA_ID: idea_id,
                TEXT: idea_dict[TEXT],
                FEEDBACKS_FIELD: get_feedbacks_with_suggestions(idea_id)
            }
            if len(idea[FEEDBACKS_FIELD]) > 0:
                result.append(idea)
        return result


def get_feedbacks_with_suggestions(idea_id):
    feedbacks_with_suggestions = []
    for feedback_dict in mc.get_feedback_dicts(idea_id):
        feedback_id = feedback_dict[mc.FEEDBACK_ID]
        if HOW_MANY_SUGGESTION_RANKS > 0:
            suggestions = list(mc.get_well_ranked_suggestions_for_feedback(feedback_id))
        else:
            suggestions = list(mc.get_suggestions_for_feedback(feedback_id))
        feedback_dict[SUGGESTIONS_FIELD] = suggestions
        if len(suggestions) > 0:
            feedbacks_with_suggestions.append(feedback_dict)
    return feedbacks_with_suggestions


def render_edit_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        problem_dict = mc.get_problem_dict(problem_id)
        template = env.get_template('new_problem.html')
        print "lazy is", problem_dict[LAZY]
        return template.render(count_goal=problem_dict[SCHEMA_ASSIGNMENTS_NUM], problem_id=problem_id,
                               title=problem_dict[TITLE], operation="edit", description=problem_dict[mc.DESCRIPTION],
                               lazy=problem_dict[LAZY])


def render_view_page(problem_slug):
    if check_problem_access(problem_slug) is True:
        problem_id = mc.get_problem_id(cherrypy.session[USERNAME_KEY], problem_slug)
        problem_dict = mc.get_problem_dict(problem_id)
        template = env.get_template('new_problem.html')
        return template.render(count_goal=problem_dict[SCHEMA_ASSIGNMENTS_NUM], problem_id=problem_id,
                               operation="view", title=problem_dict[TITLE], description=problem_dict[mc.DESCRIPTION],
                               lazy=problem_dict[LAZY])


def render_new_problem():
    template = env.get_template('new_problem.html')
    return template.render()


def render_account_edit_page():
    template = env.get_template('account_edit.html')
    return template.render()


def render_profile():
    template = env.get_template('profile_info.html')
    return template.render()


def render_schema1(language, worker_id):
    if PROBLEM1 in cherrypy.session:
        raise cherrypy.HTTPError(403)
    if language == ENGLISH:
        problem_dict = mc.find_problem({})
        problem_id = problem_dict[PROBLEM_ID]
        problem = problem_dict[DESCRIPTION]
    else:
        translation_dict = mc.find_translation({LANGUAGE: language, APPROVED: True})
        problem_id = translation_dict[PROBLEM_ID]
        problem = translation_dict[IMPROVED]

    cherrypy.session[ACCEPT_TIME] = datetime.datetime.now()
    cherrypy.session[PROBLEM1] = problem_id
    cherrypy.session[WORKER_ID] = worker_id
    cherrypy.session[LANGUAGE] = language

    filename = "generate_schema1_{}.html".format(language)
    template = env.get_template(filename)
    return template.render(problem=problem, problem_id=problem_id, worker_id=worker_id)


def render_schema2():
    if PROBLEM2 in cherrypy.session:
        raise cherrypy.HTTPError(403)
    language = cherrypy.session[LANGUAGE]
    problem1 = cherrypy.session[PROBLEM1]
    worker_id = cherrypy.session[WORKER_ID]
    if language == ENGLISH:
        problem_dict = mc.find_problem({PROBLEM_ID: {"$ne": problem1}})
        problem_id = problem_dict[PROBLEM_ID]
        problem = problem_dict[DESCRIPTION]
    else:
        translation_dict = mc.find_translation({LANGUAGE: language, APPROVED: True, PROBLEM_ID: {"$ne": problem1}})
        problem_id = translation_dict[PROBLEM_ID]
        problem = translation_dict[IMPROVED]

    cherrypy.session[ACCEPT_TIME] = datetime.datetime.now()
    cherrypy.session[PROBLEM2] = problem_id

    filename = "generate_schema2_{}.html".format(language)
    template = env.get_template(filename)
    return template.render(problem=problem, problem_id=problem_id,  worker_id=worker_id)


def render_survey():
    # print str(dict(cherrypy.session))
    if WORKER_ID not in cherrypy.session:
        raise cherrypy.HTTPError(403)
    language = cherrypy.session[LANGUAGE]
    worker_id = cherrypy.session[WORKER_ID]

    filename = "survey_{}.html".format(language)
    template = env.get_template(filename)
    return template.render(worker_id=worker_id)


def render_inspiration(language, worker_id, no_schema):
    if no_schema:
        translation_dict = mc.find_translation({
            LANGUAGE: language, APPROVED: True, NS_USE_COUNT: {"$lt": NS_USE_LIMIT}
        })
        mc.update_translation({TRANSLATION_ID: translation_dict[TRANSLATION_ID]}, {"$inc": {NS_USE_COUNT: 1}})
        problem_id = translation_dict[PROBLEM_ID]
        problem = translation_dict[IMPROVED]
    else:
        schema_dict = mc.find_schema({
            LANGUAGE: language, INSPIRED_NUM: {"$lt": HOW_MANY_INSPIRATIONS_PER_SCHEMA}
        })
        mc.update_schema({SCHEMA_ID: schema_dict[SCHEMA_ID]}, {"$inc": {INSPIRED_NUM: 1}})
        problem_id = schema_dict[PROBLEM_ID]
        problem = schema_dict[TEXT]
        cherrypy.session[SCHEMA_ID] = schema_dict[SCHEMA_ID]

    cherrypy.session[ACCEPT_TIME] = datetime.datetime.now()
    cherrypy.session[NO_SCHEMA] = True if no_schema else False
    cherrypy.session[LANGUAGE] = language
    cherrypy.session[PROBLEM_ID] = problem_id
    cherrypy.session[WORKER_ID] = worker_id

    filename = 'generate_inspiration_{}.html'.format(language)
    template = env.get_template(filename)
    return template.render(problem=problem, problem_id=problem_id, worker_id=worker_id)


def render_idea():
    cherrypy.session[ACCEPT_TIME] = datetime.datetime.now()
    language = cherrypy.session[LANGUAGE]
    worker_id = cherrypy.session[WORKER_ID]
    no_schema = cherrypy.session[NO_SCHEMA]
    source_link = cherrypy.session[INSPIRATION_LINK]
    problem_id = cherrypy.session[PROBLEM_ID]
    ns_suffix = "ns_" if no_schema else ""
    if language == ENGLISH:
        problem = mc.get_problem_description(problem_id)
    else:
        translation_dict = mc.find_translation({
            LANGUAGE: language, APPROVED: True, PROBLEM_ID: problem_id
        })
        problem = translation_dict[IMPROVED]
    filename = 'generate_{}idea_{}.html'.format(ns_suffix, language)
    template = env.get_template(filename)
    return template.render(problem=problem, source_link=source_link,
                           problem_id=problem_id, worker_id=worker_id)


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
