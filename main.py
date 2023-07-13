import requests
import json
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTabWidget,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QGridLayout,
    QListView, QMessageBox
)
from PyQt6.QtCore import QStringListModel
appData = {}
ibData = {}


class Persontasksview(QWidget):
    def __init__(self, path):
        super().__init__()
        self.data_path = path
        self.data = self.get_data()
        self.new_task_name = ''
        self.layout = QVBoxLayout()
        self.initUI()
        self.setLayout(self.layout)

    def get_data(self):
        link = self.data_path.split('_')
        if len(link) == 1:
            return ibData['local_data'][link[0]]['global']['person_tasks']
        else:
            return ibData['local_data'][link[0]]['local'][link[1]]['person_tasks']

    def initUI(self):
        data_view = QTabWidget()

        for task in self.data.keys():
            test_layout = QVBoxLayout()
            test_widget = QWidget()

            delete_button = QPushButton(f'Удалить {task}')
            delete_button.setObjectName(self.data_path + '_' + task)
            delete_button.clicked.connect(self.delete_task)
            test_layout.addWidget(delete_button)

            person_Text = QTextEdit(self.data[task])
            person_Text.setObjectName(self.data_path + '_' + task)
            person_Text.textChanged.connect(self.change_data)
            test_layout.addWidget(person_Text)
            test_widget.setLayout(test_layout)
            data_view.addTab(test_widget, task)
        add_new_widget = QWidget()
        add_new_layout = QVBoxLayout()

        add_new_name = QLineEdit()
        add_new_name.textChanged.connect(self.changed_new_name)
        add_new_button = QPushButton('Добавить новую задачу')
        add_new_button.clicked.connect(self.add_new_task)

        add_new_layout.addWidget(add_new_name)
        add_new_layout.addWidget(add_new_button)

        add_new_widget.setLayout(add_new_layout)
        data_view.addTab(add_new_widget, '+')

        self.layout.addWidget(data_view)

    def delete_task(self):
        sender = self.sender()
        link = sender.objectName().split('_')
        if len(link) == 2:
            ibData['local_data'][link[0]]['global']['person_tasks'].pop(link[1])
        else:
            ibData['local_data'][link[0]]['local'][link[1]]['person_tasks'].pop(link[2])
        self.updateapp()

    def add_new_task(self):
        link = self.data_path.split('_')
        if len(link) == 1:
            ibData['local_data'][link[0]]['global']['person_tasks'][self.new_task_name] = ''
        else:
            ibData['local_data'][link[0]]['local'][link[1]]['person_tasks'][self.new_task_name] = ''
        self.data = self.get_data()
        self.updateapp()

    def updateapp(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.initUI()

    def clear(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def changed_new_name(self):
        sender = self.sender()
        self.new_task_name = sender.text()

    def change_data(self):
        sender = self.sender()
        link = sender.objectName().split('_')
        print(link)
        if len(link) == 2:
            ibData['local_data'][link[0]]['global']['person_tasks'][link[1]] = sender.toPlainText()
        else:
            ibData['local_data'][link[0]]['local'][link[1]]['person_tasks'][link[2]] = sender.toPlainText()

    def closeEvent(self, event):
        self.close()


class Listview(QWidget):
    def __init__(self, path):
        super().__init__()
        self.data_path = path
        self.string_list = self.get_data_for_path()
        self.initUI()

    def get_data_for_path(self):
        global ibData
        link = self.data_path.split('_')
        if link[0] == 'global':
            return ibData['global_data']['provision']
        else:
            if len(link) == 2:
                return ibData["local_data"][link[-1]]['global']['equipment']
            if len(link) == 3:
                return ibData["local_data"][link[-2]]['local'][link[-1]]['equipment']

    def initUI(self):
        layout = QGridLayout()
        self.listview = QListView()
        self.stringlistmodel = QStringListModel()
        self.stringlistmodel.setStringList(self.string_list)
        self.listview.setModel(self.stringlistmodel)
        self.stringlistmodel.dataChanged.connect(self.save)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_kw)
        self.line_edit = QLineEdit()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_kw)

        layout.addWidget(self.listview, 0, 0)
        layout.addWidget(self.delete_button, 0, 1)
        layout.addWidget(self.line_edit, 1, 0)
        layout.addWidget(self.add_button, 1, 1)
        self.setLayout(layout)

    def add_kw(self):
        row = self.stringlistmodel.rowCount()
        kw = self.line_edit.text()
        self.stringlistmodel.insertRow(row)
        self.stringlistmodel.setData(self.stringlistmodel.index(row), kw)
        self.line_edit.setText("")

    def delete_kw(self):
        index = self.listview.currentIndex()
        self.stringlistmodel.removeRow(index.row())

    def save(self):
        global ibData
        self.string_list = self.stringlistmodel.stringList()
        link = self.data_path.split('_')
        new_data = [self.listview.model().data(self.listview.model().index(x, 0)) for x in range(self.listview.model().rowCount())]
        if link[0] == 'global':
            ibData['global_data']['provision'] = new_data
        else:
            if len(link) == 2:
                ibData["local_data"][link[-1]]['global']['equipment'] = new_data
            if len(link) == 3:
                ibData["local_data"][link[-2]]['local'][link[-1]]['equipment'] = new_data


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.list_p = None
        self.new_subject_task_name = ''
        self.new_type_activity_name = ''
        self.new_direction_name = ''
        self.new_metasubject_with_watch = ''
        self.new_metasubject = ''
        self.person_data_ = None
        self.load_ui()

    def load_ui(self):
        main_layout = QVBoxLayout()

        directions_list_name = QLabel('Направления')
        main_layout.addWidget(directions_list_name)

        directions_list = QTabWidget()
        for direction in ibData['local_data'].keys():

            direction_widget = QWidget()
            direction_widget.setObjectName(direction)
            direction_layout = QVBoxLayout()

            type_activities_list_name = QLabel('Виды активности')
            direction_layout.addWidget(type_activities_list_name)

            type_activities_list = QTabWidget()
            type_activities_list.setObjectName(direction)

            for type_activity in ibData['local_data'][direction]['local']:

                type_activity_widget = QWidget()
                type_activity_widget.setObjectName(type_activity)

                type_activity_layout = QVBoxLayout()
                subject_tasks_list_name = QLabel('Предметные задачи')
                type_activity_layout.addWidget(subject_tasks_list_name)

                subject_tasks_list = QTabWidget()
                subject_tasks_list.setObjectName(f'{direction}_{type_activity}')

                for subject_task in ibData['local_data'][direction]['local'][type_activity]['subject_tasks']:

                    subject_task_widget = QWidget()
                    subject_task_widget.setObjectName(f'{direction}_{type_activity}_{subject_task}')

                    subject_task_layout = QVBoxLayout()

                    module_edit_line_name = QLabel('Модуль')
                    subject_task_layout.addWidget(module_edit_line_name)

                    module_edit_line = QLineEdit(
                        ibData['local_data'][direction]['local'][type_activity]['subject_tasks'][subject_task]
                        ['module'])
                    module_edit_line.setObjectName(f'{direction}_{type_activity}_{subject_task}_module')
                    module_edit_line.textChanged.connect(self.change_subject_task_data)
                    subject_task_layout.addWidget(module_edit_line)

                    duration_edit_line_name = QLabel('Длительность программы в часах')
                    subject_task_layout.addWidget(duration_edit_line_name)

                    duration_edit_line = QLineEdit(
                        str(ibData['local_data'][direction]['local'][type_activity]['subject_tasks']
                            [subject_task]['duration']))
                    duration_edit_line.setObjectName(f'{direction}_{type_activity}_{subject_task}_duration')
                    duration_edit_line.textChanged.connect(self.change_subject_task_data)
                    subject_task_layout.addWidget(duration_edit_line)

                    theory_edit_line_name = QLabel('Теория')
                    subject_task_layout.addWidget(theory_edit_line_name)

                    theory_edit_line = QTextEdit(
                        ibData['local_data'][direction]['local'][type_activity]['subject_tasks']
                        [subject_task]['theory'])
                    theory_edit_line.setObjectName(f'{direction}_{type_activity}_{subject_task}_theory')
                    theory_edit_line.textChanged.connect(self.change_subject_task_data)
                    subject_task_layout.addWidget(theory_edit_line)

                    practice_edit_line_name = QLabel('Практика')
                    subject_task_layout.addWidget(practice_edit_line_name)

                    practice_edit_line = QTextEdit(
                        ibData['local_data'][direction]['local'][type_activity]['subject_tasks']
                        [subject_task]['practice'])
                    practice_edit_line.setObjectName(f'{direction}_{type_activity}_{subject_task}_practice')
                    practice_edit_line.textChanged.connect(self.change_subject_task_data)
                    subject_task_layout.addWidget(practice_edit_line)

                    result_edit_line_name = QLabel('Результат')
                    subject_task_layout.addWidget(result_edit_line_name)

                    result_edit_line = QTextEdit(
                        ibData['local_data'][direction]['local'][type_activity]['subject_tasks']
                        [subject_task]['result'])
                    result_edit_line.setObjectName(f'{direction}_{type_activity}_{subject_task}_result')
                    result_edit_line.textChanged.connect(self.change_subject_task_data)
                    subject_task_layout.addWidget(result_edit_line)

                    delete_subject_task_button = QPushButton(f'Удалить предметную задачу {subject_task}')
                    delete_subject_task_button.setObjectName(f'{direction}_{type_activity}_{subject_task}')
                    delete_subject_task_button.clicked.connect(self.delete_subject_task)
                    subject_task_layout.addWidget(delete_subject_task_button)

                    subject_task_widget.setLayout(subject_task_layout)

                    subject_tasks_list.addTab(subject_task_widget, subject_task)

                add_new_subject_task_tab_widget = QWidget()
                add_new_subject_task_tab_layuot = QVBoxLayout()

                name_new_subject_task = QLineEdit()
                name_new_subject_task.textChanged.connect(self.name_new_subject_task_changed)
                add_new_subject_task_tab_layuot.addWidget(name_new_subject_task)

                add_new_subject_task_tab_button = QPushButton('Добавить предметную задачу')
                add_new_subject_task_tab_button.setObjectName(f'{direction}_{type_activity}')
                add_new_subject_task_tab_button.clicked.connect(self.add_new_subject_task_event)
                add_new_subject_task_tab_layuot.addWidget(add_new_subject_task_tab_button)

                warning_messege = QLabel("Введите название новой предметной задачи.\nПосле нажатия на кнопку приложение перезагрузится!")
                add_new_subject_task_tab_layuot.addWidget(warning_messege)

                add_new_subject_task_tab_widget.setLayout(add_new_subject_task_tab_layuot)
                subject_tasks_list.addTab(add_new_subject_task_tab_widget, "+")

                type_activity_layout.addWidget(subject_tasks_list)

                delete_type_activity_button = QPushButton(f'Удалить вид деятельности {type_activity}')
                delete_type_activity_button.setObjectName(f'{direction}_{type_activity}')
                delete_type_activity_button.clicked.connect(self.delete_type_activity)
                type_activity_layout.addWidget(delete_type_activity_button)

                provision_button = QPushButton('Редактировать список оборудования')
                provision_button.setObjectName(f'local_{direction}_{type_activity}')
                provision_button.clicked.connect(self.open_provision_window)
                type_activity_layout.addWidget(provision_button)

                person_data = QPushButton('Редактировать Личностные задачи')
                person_data.setObjectName(f'{direction}_{type_activity}')
                person_data.clicked.connect(self.open_person_tasks)
                type_activity_layout.addWidget(person_data)

                type_activity_widget.setLayout(type_activity_layout)
                type_activities_list.addTab(type_activity_widget, type_activity)

            add_new_type_activity_tab_widget = QWidget()
            add_new_type_activity_tab_layuot = QVBoxLayout()

            name_new_type_activity = QLineEdit()
            name_new_type_activity.textChanged.connect(self.name_new_type_activity_changed)
            add_new_type_activity_tab_layuot.addWidget(name_new_type_activity)

            add_new_type_activity_tab_button = QPushButton('Добавить вид деятельности')
            add_new_type_activity_tab_button.setObjectName(direction)
            add_new_type_activity_tab_button.clicked.connect(self.add_type_activity_task_event)
            add_new_type_activity_tab_layuot.addWidget(add_new_type_activity_tab_button)

            warning_messege = QLabel(
                "Введите название нового вида деятельности.\nПосле нажатия на кнопку приложение перезагрузится!")
            add_new_type_activity_tab_layuot.addWidget(warning_messege)

            add_new_type_activity_tab_widget.setLayout(add_new_type_activity_tab_layuot)
            type_activities_list.addTab(add_new_type_activity_tab_widget, "+")
            direction_layout.addWidget(type_activities_list)

            delete_direction_button = QPushButton(f'Удалить направление {direction}')
            delete_direction_button.setObjectName(direction)
            delete_direction_button.clicked.connect(self.delete_direction)
            direction_layout.addWidget(delete_direction_button)

            provision_button = QPushButton('Редактировать список оборудования')
            provision_button.setObjectName(f'local_{direction}')
            provision_button.clicked.connect(self.open_provision_window)
            direction_layout.addWidget(provision_button)

            person_data = QPushButton('Редактировать Личностные задачи')
            person_data.setObjectName(direction)
            person_data.clicked.connect(self.open_person_tasks)
            direction_layout.addWidget(person_data)

            direction_widget.setLayout(direction_layout)
            directions_list.addTab(direction_widget, direction)

        add_new_direction_tab_widget = QWidget()
        add_new_direction_tab_layuot = QVBoxLayout()

        name_new_direction = QLineEdit()
        name_new_direction.textChanged.connect(self.name_new_direction_changed)
        add_new_direction_tab_layuot.addWidget(name_new_direction)

        add_new_direction_tab_button = QPushButton('Добавить направление')
        add_new_direction_tab_button.clicked.connect(self.add_direction_task_event)
        add_new_direction_tab_layuot.addWidget(add_new_direction_tab_button)

        warning_messege = QLabel(
            "Введите название нового направления.\nПосле нажатия на кнопку приложение перезагрузится!")
        add_new_direction_tab_layuot.addWidget(warning_messege)

        add_new_direction_tab_widget.setLayout(add_new_direction_tab_layuot)
        directions_list.addTab(add_new_direction_tab_widget, "+")
        main_layout.addWidget(directions_list)

        metasubjects_with_watch_list_name = QLabel('Метапредметные задачи с часами')
        main_layout.addWidget(metasubjects_with_watch_list_name)
        metasubjects_with_watch_list = QTabWidget()

        for metasubject_with_watch in ibData['global_data']['metasubject_with_watch']:
            metasubject_with_watch_widget = QWidget()
            metasubject_with_watch_widget.setObjectName(metasubject_with_watch)

            metasubject_with_watch_layout = QVBoxLayout()

            module_edit_line_name = QLabel('Модуль')
            metasubject_with_watch_layout.addWidget(module_edit_line_name)

            module_edit_line = QLineEdit(
                ibData['global_data']['metasubject_with_watch'][metasubject_with_watch]['module'])
            module_edit_line.setObjectName(f'{metasubject_with_watch}_module')
            module_edit_line.textChanged.connect(self.change_metasubject_with_watch_data)
            metasubject_with_watch_layout.addWidget(module_edit_line)

            duration_edit_line_name = QLabel('Длительность программы в часах')
            metasubject_with_watch_layout.addWidget(duration_edit_line_name)

            duration_edit_line = QLineEdit(
                str(ibData['global_data']['metasubject_with_watch'][metasubject_with_watch]['duration']))
            duration_edit_line.setObjectName(f'{metasubject_with_watch}_duration')
            duration_edit_line.textChanged.connect(self.change_metasubject_with_watch_data)
            metasubject_with_watch_layout.addWidget(duration_edit_line)

            theory_edit_line_name = QLabel('Теория')
            metasubject_with_watch_layout.addWidget(theory_edit_line_name)

            theory_edit_line = QTextEdit(
                ibData['global_data']['metasubject_with_watch'][metasubject_with_watch]['theory'])
            theory_edit_line.setObjectName(f'{metasubject_with_watch}_theory')
            theory_edit_line.textChanged.connect(self.change_metasubject_with_watch_data)
            metasubject_with_watch_layout.addWidget(theory_edit_line)

            practice_edit_line_name = QLabel('Практика')
            metasubject_with_watch_layout.addWidget(practice_edit_line_name)

            practice_edit_line = QTextEdit(
                ibData['global_data']['metasubject_with_watch'][metasubject_with_watch]['practice'])
            practice_edit_line.setObjectName(f'{metasubject_with_watch}_practice')
            practice_edit_line.textChanged.connect(self.change_metasubject_with_watch_data)
            metasubject_with_watch_layout.addWidget(practice_edit_line)

            result_edit_line_name = QLabel('Результат')
            metasubject_with_watch_layout.addWidget(result_edit_line_name)

            result_edit_line = QTextEdit(
                ibData['global_data']['metasubject_with_watch'][metasubject_with_watch]['result'])
            result_edit_line.setObjectName(f'{metasubject_with_watch}_result')
            result_edit_line.textChanged.connect(self.change_metasubject_with_watch_data)
            metasubject_with_watch_layout.addWidget(result_edit_line)

            delete_subject_task_button = QPushButton(f'Удалить метапредметную задачу {metasubject_with_watch}')
            delete_subject_task_button.setObjectName(f'{metasubject_with_watch}')
            delete_subject_task_button.clicked.connect(self.delete_metasubject_with_watch)
            metasubject_with_watch_layout.addWidget(delete_subject_task_button)

            metasubject_with_watch_widget.setLayout(metasubject_with_watch_layout)

            metasubjects_with_watch_list.addTab(metasubject_with_watch_widget, metasubject_with_watch)

        add_metasubject_with_watch_layout = QVBoxLayout()
        add_metasubject_with_watch_widget = QWidget()

        add_metasubject_with_watch_line_text = QLineEdit()
        add_metasubject_with_watch_line_text.textChanged.connect(self.name_new_metasubject_with_watch_changed)
        add_metasubject_with_watch_layout.addWidget(add_metasubject_with_watch_line_text)
        add_metasubject_with_watch_button_text = QPushButton('Добавить метапредметную задачу')
        add_metasubject_with_watch_button_text.clicked.connect(self.add_metasubject_with_watch_event)
        add_metasubject_with_watch_layout.addWidget(add_metasubject_with_watch_button_text)

        warning_messege = QLabel(
            "Введите название новой предметной задачи.\nПосле нажатия на кнопку приложение перезагрузится!")

        add_metasubject_with_watch_layout.addWidget(warning_messege)

        add_metasubject_with_watch_widget.setLayout(add_metasubject_with_watch_layout)

        metasubjects_with_watch_list.addTab(add_metasubject_with_watch_widget, "+")

        main_layout.addWidget(metasubjects_with_watch_list)

        metasubjects_list_name = QLabel('Метапредметные задачи без часов')
        main_layout.addWidget(metasubjects_list_name)
        metasubjects_list = QTabWidget()

        for metasubject in ibData['global_data']['metasubject']:
            metasubject_widget = QWidget()
            metasubject_widget.setObjectName(metasubject)

            metasubject_layout = QVBoxLayout()

            module_edit_line_name = QLabel('Модуль')
            metasubject_layout.addWidget(module_edit_line_name)

            module_edit_line = QLineEdit(
                ibData['global_data']['metasubject'][metasubject]['module'])
            module_edit_line.setObjectName(f'{metasubject}_module')
            module_edit_line.textChanged.connect(self.change_metasubject_data)
            metasubject_layout.addWidget(module_edit_line)

            duration_edit_line_name = QLabel('Длительность программы в часах')
            metasubject_layout.addWidget(duration_edit_line_name)

            duration_edit_line = QLineEdit(
                str(ibData['global_data']['metasubject'][metasubject]['duration']))
            duration_edit_line.setObjectName(f'{metasubject}_duration')
            duration_edit_line.textChanged.connect(self.change_metasubject_data)
            metasubject_layout.addWidget(duration_edit_line)

            theory_edit_line_name = QLabel('Теория')
            metasubject_layout.addWidget(theory_edit_line_name)

            theory_edit_line = QTextEdit(
                ibData['global_data']['metasubject'][metasubject]['theory'])
            theory_edit_line.setObjectName(f'{metasubject}_theory')
            theory_edit_line.textChanged.connect(self.change_metasubject_data)
            metasubject_layout.addWidget(theory_edit_line)

            practice_edit_line_name = QLabel('Практика')
            metasubject_layout.addWidget(practice_edit_line_name)

            practice_edit_line = QTextEdit(
                ibData['global_data']['metasubject'][metasubject]['practice'])
            practice_edit_line.setObjectName(f'{metasubject}_practice')
            practice_edit_line.textChanged.connect(self.change_metasubject_data)
            metasubject_layout.addWidget(practice_edit_line)

            result_edit_line_name = QLabel('Результат')
            metasubject_layout.addWidget(result_edit_line_name)

            result_edit_line = QTextEdit(
                ibData['global_data']['metasubject'][metasubject]['result'])
            result_edit_line.setObjectName(f'{metasubject}_result')
            result_edit_line.textChanged.connect(self.change_metasubject_data)
            metasubject_layout.addWidget(result_edit_line)

            delete_metasubject_button = QPushButton(f'Удалить метапредметную задачу {metasubject}')
            delete_metasubject_button.setObjectName(f'{metasubject}')
            delete_metasubject_button.clicked.connect(self.delete_metasubject)
            metasubject_layout.addWidget(delete_metasubject_button)

            metasubject_widget.setLayout(metasubject_layout)

            metasubjects_list.addTab(metasubject_widget, metasubject)

        add_metasubject_layout = QVBoxLayout()
        add_metasubject_widget = QWidget()

        add_metasubject_line_text = QLineEdit()
        add_metasubject_line_text.textChanged.connect(self.name_new_metasubject_changed)
        add_metasubject_layout.addWidget(add_metasubject_line_text)
        add_metasubject_button_text = QPushButton('Добавить предметную задачу')
        add_metasubject_button_text.clicked.connect(self.add_metasubject_event)
        add_metasubject_layout.addWidget(add_metasubject_button_text)

        warning_messege = QLabel(
            "Введите название новой предметной задачи.\nПосле нажатия на кнопку приложение перезагрузится!")

        add_metasubject_layout.addWidget(warning_messege)

        add_metasubject_widget.setLayout(add_metasubject_layout)

        metasubjects_list.addTab(add_metasubject_widget, "+")

        main_layout.addWidget(metasubjects_list)

        provision_button = QPushButton('Редактировать список общего оборудования')
        provision_button.setObjectName('global')
        provision_button.clicked.connect(self.open_provision_window)
        main_layout.addWidget(provision_button)

        req_button = QPushButton('Отправить на сервер')
        req_button.clicked.connect(self.server_request)
        main_layout.addWidget(req_button)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        scroll = QScrollArea()
        scroll.setWidget(main_widget)

        self.setCentralWidget(scroll)

    def server_request(self):
        requests.post(f'{appData["server_url"]}admin/load_new_data', json=ibData)
        dialog = QMessageBox(parent=self, text="новая версия уже на сервере")
        dialog.setWindowTitle("Message Dialog")
        ret = dialog.exec()

    def open_person_tasks(self):
        sender = self.sender()
        if self.person_data_ is None:
            self.person_data_ = Persontasksview(sender.objectName())
        self.person_data_.show()

    def open_provision_window(self):
        sender = self.sender()
        if self.list_p is None:
            self.list_p = Listview(sender.objectName())
        self.list_p.show()

    def change_metasubject_data(self):
        global ibData
        sender = self.sender()
        changed_element_name = sender.objectName().split('_')
        if changed_element_name[-1] in ["theory", "practice", "result"]:
            changed_element_data = sender.toPlainText()
        else:
            changed_element_data = sender.text()
        if changed_element_name[-1] == 'duration':
            changed_element_data = int(changed_element_data)
        ibData['global_data']['metasubject'][changed_element_name[0]][changed_element_name[1]] = changed_element_data

    def name_new_metasubject_changed(self):
        sender = self.sender()
        self.new_metasubject = sender.text()

    def add_metasubject_event(self):
        ibData['global_data']['metasubject'][self.new_metasubject] = {
            "duration": 0,
            "module": "",
            "theory": "",
            "practice": "",
            "result": ""
        }
        self.load_ui()

    def delete_metasubject(self):
        sender = self.sender()
        ibData['global_data']['metasubject'].pop(sender.objectName())
        self.load_ui()

    def name_new_metasubject_with_watch_changed(self):
        sender = self.sender()
        self.new_metasubject_with_watch = sender.text()

    def add_metasubject_with_watch_event(self):
        ibData['global_data']['metasubject_with_watch'][self.new_metasubject_with_watch] = {
            "duration": 0,
            "module": "",
            "theory": "",
            "practice": "",
            "result": ""
        }
        self.load_ui()

    def delete_metasubject_with_watch(self):
        sender = self.sender()
        ibData['global_data']['metasubject_with_watch'].pop(sender.objectName())
        self.load_ui()

    def change_metasubject_with_watch_data(self):
        global ibData
        sender = self.sender()
        changed_element_name = sender.objectName().split('_')
        if changed_element_name[-1] in ["theory", "practice", "result"]:
            changed_element_data = sender.toPlainText()
        else:
            changed_element_data = sender.text()
        if changed_element_name[-1] == 'duration':
            changed_element_data = int(changed_element_data)
        ibData['global_data']['metasubject_with_watch'][changed_element_name[0]][changed_element_name[1]] = changed_element_data

    def delete_subject_task(self):
        sender = self.sender()
        path = sender.objectName().split('_')
        ibData['local_data'][path[0]]['local'][path[1]]['subject_tasks'].pop(path[2])
        self.load_ui()

    def delete_type_activity(self):
        sender = self.sender()
        path = sender.objectName().split('_')
        ibData['local_data'][path[0]]['local'].pop(path[1])
        self.load_ui()

    def delete_direction(self):
        sender = self.sender()
        ibData['local_data'].pop(sender.objectName())
        self.load_ui()

    def name_new_direction_changed(self):
        sender = self.sender()
        self.new_direction_name = sender.text()

    def add_direction_task_event(self):
        ibData['local_data'][self.new_direction_name] = {
            'local': {},
            'global': {
                "equipment": [],
                "person_tasks": {}
            }
        }
        self.load_ui()

    def name_new_type_activity_changed(self):
        sender = self.sender()
        self.new_type_activity_name = sender.text()

    def add_type_activity_task_event(self):
        sender = self.sender()
        ibData['local_data'][sender.objectName()]['local'][self.new_type_activity_name] = {
            'subject_tasks': {},
            "equipment": [],
            "person_tasks": {}
        }
        self.load_ui()

    def add_new_subject_task_event(self):
        sender = self.sender()
        path = sender.objectName().split('_')
        ibData['local_data'][path[0]]['local'][path[1]]['subject_tasks'][self.new_subject_task_name] = {
            "duration": 18,
            "module": "",
            "theory": "",
            "practice": "",
            "result": ""
        }
        self.load_ui()

    def name_new_subject_task_changed(self):
        sender = self.sender()
        self.new_subject_task_name = sender.text()

    def change_subject_task_data(self):
        global ibData
        sender = self.sender()
        changed_element_name = sender.objectName().split('_')
        if changed_element_name[-1] in ["theory", "practice", "result"]:
            changed_element_data = sender.toPlainText()
        else:
            changed_element_data = sender.text()
        if changed_element_name[-1] == 'duration':
            changed_element_data = int(changed_element_data)
        ibData['local_data'][changed_element_name[0]]['local'][changed_element_name[1]]['subject_tasks'][changed_element_name[2]][changed_element_name[3]] = changed_element_data


def load_config():
    global appData
    with open('appConfig.json') as config:
        appData = json.load(config)


def update_or_load_Data():
    global appData, ibData
    ibData = requests.get(f'{appData["server_url"]}get_ib_back').json()


def first_start():
    load_config()
    update_or_load_Data()
    return True


def start():
    if first_start():
        app = QApplication(sys.argv)
        w = MainWindow()
        w.show()
        app.exec()


if __name__ == "__main__":
    start()
