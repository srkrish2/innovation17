# format example: 23 Apr 2012 4:00 PM
READABLE_TIME_FORMAT = "%d %b %Y %I:%M %p"
TIME_CREATED = "time_created"
USERNAME_KEY = "username"
PREVIOUS_URL_KEY = "previous_url"

# ranking settings.
# the following define how many turkers to ask to rank an item
# to disable ranking for a stage, set the constant to 0 (so we won't post rank hit and won't filter anything by rank)
HOW_MANY_SCHEMA_RANKS = 3
HOW_MANY_INSPIRATION_RANKS = 2
HOW_MANY_IDEA_RANKS = 0  # don't change this before adding supporting code :)
HOW_MANY_SUGGESTION_RANKS = 2

# HIT evaluation details - don't change these if you're just trying to switch ranking on/off
HOW_MANY_SCHEMAS_IN_ONE_RANK_HIT = 3
HOW_MANY_SUGGESTIONS_IN_ONE_RANK_HIT = 3
MIN_CATEGORY_RANK = 1

# Lazy mode settings. Since lazy users don't choose how many schemas/inspiration/ideas to get, we define that here.
HOW_MANY_SCHEMAS = HOW_MANY_SCHEMAS_IN_ONE_RANK_HIT  # how many schemas for each problem
HOW_MANY_INSPIRATIONS = 1  # how many inspirations for each schema
HOW_MANY_IDEAS = 1  # how many ideas for each inspiration
PERIOD = 10  # how often to check mturk for updates, in seconds.

EDIT_LINK_FORMAT = "/problem/{}/edit"
SCHEMAS_LINK_FORMAT = "/problem/{}/schemas"
IDEAS_LINK_FORMAT = "/problem/{}/ideas"
INSPIRATIONS_LINK_FORMAT = "/problem/{}/inspirations"
VIEW_LINK_FORMAT = "/problem/{}/view"
SUGGESTIONS_LINK_FORMAT = "/problem/{}/suggestions"

SCHEMA_COUNT = "schema_count"
INSPIRATION_COUNT = "inspiration_count"
IDEA_COUNT = "idea_count"
SUGGESTION_COUNT = "suggestion_count"

EDIT_PAGE_LINK = "edit_page_link"
VIEW_PAGE_LINK = "view_page_link"
SCHEMAS_PAGE_LINK = "schemas_page_link"
INSPIRATIONS_PAGE_LINK = "inspirations_page_link"
IDEAS_PAGE_LINK = "ideas_page_link"
SUGGESTIONS_PAGE_LINK = "suggestions_page_link"

FEEDBACKS_FIELD = "feedbacks"
SUGGESTIONS_FIELD = "suggestions"
IDEAS_FIELD = "ideas"
FEEDBACKS_NUM = "feedbacks_num"

PROBLEM_TEXT_FIELD = "problem_text"
SCHEMA_TEXT_FIELD = "schema_text"
INSPIRATION_TEXT_FIELD = "inspiration_text"

RANKS_FIELD = "ranks"

RESTART = "RESTART"
FAIL = "FAIL"
SUCCESS = "SUCCESS"

###################################################################
############################ DATABASE #############################
###################################################################


# PROBLEM: {
TITLE = "title"
DESCRIPTION = "description"
STAGE = "stage"
OWNER_USERNAME = "owner_username"
SLUG = "slug"
PROBLEM_ID = "problem_id"
SCHEMA_ASSIGNMENTS_NUM = "schema_assignments_num"
LAZY = "lazy"
# }

# SCHEMA_HIT: {
HIT_ID = "hit_id"
COUNT = "count"
COUNT_GOAL = "count_goal"
# PROBLEM_ID
# }

# SCHEMA: {
TEXT = "text"
SCHEMA_ID = "schema_id"
WORKER_ID = "worker_id"
STATUS = "status"
# TIME_CREATED
# PROBLEM_ID
WELL_RANKED = "well_ranked"
POSTED_FOR_RANK = "posted_for_rank"
# }

# RANK_SCHEMA_HIT: {
# HIT_ID
SUBMITTED_BY_WORKER = "submitted_by_worker"
SCHEMA_IDS = "schema_ids"
# PROBLEM_ID
# }

# SCHEMA_RANK: {
RANK_ID = "rank_id"
CATEGORY1 = "category1"
CATEGORY2 = "category2"
# TIME_CREATED
# WORKER_ID
# SCHEMA_ID
# PROBLEM_ID
# }

# INSPIRATION_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# PROBLEM_ID
# SCHEMA_ID
# }

# INSPIRATION: {
INSPIRATION_LINK = "source_link"
INSPIRATION_ADDITIONAL = "image_link"
INSPIRATION_SUMMARY = "summary"
INSPIRATION_REASON = "reason"
INSPIRATION_ID = "inspiration_id"
# SCHEMA_ID
# TIME_CREATED
# WORKER_ID
# STATUS
# PROBLEM_ID
# POSTED_FOR_RANK
# WELL_RANKED
# }

# RANK_INSPIRATION_HIT: {
# HIT_ID
# INSPIRATION_ID
# SUBMITTED
# PROBLEM_ID
# }

# INSPIRATION_RANK: {
# RANK_ID
RANK = "rank"
# TIME_CREATED
# WORKER_ID
# INSPIRATION_ID
# }

# IDEA_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# PROBLEM_ID
# SCHEMA_ID
# INSPIRATION_ID
# POSTED_FOR_RANK
# WELL_RANKED
# }

# IDEA: {
# TEXT
IDEA_ID = "idea_id"
# TIME_CREATED
# SLUG
# WORKER_ID
# PROBLEM_ID
# SCHEMA_ID
# INSPIRATION_ID
# STATUS
# POSTED_FOR_RANK
# WELL_RANKED
# }

# FEEDBACK: {
# TEXT
FEEDBACK_ID = "feedback_id"
# IDEA_ID
# }

# SUGGESTION_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# FEEDBACK_ID
# PROBLEM_ID
# IDEA_ID
# }

# SUGGESTION: {
SUGGESTION_ID = "suggestion_id"
# TEXT
# TIME_CREATED
# WORKER_ID
# PROBLEM_ID
# FEEDBACK_ID
# IDEA_ID
# POSTED_FOR_RANK
# WELL_RANKED
# }

# RANK_SUGGESTION_HIT: {
# HIT_ID
SUGGESTION_IDS = "suggestion_ids"
# SUBMITTED_BY_WORKER
# PROBLEM_ID
# }

# SUGGESTION_RANK: {
# RANK_ID
# RANK
# TIME_CREATED
# WORKER_ID
# SUGGESTION_ID
# }

# USER: {
USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"
# }

# TRANSLATION: {
# PROBLEM_ID
TRANSLATION_ID = "translation_id"
LANGUAGE = "language"
DETAILS = "details"  #: {STEP: 1, TIME_CREATED: 1, WORKER_ID: 1, TEXT: 1},
STEP = "step"
INITIAL = "initial"
IMPROVED = "improved"
APPROVED = "approved"
# }


# FIELD CONSTANTS
STAGE_UNPUBLISHED = "unpublished"
STAGE_SCHEMA = "schema"
STAGE_INSPIRATION = "inspiration"
STAGE_IDEA = "idea"
STAGE_SUGGESTION = "suggestion"

STATUS_REJECTED = 0
STATUS_ACCEPTED = 1
STATUS_PROCESSED = 2
STATUS_NEW = 1



