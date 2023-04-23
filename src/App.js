import React, { useState } from 'react';
import { components } from "react-select";
import Creatable from "react-select/creatable";
import Select from 'react-select';
import axios from "axios";
import './App.css';

var requestLoaded = true;

const SelectLineType1 = (props) => {
  return (
    <components.Menu {...props}>
      {props.getValue().length || 0 <= 2 ? (props.children) : (<div style={{ margin: 15 }}>Max limit achieved</div>)}
    </components.Menu>
  );
};

const GetMetodicLink = () =>{
  return <form action='http://khv2022.pythonanywhere.com/constructor/get_mrt' method='POST'><button type='submit'>!!!Скачать файл с методическими рекомендациями!!!</button></form>
}

function App (){
  let timeLimit = 0;
  let selectedTasksCount = 0;

  const [iDBFrontend, setIDBFrontend] = useState(null)
  const [requestStatus, setRequestStatus] = useState(0);

  const [directionsList, setDirectionsList] = useState([]);

  const [directionSelected, setDirectionSelected] = useState('');
  const [activitySelected, setActivitySelected] = useState('');
  const [subjectsTasksSelected, setSubjectsTasksSelected] = useState('');

  const [training_period, setTraining_period] = useState('0');
  const [programTImeLimitParam1, setProgramTImeLimitParam1] = useState('');
  const [programTImeLimitParam2, setProgramTImeLimitParam2] = useState('');
  const [programTImeLimitParam3, setProgramTImeLimitParam3] = useState('');

  function getIDB(){
    axios({
      method: "GET",
      url:"/get_ib_front",
    })
    .then((response) => {
      setRequestStatus(1);
      const res = response.data;
      setIDBFrontend(({localData: res.local_data,globalData: res.global_data}));
      setDirectionsList(Object.keys(iDBFrontend.localData));
      directionsList.push('')
      requestLoaded = false
    }).catch((error) => {
      if (error.response) {
        setRequestStatus(2);
        console.log(error.response);
        console.log(error.response.status);
        console.log(error.response.headers);
        }
    })
  }

  function getActivityList(){
    if (directionSelected === ''){
      return <select type="text" name="en_type_activity" value={activitySelected} onChange={(event) => setActivitySelected(event.target.value)}>
        <option value=""></option>
        </select>
    }
    else {
      return <select type="text" name="en_type_activity" value={activitySelected} onChange={(event) => setActivitySelected(event.target.value)}>
        <option value=""></option>
        {Object.keys(iDBFrontend.localData[directionSelected]['subjects']).map((activity) => <option value={activity}>{activity}</option>)}
      </select>
    }
  }

  function reloadTimeLimit(){
    if (training_period === "36"){
      if (programTImeLimitParam3 === '1') makeTimeLimit(training_period, 1, 2)
      else if (programTImeLimitParam3 === '2') makeTimeLimit(training_period, 2, 1)
      else if (programTImeLimitParam3 === '3') makeTimeLimit(training_period, 1, 1)
      else makeTimeLimit(training_period, 0, 0)
    }
    else makeTimeLimit(training_period, programTImeLimitParam1, programTImeLimitParam2)
  }

  function makeTimeLimit(param1, param2, param3){
    timeLimit = (Number(param1) * Number(param2) * Number(param3));
  }

  function getTrainingPlan(){
    if (training_period === "36")
      return <div onClick={reloadTimeLimit()}>
        <p>Выберите план </p>
        <select type="text" name="en_duration_lesson_choice" value={programTImeLimitParam3} onChange={(event)=>{setProgramTImeLimitParam3(event.target.value)}}>
          <option value="0"></option>
          <option value="1">продолжительность занятия - 1 час; 2 занятия в неделю</option>
          <option value="2">продолжительность занятия - 2 час; 1 занятие в неделю</option>
          <option value="3">продолжительность занятия - 1 час; 1 занятие в неделю</option>
        </select><br/>
        </div>
    else if (training_period === "18") return <div onClick={reloadTimeLimit()}><p>Продолжительность  занятия  в академических  часах </p>
    <select type="text" name="en_duration_lesson" value={programTImeLimitParam1} onChange={(event)=>{setProgramTImeLimitParam1(event.target.value)}}>
      <option value="0">0</option>
      <option value="1">1</option>
      <option value="2">2</option>
    </select><br/>
    <p>Кол-во занятий в неделю </p>
    <select type="text" name="en_number_classes" value={programTImeLimitParam2} onChange={(event)=>{setProgramTImeLimitParam2(event.target.value)}}>
      <option value="0">0</option>
      <option value="1">1</option>
      <option value="2">2</option>
    </select><br/>
    </div>
    else return <div></div>
  }

  function getLimitAlert(){
    selectedTasksCount = subjectsTasksSelected.length
    if ((selectedTasksCount > timeLimit / 18 - 1)&& selectedTasksCount !== 0) {
      return <label className='alertMessege'>!часы за метапредметные задачи учитываться не будут!</label>
    }
    return <div></div>
  }

  function getPersonalTasksList(){
    var personalTasksList = iDBFrontend.localData[directionSelected]['person']
    personalTasksList.push.apply(personalTasksList, iDBFrontend.localData[directionSelected]['subjects'][activitySelected]['person']);
    return personalTasksList
  }

  function getTasksSelectPart(){
    if (activitySelected !== ''){
      return <div>
          <p>Период обучения в неделях</p>
          <select type="text" name="en_training_periodn" value={training_period} onChange={(event)=>{setTraining_period(event.target.value)}}>
            <option value="0">0</option>
            <option value="18">18</option>
            <option value="36">36</option>
          </select>
          {getTrainingPlan()}
          <p>программа расчитана на { timeLimit } часа(ов)</p>
          <p>Форма обучения</p>
          <Select
            components={{ SelectLineType1 }}
            name='en_form_edu'
            isMulti
            options={[
              {
                label: "очная",
                value: "очная"
              },
              {
                label: "дистанционная",
                value: "дистанционная"
              },
              {
                label: "заочная",
                value: "заочная"
              }
            ]}/>
          <p>Задачи предметные (каждая задача выдаёт содержательный модуль, расчитанный на 18 часов)</p>
          <Select
            value={subjectsTasksSelected}
            components={{ Menu }}
            name='en_subject_taskss'
            isMulti
            options={iDBFrontend.localData[directionSelected]['subjects'][activitySelected]['subject'].map((item) => ({"label": item, 'value':item}))}
            onChange={setSubjectsTasksSelected}
          />
          {getLimitAlert()}
          <p>Задачи метапредметные (с часами)</p>
          <Select
            name='en_metasubject_tasks'
            isMulti
            options={iDBFrontend.globalData['metasubject_with_watch'].map((item) => ({"label": item, 'value':item}))}
          />
          <p>Задачи метапредметные (без часов)</p>
          <Select
            name='en_metasubject_tasks_no'
            isMulti
            options={iDBFrontend.globalData['metasubject'].map((item) => ({"label": item, 'value':item}))}
          />
          <p>Задачи личностные</p>
          <Select
            name='en_personal_tasks'
            isMulti
            options={getPersonalTasksList().map((item) => ({"label": item, 'value':item}))}
          />
      </div> 
    }
    else return <div></div>
  }

  function getEquipmentList(){
    var globalEquipmentList = iDBFrontend.localData[directionSelected]['subjects'][activitySelected]['equipment'];
    globalEquipmentList.push.apply(globalEquipmentList, iDBFrontend.localData[directionSelected]['equipment']);
    return globalEquipmentList
  }

  function getInventoryChoise(){
    if (activitySelected !== ''){
      return <div>
        <p>Общее оборудование</p>
        <Creatable
            name='cop_material_support_1'
            isMulti
            options={iDBFrontend.globalData['provision'].map((item) => ({"label": item, 'value':item}))}
          />
        <p>Специальное оборудование</p>
        <Creatable
            name='cop_material_support_2'
            isMulti
            options={getEquipmentList().map((item) => ({"label": item, 'value':item}))}
          />
      </div> 
    }
  }

  function getOutButton(){
    if (activitySelected !== ''){
      return <div className = "button"><input type="submit" id="hidden-button"/></div>
    }
  }

  const Menu = (props) => {
    return (
      <components.Menu {...props}>
        { selectedTasksCount < timeLimit / 18 ? (props.children) : (<div style={{ margin: 15 }}>Max limit achieved</div>)}
      </components.Menu>
    );
  };

  function getForm(){
    if (requestLoaded) getIDB();
    if (requestStatus === 0) {return <div>Идёт загрузка...</div>}
    else if (requestStatus === 2){return <div>Проблема с сетью или сервером</div>}
    else if (requestStatus === 1) {
      // return <form action="http://khv2022.pythonanywhere.com/constructor/test" method = "POST">
      return <form action="http://127.0.0.1:5000/constructor/test" method = "POST">
        <div className="forms">
          <h2>Титульный лист</h2>
          <p>Учредитель образовательной организации</p>
          <input type="text" name="tp_founder_eo"/>
          <p>Полное название образовательной организации (по уставу)</p>
          <input type="text" name="tp_fullname_eo"/>
          <p>Сокращенное название образовательной организации (по уставу)</p>
          <input type="text" name="tp_shortname_eo"/>
          <p>Рассмотрено на </p>
          <select type="text" name="tp_expert_advisory_org">
            <option value="НМС">НМС (Научно-методический совет)</option>
            <option value="ПС">ПС (педагогический совет)</option>
          </select>
          <p>№ протокола</p>
          <input type="text" name="tp_protocol_number"/>
          <p>Дата заседания НМС, ПС</p>
          <input type="date" name="tp_meeting_date_smc"/>
          <p>Дата утверждения программы руководителем</p>
          <h5>(в соответствии с приказом образовательной организации реализующей программу)</h5>
          <input type="date" name="tp_date_approval_program"/>
          <p>Фамилия, иннициалы руководителя образовательной организации</p>
          <input type="text" name="tp_surname_head_eo"/>
          <p>Должность руководителя образовательной организации</p>
          <input type="text" name="tp_eo_lvl"/>
          <p>Дополнительная общеобразовательная общеразвивающая программа (укажите название)</p>
          <input type="text" name="tp_program_name"/>
          <p>Программа имеет направленность </p>
          <select type="text" name="en_orientation" value={directionSelected} onChange={(event) => setDirectionSelected(event.target.value)}>
            <option value=""></option>
            {directionsList.map((direction) => <option value={direction}>{direction}</option>)}
          </select>
          <p>Адресат программы (возраст в границах  от 6 до 18 лет)</p>
          <input type="text" name="tp_addressee_program"/>
          <p>Дополнительные требования к обучающемуся (необязательно к заполнению)</p>
          <textarea name="tp_addressee_lvl"/>
          <p>Место реализации программы (город, поселок)</p>
          <input type="text" name="tp_implementation_place"/>
          <p>Год утверждения программы</p>
          <h5>(программы утверждаются ежегодно перед началом реализации)</h5>
          <select type="text" name="tp_approval_year">
            <option value="2022">2022</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
            <option value="2026">2026</option>
            <option value="2027">2027</option>
            <option value="2028">2028</option>
            <option value="2029">2029</option>
            <option value="2029">2030</option>
          </select>
          <p>Фамилия, иннициалы, должность составителя программы</p>
          <h5>Например, Иванов С.И., педагог дополнительного образования</h5>
          <input type="text" name="tp_surname_originator"/>
          <h2>Пояснительная записка</h2>
          <p>Вид деятельности </p>
            {getActivityList()}
          <div>
            <p>Актуальность</p>
            <h5>— это ответ на вопрос, зачем современным детям в современных условиях нужна конкретная программа (своевременность, современность). 
            Актуальность отражает:<br/>
            1. актуальность для общества (как ребёнок с приобретёнными компетенциями будет востребован в современном обществе),<br/>
            2. актуальность для ребёнка (что ребёнок приобретет и как изменится).
            (не более 1000 знаков)
            </h5>
          </div>
          <textarea name="en_relevance"/>
          <p>Цели программы</p>
          <textarea name='en_program_objectives '/>
          <div>
            <p>Новизна</p>
            <h5>
          указать, имеются ли аналогичные программы других авторов, чем от них отличается данная программа. Отличие может быть в том, как расставлены акценты, какие новые педагогические технологии, формы диагностики использованы и т. п. 
          </h5>
          <h4>
            Если новизны нет, не нужно ее выдумывать!
          </h4>
          </div>
          <textarea name="en_new_exp"/>
          {getTasksSelectPart()}
          <div>
            <p>Формы организации занятий</p>
            <h5>пример: групповые, индивидуальные, парные; круглые столы, практические занятия, лабораторные работы, экспериментальные и проектные площадки, открытые занятии, экскурсии и т. п. (не более 500 знаков)</h5>
          </div>
          <textarea name='en_form_education'/>
          <h2>Учебный план</h2>
          <p>Настройка таблицы происходит в документе</p>
          <h2>Комплекс организационно – педагогических условий</h2>
          <h3>Материально-техническое обеспечение</h3>
          {getInventoryChoise()}
          <h3>Информационно-методическое обеспечение</h3>
          <p>Информационные ресурсы</p>
          <textarea name='cop_technical_support_1'/>
          <p>Методическое обеспечение</p>
          <textarea name='cop_technical_support_2'/>
          <div>
            <p>Формы представления результатов</p>
            <h5>(соревнования, сдача нормативов, участие в выставках, конкурсах, фестивалях, презентация проекта, отчетное занятие, отчетный концерт, спектакль и т.п).</h5>
          </div>
          <textarea name='cop_form_visual'/>
          <p>Формы контроля по отдельным разделам программы,  по итогам учебного года,  по итогам освоения программы (если программа более чем на один год).</p>
          <textarea name='cop_form_control'/>
          <div>
            <p>Оценочные материалы</p>
            <h5> это пакет диагностических методик, позволяющих определить достижение учащимися планируемых результатов. Это могут быть: контрольные нормативы, протокол и итоги соревнований, тест, психолого-педагогическая диагностика, диагностическая карта, протокол  конкурса.
            Оценочные материалы должны отслеживать и оценивать только те результаты, которые перечислены в разделе ожидаемые результаты.
            Для каждой программы разрабатываются свои, характерные для нее, параметры, критерии, оценочные материалы и диагностики. Оценочные материалы могут использоваться как готовые, разработанные другими авторами, так и разработанными самостоятельно. При использовании готовых методик обязательно указываются их авторы, даются ссылки на источники информации. Если автор программы самостоятельно разработал диагностические материалы, перечни и описания заданий помещаются в Приложении к программе. 
            </h5>
          </div>
          <textarea name='cop_materials_edu'/>
          <h2>СПИСОК ИСТОЧНИКОВ</h2>
          <p>Литература для детей (*необязательно для заполнения)</p>
          <textarea name='cop_list_sourse_2'/>
          <p>Литература для родителей (*необязательно для заполнения)</p>
          <textarea name='cop_list_sourse_3'/>
          <p>Литература для педагогов</p>
          <textarea name='cop_list_sourse_1'/>
          <label className='alertMessege'>Выдаваемый файл требует проверки и редактирования!</label>
        </div>
        {getOutButton()}
      </form>
    }
  }

  return (
    <div className="App">
      {GetMetodicLink()}
      {getForm()}
      </div>
  );
}

export default App;
