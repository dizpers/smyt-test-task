Deploy
======

.. contents:: Содержание
    :depth: 3

Требования
----------

Для запуска web-приложения необходима ОС семейства Linux с установленными:

* MySQL
* python 2.7.x
* git
* python-dev
* nginx
* nodejs
* npm
* bower

Глобально должны быть установлены следующие модули Python:

* virtualenv
* pip

Развертывание
-------------

Получение файлов проекта и создание виртуальной среды окружения
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Получаем файлы проекта из ``master`` ветки git-репозитория:

::

    git clone git@github.com:dizpers/smyt-test-task.git

Переходим в папку с проектом:

::

    cd smyt-test-task

Создаем виртуальную среду окружения:

::

    virtualenv .env

Активируем созданное окружение

::

    source .env/bin/activate

Устанавливаем необходимые пакеты Python:

::

    pip install -U -r requirements.txt
    pip install -U -r requirements-dev.txt

Настройка базы данных
^^^^^^^^^^^^^^^^^^^^^
Указываем необходимые настройки MySQL в `my.cnf`:

::

    [mysqld]
    character-set-server = utf8
    collation-server = utf8_unicode_ci
    init-connect='SET NAMES utf8'

Создаем базу данных:

::

   mysql -h localhost -P 3306  -uroot -p -e 'create database smyt default character set utf8 collate utf8_general_ci';

Создаём пользователя MySQL, которому выдаём нужные привилегии:

::

   mysql -h localhost -P 3306 -uroot -p -e "GRANT ALL PRIVILEGES ON \`smyt%\`.* TO 'smyt_user'@'localhost' IDENTIFIED BY 'smyt_password';"

Создаем файл локальных настроек `smyt/settings/local.py` путем копирования шаблона:

::

    cp smyt/settings/local.py.template smyt/settings/local.py

Редактируем файл настроек `smyt/settings/local.py` так, чтобы он содержал настройки
баз данных в соответствии с принятыми для django `конвенциями <https://docs.djangoproject.com/en/dev/ref/settings/#databases>`_
(имя обычной и тестовой БД изменять нельзя) и случайное значение SECRET_KEY:

::

   vim smyt/settings/local.py

Далее, выполняем следующие команды:
::

    python manage.py syncdb --noinput
    python manage.py migrate

Инициализация объектов
^^^^^^^^^^^^^^^^^^^^^^

Иниализируем статику:

::

    python manage.py bower_install -F
    python manage.py collectstatic

Создаём суперпользователя:

::

   python manage.py createsuperuser

Запускаем тесты:

::

    python manage.py test --settings=smyt.settings.test

Управление приложением
----------------------

Для запуска приложения необходимо, находясь в папке с проектом, выполнить следующую команду:

::

   DJANGO_SETTINGS_MODULE=smyt.settings.local gunicorn -n smyt -c common/configs/gunicorn.py -D -p spool/pids/smyt.pid smyt.wsgi

Для остановки приложения необходимо, находясь в папке с проектом, выполнить следующую команду:

::

    bash kill.sh

Конфиг Nginx
------------

::

    upstream smyt_app_server {
        server 127.0.0.1:8000 fail_timeout=0;
    }

    server {
        listen 80 default;
        server_name smyt.ru;

        access_log $PROJECT_ROOT/spool/logs/nginx-access.log;
        error_log $PROJECT_ROOT/spool/logs/nginx-error.log;

        location /static/ {
              alias $PROJECT_ROOT/spool/static/;
        }

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass http://smyt_app_server;
        }

    }
