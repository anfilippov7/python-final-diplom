# Дипломная работа к профессии Python-разработчик «API Сервис заказа товаров для розничных сетей».

## Описание использования сервиса

Перед началом использования сервиса необходимо:

- Установить необходимые библиотеки, выполнив команду pip install -r requirements.txt

- Запустить базу данных командой sudo docker-compose up

- Выполнить команды python manage.py makemigrations и python manage.py migrate

- Запустить сервер redis в отдельном терминале командой redis-server

- Запустить приложение Celery командой python -m celery -A orders worker 

- Запустить сервер Django python manage.py runserver

- Проверить корректность работы приложения выполнив запросы из файла requests.http

- Проверить работу приложения Celery на наличие ошибок командой  python -m celery -A orders worker -l info 


## 1.05.2023 Добавлен функционал:

- DRF тротлинг

- добавлена возможность авторизации из VK и yandex


## 21.05.2023 drf-spectacular


для запуска drf-spectacular необходимо выполнить две команды:

- python3 manage.py spectacular --color --file schema.yml
- sudo docker run -p 80:8080 -e SWAGGER_JSON=/schema.yml -v ${PWD}/schema.yml:/schema.yml swaggerapi/swagger-ui
