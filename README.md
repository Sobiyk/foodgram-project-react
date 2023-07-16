# Foodgram ![CI](https://github.com/Sobiyk/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание

Данный проект включает в себя онлайн сервис Foodgram и API для него. На этом
сервисе пользователи могут публиковать рецепты, подписываться на публикации
других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов, необходимых для
приготовления одного или нескольких выбранных блюд.

### Проект доступен по этой [ссылке](http://sobiy.ddns.net)

### В проекте используются:
* ##### Django v. 3.2
* ##### Django Rest Framework v. 3.12.4
* ##### Simple JWT v. 5.2.2
* ##### docker v. 23.0.4
* ##### docker-compose v. 1.29.2
* ##### python-dotenv v. 1.0.0
* ##### nginx
* ##### gunicorn v.20.0.4

## Шаблон наполнения .env файла:
```
SECRET_KEY=django secret key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=имя базы данных
POSTGRES_USER=логин для подключенияк базе данных
POSTGRES_PASSWORD=пароль для подключения к БД
DB_HOST=название сервисса (контейнера)
DB_PORT=прот для подключения к БД
```

### Команды для запуска проекта:
  * Клонируйте репозиторий с помощью SSH
  ```
  git clone git@github.com:Xewus/foodgram-project-react.git
  ```

  * Подключитесь к своему серверу
  ```
  ssh <user>@<server IP>
  ```
  * Установите Docker и Docker compose и предоставьте им права доступа
  ```
  sudo apt install docker.io
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  ```
  * Создайте проектную директорию
  ```
  mkdir foodgram-project
  cd foodgram-project/
  ```
  * В ней создайте .env файл и заполните его по шаблону
  ```
  touch .env
  ```
  * Скопируйте папку infra на удаленный сервер
  ```
  scp -r infra/ <server user>@<server IP>:/home/<server user>/foodgram-project/ 
  ```
  * Запустите docker-compose
  ```
  sudo docker-compose up -d
  ```
  * Выполните миграции. создайте суперюзера для админ-панели и соберите статику
  ```
  sudo docker exec -it infra_web python manage.py migrate
  sudo docker exec -it infra_web python manage.py createsuperuser
  sudo docker exec -it infra_web python manage.py collectstatic --no-input
  ```
### Команда для заполнения базы данных ингредиентами:
  ```
  sudo docker exec -it infra_db_1 COPY app_ingredient(name, measurement_unit) FROM '/var/lib/potgresql/data/ingredients.csv' DELIMITER ',' CSV HEADER;
  ```

##### Над проектом работал:
* [Собковский Кирилл](https://github.com/Sobiyk)