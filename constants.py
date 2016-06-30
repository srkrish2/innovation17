# format example: 23 Apr 2012 4:00 PM
READABLE_TIME_FORMAT = "%d %b %Y %I:%M %p"
USERNAME_KEY = "username"
PREVIOUS_URL_KEY = "previous_url"
HOW_MANY_RANKS = 1
MIN_RANK = 1
HOW_MANY_SCHEMAS = 1
HOW_MANY_INSPIRATIONS = 1
HOW_MANY_IDEAS = 1
PERIOD = 20

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
TIME_CREATED = "time_created"
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
RANK = "rank"
# }

# RANK_SCHEMA_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# SCHEMA_ID
# }

# SCHEMA_RANK: {
RANK_ID = "rank_id"
# RANK
# TIME_CREATED
# WORKER_ID
# SCHEMA_ID
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
# RANK
# }

# RANK_INSPIRATION_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# INSPIRATION_ID
# }

# INSPIRATION_RANK: {
# RANK_ID
# RANK
# TIME_CREATED
# WORKER_ID
# SCHEMA_ID
# }

# IDEA_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# PROBLEM_ID
# SCHEMA_ID
# INSPIRATION_ID
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
# RANK
# }

# RANK_IDEA_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# INSPIRATION_ID
# }

# RANK_IDEA_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# IDEA_ID
# }

# IDEA_RANK: {
# RANK_ID
# RANK
# TIME_CREATED
# WORKER_ID
# SCHEMA_ID
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
# RANK
# }

# RANK_SUGGESTION_HIT: {
# HIT_ID
# COUNT
# COUNT_GOAL
# IDEA_ID
# }

# SUGGESTION_RANK: {
# RANK_ID
# RANK
# TIME_CREATED
# WORKER_ID
# SCHEMA_ID
# }

# USER: {
USER_USERNAME = "username"
USER_EMAIL = "email"
USER_PASSWORD = "password"
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
