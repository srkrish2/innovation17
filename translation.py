import mongodb_controller as mc
from utility_functions import generate_id
import mturk_controller
from constants import *


def get_translation(problem_id, description, language):
    obtained_final_translation = False
    while not obtained_final_translation:
        obtained_final_translation = run_translation_stages(problem_id, description, language)
    print "TRANSLATED:", problem_id, "into", language


def run_translation_stages(problem_id, description, language):
    translation_id = generate_id()
    mturk_controller.post_translation_hit(description, FLAG_INITIAL, language)
    insert_new_translation_doc(problem_id, language, translation_id)
    result = None
    while result is None:
        result = mturk_controller.get_translation_result(hit_id)
    add_initial_translation(result, translation_id)

    initial = result[TEXT]
    mturk_controller.post_translation_hit(initial, FLAG_IMPROVE, language)
    result = None
    while result is None:
        result = mturk_controller.get_translation_result(hit_id)
    update_translation(result, translation_id, 1)

    improved = result[TEXT]
    mturk_controller.post_translation_hit(improved, FLAG_VERIFY, language)
    result = None
    while result is None:
        result = mturk_controller.get_translation_result(hit_id)
    approved = result[TEXT] == "YES"
    update_translation(result, translation_id, 2)
    return approved


def insert_new_translation_doc(problem_id, language, translation_id):
    doc = {
        PROBLEM_ID: problem_id,
        LANGUAGE: language,
        TRANSLATION_ID: translation_id,
        DETAILS: []
    }
    translations_collection.insert_one(doc)


def add_initial_translation(mturk_dict, translation_id):
    query = {
        TRANSLATION_ID: translation_id
    }
    doc = translations_collection.find_one(query)
    doc[DETAILS].append(
        {
            STEP: 0,
            TIME_CREATED: mturk_dict[TIME_CREATED],
            WORKER_ID: mturk_dict[WORKER_ID],
        }
    )
    doc[INITIAL] = mturk_dict[TEXT]
    translations_collection.update_one(query, {"$set": doc})


def add_improved_translation(mturk_dict, translation_id):
    query = {
        TRANSLATION_ID: translation_id
    }
    doc = translations_collection.find_one(query)
    doc[DETAILS].append(
        {
            STEP: 1,
            TIME_CREATED: mturk_dict[TIME_CREATED],
            WORKER_ID: mturk_dict[WORKER_ID],
        }
    )
    doc[IMPROVED] = mturk_dict[TEXT]
    translations_collection.update_one(query, {"$set": doc})


def add_translation_verification(mturk_dict, translation_id):
    query = {
        TRANSLATION_ID: translation_id
    }
    doc = translations_collection.find_one(query)
    doc[DETAILS].append(
        {
            STEP: 2,
            TIME_CREATED: mturk_dict[TIME_CREATED],
            WORKER_ID: mturk_dict[WORKER_ID],
        }
    )
    doc[APPROVED] = mturk_dict[TEXT] == "YES"
    translations_collection.update_one(query, {"$set": doc})


def render_upwork_page(language, stage, problem_id):
    languages = {"en": ENGLISH, "ru": RUSSIAN, "ch": CHINESE}
    stages = {"sc": SCHEMA, "in": INSPIRATION, "id": IDEA}
    try:
        language = languages[language]
        stage = stages[stage]
        if stage == SCHEMA:
            problem_translation = find_translation(problem_id, language)
        if stage == INSPIRATION:
            find_schema(problem_id, language)
        if stage == IDEA:
            find_inspiration(problem_id, language)
    except KeyError or TypeError:
        return "404 Page not found!"



import pymongo
# client
client = pymongo.MongoClient()
# database
db = client.chi_db
# collections
translations_collection = db.translations
# insert_new_translation_doc(123,"chinese",456)
# add_initial_translation({TIME_CREATED:1,WORKER_ID:7, TEXT:'initial'}, 456)
# add_improved_translation({TIME_CREATED:2,WORKER_ID:7, TEXT:'improved'}, 456)
add_translation_verification({TIME_CREATED:2,WORKER_ID:7, TEXT:'YES'}, 456)