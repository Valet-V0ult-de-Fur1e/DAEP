#!/usr/bin/python
 # -*- coding: utf-8 -*-
from flask import Flask, send_file, request, redirect
from flask_cors import CORS, cross_origin
from infobase import makeStartData, makeFrontendConfig
from docxtpl import DocxTemplate
import os
import json

frontData = None
backData = None


def loadData():
    global frontData, backData
    if not os.path.exists('ibBackend.json'):
        makeStartData()
    if not os.path.exists('ibFrontend.json'):
        makeFrontendConfig()
    with open('ibBackend.json', 'r', encoding="utf-8") as fileBackendData:
        backData = json.load(fileBackendData)
    with open('ibFrontend.json', 'r', encoding="utf-8") as fileFrontendData:
        frontData = json.load(fileFrontendData)


def loadDataServer():
    with open("data_file.json", "r") as data_file_read:
        data = json.load(data_file_read)
    return data['files_count']


def saveDataServer():
    global programCount
    with open("data_file.json", "r") as data_file_read:
        data = json.load(data_file_read)
    data["files_count"] = programCount
    with open("data_file.json", "w") as data_file_write:
        json.dump(data, data_file_write)


loadData()
programCount = loadDataServer()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/constructor/get_mrt', methods=['GET', 'POST'])
def get_mrt():
    return send_file('Метод.рек.  Конструктор.docx')


@app.route('/constructor/get_programs_count')
def get_programs_count():
    with open("data_file.json", "r") as data_file_read:
        data = json.load(data_file_read)
    return data


@app.route('/get_ib_front')
@cross_origin()
def getIbFront():
    return send_file("ibFrontend.json")


@app.route('/get_ib_back')
@cross_origin()
def getIbBack():
    return send_file("ibBackend.json")


@app.route('/constructor/test_req', methods=['GET', 'POST'])
def test_req():
    pass


@app.route('/constructor/test', methods=['GET', 'POST'])
def make_program():
    try:
        global backData, programCount
        if os.path.exists(f'{programCount}.docx'):
            os.remove(f'{programCount}.docx')
        data_dict = {}

        for key, item in request.values.lists():
            data_dict[key] = item if key in ['en_form_edu', 'en_subject_taskss', 'en_metasubject_tasks', 'en_personal_tasks', 'en_metasubject_tasks_no', 'cop_material_support_1', 'cop_material_support_2'] else item[0]

        modules_dict = []
        subj_data_dict = []
        data_dict["cop_meta_result"] = []
        data_dict["cop_sub_result"] = []

        if data_dict["en_training_periodn"] == "36":

            if data_dict["en_duration_lesson_choice"] == "1":
                data_dict["en_duration_lesson"] = "1"
                data_dict["en_number_classes"] = "2"

            if data_dict["en_duration_lesson_choice"] == "2":
                data_dict["en_duration_lesson"] = "2"
                data_dict["en_number_classes"] = "1"

            if data_dict["en_duration_lesson_choice"] == "3":
                data_dict["en_duration_lesson"] = "1"
                data_dict["en_number_classes"] = "1"

        data_dict['cop_meta_result'] = ''
        data_dict['cop_sub_result'] = ''
        data_dict['cop_person_result'] = ''
        all_time = int(data_dict["en_training_periodn"]) * int(data_dict["en_duration_lesson"]) * int(data_dict["en_number_classes"]) // 18

        if len(data_dict['en_subject_taskss']) > 0:
            for item in data_dict['en_subject_taskss']:
                modules_dict.append({"name": item, "time": backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['subject_tasks'][item]['duration']})
                module = {
                    "module_name": backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['subject_tasks'][item]['module'],
                    "teori": backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['subject_tasks'][item]['theory'],
                    "practic": backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['subject_tasks'][item]['practice']
                }
                subj_data_dict.append(module)
                data_dict["cop_sub_result"] += backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['subject_tasks'][item]['result']

        if len(data_dict['en_metasubject_tasks']) > 0:
            for item in data_dict['en_metasubject_tasks']:
                if all_time >= len(data_dict['en_subject_taskss']) + 1:
                    modules_dict.append({"name": item, "time": backData['global_data']['metasubject_with_watch'][item]['duration']})
                module = {
                    "module_name": backData['global_data']['metasubject_with_watch'][item]['module'],
                    "teori": backData['global_data']['metasubject_with_watch'][item]['theory'],
                    "practic": backData['global_data']['metasubject_with_watch'][item]['practice']
                }
                subj_data_dict.append(module)
                data_dict["cop_meta_result"] += backData['global_data']['metasubject_with_watch'][item]['result']

        if len(data_dict['en_metasubject_tasks_no']) > 0:
            for item in data_dict['en_metasubject_tasks_no']:
                data_dict["cop_meta_result"] += backData['global_data']['metasubject'][item]['result']

        if len(data_dict['en_personal_tasks']) > 0:
            for item in data_dict['en_personal_tasks']:
                if item in backData['local_data'][data_dict['en_orientation']]['global']['person_tasks'].keys():
                    data_dict['cop_person_result'] += backData['local_data'][data_dict['en_orientation']]['global']['person_tasks'][item]
                if item in backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['person_tasks'].keys():
                    data_dict['cop_person_result'] += backData['local_data'][data_dict['en_orientation']]['local'][data_dict['en_type_activity']]['person_tasks'][item]

        data_dict['modules'] = modules_dict
        data_dict['plan_list'] = subj_data_dict
        docFileOut = DocxTemplate("cshablonv6.docx")
        docFileOut.render(data_dict)
        programCount += 1
        saveDataServer()
        programName = f'{programCount}.docx'
        docFileOut.save(programName)
        return send_file(programName)
    except BaseException as e:
        return {}


@app.errorhandler(404)
def page_not_found(err):
    return redirect("https://obr-khv.ru{}".format(request.path))
