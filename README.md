# Organizational Structure API

API для управления иерархической структурой подразделений и сотрудников.

## Технологии

- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции
- **Docker** - контейнеризация
- **Pytest** - тестирование

## Требования

- Docker Desktop
- Docker Compose

## Быстрый запуск

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd org-structure-api

# Запустить проект
docker-compose up --build
После запуска API будет доступно:

API: http://localhost:8000

Документация Swagger: http://localhost:8000/docs

API Endpoints
Метод	Эндпоинт	Описание
POST	/departments/	Создать подразделение
POST	/departments/{id}/employees/	Создать сотрудника
GET	/departments/{id}	Получить подразделение с деревом
PATCH	/departments/{id}	Обновить/переместить подразделение
DELETE	/departments/{id}	Удалить подразделение
Параметры
GET /departments/{id}

depth - глубина вложенных подразделений (1-5, по умолчанию 1)

include_employees - включить сотрудников в ответ (true/false)

DELETE /departments/{id}

mode - режим удаления (cascade или reassign)

reassign_to_department_id - ID подразделения для переназначения (обязателен при mode=reassign)

Примеры запросов
Создание подразделения
bash
curl -X POST http://localhost:8000/departments/ \
  -H "Content-Type: application/json" \
  -d '{"name":"IT Department","parent_id":null}'
Создание сотрудника
bash
curl -X POST http://localhost:8000/departments/1/employees/ \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Иван Петров","position":"Senior Developer","hired_at":"2024-01-15"}'
Получение дерева подразделений
bash
curl "http://localhost:8000/departments/1?depth=2&include_employees=true"
Перемещение подразделения
bash
curl -X PATCH http://localhost:8000/departments/2 \
  -H "Content-Type: application/json" \
  -d '{"parent_id":1}'
Удаление подразделения
bash
# Каскадное удаление
curl -X DELETE "http://localhost:8000/departments/2?mode=cascade"

# Удаление с переназначением сотрудников
curl -X DELETE "http://localhost:8000/departments/2?mode=reassign&reassign_to_department_id=1"
Бизнес-логика и ограничения
Название подразделения: длина 1-200 символов, уникально в пределах одного родителя

Полное имя сотрудника: длина 1-200 символов

Должность: длина 1-200 символов

Нельзя создать подразделение-родитель самого себя

Нельзя создать цикл в дереве (возвращается 409 Conflict)

При удалении в режиме cascade удаляется всё поддерево

При удалении в режиме reassign сотрудники переназначаются в другое подразделение

Запуск тестов
bash
docker-compose exec app pytest -v
Миграции базы данных
bash
# Создать миграцию
docker-compose exec app alembic revision --autogenerate -m "migration_name"

# Применить миграции
docker-compose exec app alembic upgrade head
Структура проекта
text
app/
├── api/              # Роутеры API
├── core/             # Конфигурация и БД
├── models/           # SQLAlchemy модели
├── schemas/          # Pydantic схемы
├── services/         # Бизнес-логика
├── utils/            # Вспомогательные функции
└── tests/            # Pytest тесты
Остановка проекта
bash
docker-compose down