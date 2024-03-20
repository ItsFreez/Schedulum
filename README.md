# Schedulum

## Описание

**Schedulum** - проект, представляющий из себя сервис расписания для обучающихся ВУЗов. Реализованы 4 модели: 3 модели (Year, Month, Week) реализованы для админ-зоны Django и 1 модель (Schedule) реализована для пользователей. Есть система аутентификации через логин и пароль. Администратор сервиса должен изначально создать необходимые года, месяцы и недели для работы пользователей. Пользователи могут взаимодействовать только с расписанием: создавать, выбирать количество недель повторения, редактировать и удалять. Реализована страница пользователя, на которой отображается расписание на текущий и следующий день. Помимо web-составляющей, также разработан CRUD. Пользователи могут регистрироваться, получать авторизационный токен и работать со своим расписанием через API сервиса.
При возможности можно подключить собственного telegram bot`а к API и получать расписание через него прямо в мессенджер.

## Стек технологий 

![](https://img.shields.io/badge/Python-3.9-black?style=flat&logo=python)
![](https://img.shields.io/badge/Django-3.2-black?style=flat&logo=django)
![](https://img.shields.io/badge/DjangoRestFramework-3.12.4-black?style=flat&logo=djangorestframework) 

## Порядок действий для запуска проекта

***1. Клонировать репозиторий и перейти в папку c проектом***

```shell
git clone https://github.com:ItsFreez/Schedulum.git
```

```shell
cd Schedulum
```

***2. Cоздать и активировать виртуальное окружение***

*Для Windows*
```shell
python -m venv env
source venv/Scripts/Activate
```
*Для MacOS/Linux*
```shell
python3 -m venv env
source env/bin/activate
```

***3. Обновить менеджер pip и установить зависимости из файла requirements.txt***

```shell
python -m pip install --upgrade pip
```

```shell
pip install -r requirements.txt
```

***4. Применить миграции для создания базы данных***

```shell
cd schedulum
```

```shell
python manage.py migrate
```

***5. Запустить проект***
```shell
python manage.py runserver
```

### Автор проекта

[ItsFreez](https://github.com/ItsFreez)
