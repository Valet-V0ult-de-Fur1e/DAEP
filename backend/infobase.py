#!/usr/bin/python
 # -*- coding: utf-8 -*-
import json
from ibStartData import *


def makeFrontendConfig():
    with open("ibBackend.json", mode='rb') as IBDataBackend_file:
        ibFrontend = {
            "local_data": {},
            "global_data": {
                "metasubject_with_watch": ["Сформировать начальные умения в проектной деятельности", "Научить основам исследовательской деятельности"],
                "metasubject": ["Научить основам кооперации", "Развить коммуникативные навыки"],
                "provision": ["компьютер", "проектор", "флип-чарт", "доска", "звуковое оборудование (усилитель, микрофоны, наушники)"]
            }
        }
        IBDataBackend = json.load(IBDataBackend_file)
        for direction, type_of_activity_dict in IBDataBackend['local_data'].items():
            ibFrontend["local_data"][direction] = {
                'subjects':{},
                'person': list(type_of_activity_dict['global']['person_tasks'].keys()),
                'equipment': type_of_activity_dict['global']['equipment']
            }
            for type_of_activity, type_of_activity_data in type_of_activity_dict['local'].items():
                ibFrontend["local_data"][direction]['subjects'][type_of_activity] = {
                    'subject': list(type_of_activity_data['subject_tasks'].keys()),
                    'equipment': type_of_activity_data['equipment'],
                    'person': list(type_of_activity_data['person_tasks'].keys())
                }
        with open("ibFrontend.json", mode='w', encoding="utf-8") as readFile:
            json.dump(ibFrontend, readFile, ensure_ascii=False)


def makeBackendConfig():
    with open(baseConfigFileName, mode='rb') as readFile:
        ibBackend = json.load(readFile)
        for direction, type_of_activity_dict in idb_v1.items():
            ibBackend['local_data'][direction] = {
                "local":{},
                "global":{
                    "equipment":[],
                    "person_tasks":{}
                }
            }
            for type_of_activity, subject_tasks_list in type_of_activity_dict.items():
                ibBackend['local_data'][direction]['local'][type_of_activity] = {
                    "subject_tasks": {},
                    "equipment":[],
                    "person_tasks":{}
                }
                for subject_task in subject_tasks_list:
                    ibBackend['local_data'][direction]['local'][type_of_activity]["subject_tasks"][subject_task] = {
                        "duration": 18,
                        "module": quest_data_dict[subject_task]['module_name'],
                        "theory": quest_data_dict[subject_task]['teori'],
                        "practice": quest_data_dict[subject_task]['practic'],
                        "result": result_dict[subject_task]
                    }
        with open('ibBackend.json', mode='w', encoding="utf-8") as write_file:
            json.dump(ibBackend, write_file,ensure_ascii=False)


def makeStartData():
    makeBackendConfig()
    makeFrontendConfig()


makeStartData()