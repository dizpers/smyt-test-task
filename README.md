Test task for SMYT company
==========================

Description
-----------

Create Web-application, based on Django, by following these requirements:

1) Application should be able to create Django models on-the-fly (in memory) from text model description (in, for example, XML or YAML file); char, int and date types should be supported.

2) Tables in the DB should be created with use of standard Django tools (syncdb); for bringing changes South should be used (if models were created right, then syncdb and south should understand them well);

3) Those tables should be editable through Django admin;

4) Main page of the application should allow to view and edit data, for example:

![logo]

[logo]: http://habrastorage.org/storage2/b00/1c7/cfb/b001c7cfbd1cb0b38ad5633d5a781612.png "Пример"

After click on the cell with data, cell should become editable cell depending on data type (for type "data" we should get date picket widget), and after input and validation should be sent to the server. You should be able to add new row. Language - JavaScript.

5) All created models and queries should be covered with tests.

On the left - list of tables, on the right - data. After table choose, right block should load (via AJAX) structure and data from the table. Main requirement - no html blocks get of those data.

Result of solved task is source code on github + url of deployed application.

Description example (yaml):


    users:
        title: Users
        fields:
            - {id: name, title: Name, type: char}     
            - {id: paycheck, title: Compensation, type: int}
            - {id: date_joined, title: Date of start, type: date}
    
        
    rooms:
        title: Rooms
        fields:
            - {id: department, title: Department, type: char}     
            - {id: spots, title: Capacity, type: int}

Documentation (not the part of the task)
----------------------------------------

Deploy documentation is located in the `docs` directory.

Тестовое задание для SMYT (on Russian)
======================================

Описание
--------

Написать Web-приложение на Django со следующей функциональностью:

1) Приложение должно уметь динамически создавать классы моделей в памяти, используя текстовое описание моделей (например, из xml (или yaml) файла), должны поддерживаться типы char, int, date.

2) Таблицы в бд надо создать стандартными средствами django (syncdb), для изменения необходимо использовать south (в консоли, если модели правильно созданы, то syncdb и south их подхватывают);

3) Для этих таблиц должно быть доступно редактирование в админке django;

4) Главная страница приложения, для просмотра и редактирования введенных.
данных. пример:

![logo]

[logo]: http://habrastorage.org/storage2/b00/1c7/cfb/b001c7cfbd1cb0b38ad5633d5a781612.png "Пример"

При щелчке на ячейку данных, поле должно заменяться полем редактирования в зависимости от типа данных (для типа “дата” должен показываться виджет выбора даты), и после ввода и валидации отправляться на сервер. Должна быть возможность добавления новой строки. Язык - JavaScript.

5) Надо написать тесты для создаваемых моделей и запросов.

Слева - список таблиц, справа - данные. При выборе таблицы, в правый блок аяксом загружаются структура и  данные таблицы. Главное требование - никаких html блоков при получении этих данных.

Результатом выполнения задания считаются исходные коды на github + url развёрнутого из них приложения.

Пример описания (yaml):


    users:
        title: Пользователи
        fields:
            - {id: name, title: Имя, type: char}     
            - {id: paycheck, title: Зарплата, type: int}
            - {id: date_joined, title: Дата поступления на работу, type: date}
    
        
    rooms:
        title: Комнаты
        fields:
            - {id: department, title: Отдел, type: char}     
            - {id: spots, title: Вместимость, type: int}

Документация
------------

Документация по deploy находится в директории `docs`.
