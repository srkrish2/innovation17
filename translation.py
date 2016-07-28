import mongodb_controller as mc
from utility_functions import generate_id, convert_epoch_to_readable
import mturk_controller
from constants import *
import time
import datetime


def get_translation(problem_id, description, language):
    obtained_final_translation = False
    while not obtained_final_translation:
        obtained_final_translation = run_translation_stages(problem_id, description, language)
    print "TRANSLATED:", problem_id, "into", language


def run_translation_stages(problem_id, description, language):
    translation_id = generate_id()
    while True:
        hit_creator = mturk_controller.TranslationHITCreator(description, "", FLAG_INITIAL, language)
        hit_id = hit_creator.post()
        insert_new_translation_doc(problem_id, language, translation_id)
        result_puller = mturk_controller.GeneratedTranslations()
        result = result_puller.get_results(hit_id)
        while result is None:
            time.sleep(PERIOD)
            result = result_puller.get_results(hit_id)
        if result != FAIL and result != RESTART:
            break
    initial = add_initial_translation(result, translation_id)

    while True:
        hit_creator = mturk_controller.TranslationHITCreator(description, initial, FLAG_IMPROVE, language)
        hit_id = hit_creator.post()
        result = result_puller.get_results(hit_id)
        while result is None:
            time.sleep(PERIOD)
            result = result_puller.get_results(hit_id)
        if result != FAIL and result != RESTART:
            break
    improved = add_improved_translation(result, translation_id)

    while True:
        hit_creator = mturk_controller.TranslationHITCreator(description, improved, FLAG_VERIFY, language)
        hit_id = hit_creator.post()
        result = result_puller.get_results(hit_id)
        while result is None:
            time.sleep(PERIOD)
            result = result_puller.get_results(hit_id)
        if result != FAIL and result != RESTART:
            break
    approved = add_translation_verification(result, translation_id)
    return approved



    # if stage == SCHEMA:
    #     problem_translation = find_translation(problem_id, language)
    # if stage == INSPIRATION:
    #     find_schema(problem_id, language)
    # if stage == IDEA:
    #     find_inspiration(problem_id, language)


def insert_new_translation_doc(problem_id, language, translation_id):
    doc = {
        PROBLEM_ID: problem_id,
        LANGUAGE: language,
        TRANSLATION_ID: translation_id,
        DETAILS: []
    }
    mc.insert_translation(doc)


def add_initial_translation(mturk_dict, translation_id):
    query = {
        TRANSLATION_ID: translation_id
    }
    doc = mc.find_translation(query)
    doc[INITIAL] = mturk_dict.pop(ANSWERS)[0]
    mturk_dict[SUBMIT_TIME] = convert_epoch_to_readable(mturk_dict[SUBMIT_TIME])
    mturk_dict[ACCEPT_TIME] = convert_epoch_to_readable(mturk_dict[ACCEPT_TIME])
    mturk_dict[STEP] = 0
    doc[DETAILS].append(mturk_dict)
    mc.update_translation(query, doc)
    return doc[INITIAL]


def add_improved_translation(mturk_dict, translation_id):
    query = {
        TRANSLATION_ID: translation_id
    }
    doc = mc.find_translation(query)
    doc[IMPROVED] = mturk_dict.pop(ANSWERS)[0]
    mturk_dict[SUBMIT_TIME] = convert_epoch_to_readable(mturk_dict[SUBMIT_TIME])
    mturk_dict[ACCEPT_TIME] = convert_epoch_to_readable(mturk_dict[ACCEPT_TIME])
    mturk_dict[STEP] = 1
    doc[DETAILS].append(mturk_dict)
    mc.update_translation(query, doc)
    return doc[IMPROVED]


def add_translation_verification(mturk_dict, translation_id):
    query = {
        TRANSLATION_ID: translation_id
    }
    doc = mc.find_translation(query)
    answers = mturk_dict.pop(ANSWERS)
    mturk_dict[SUMMARY1] = answers[0]
    mturk_dict[SUMMARY2] = answers[1]
    doc[APPROVED] = answers[2] == "YES"

    mturk_dict[SUBMIT_TIME] = convert_epoch_to_readable(mturk_dict[SUBMIT_TIME])
    mturk_dict[ACCEPT_TIME] = convert_epoch_to_readable(mturk_dict[ACCEPT_TIME])
    mturk_dict[STEP] = 2
    doc[DETAILS].append(mturk_dict)
    mc.update_translation(query, doc)
    return doc[APPROVED]


def save_schema(data):
    schema = {
        TEXT: data[SCHEMA],
        SUMMARY: data[SUMMARY],
        SIMILAR: data[SIMILAR],
        WELL_RANKED: True,
        SCHEMA_ID: generate_id(),
        WORKER_ID: data[WORKER_ID],
        STATUS: 1,
        TIME_CREATED: datetime.datetime.now().strftime(READABLE_TIME_FORMAT),
        PROBLEM_ID: data[PROBLEM_ID]
    }
    mc.add_schema(schema)


# run_translation_stages(123,"wind noise description","russian")
